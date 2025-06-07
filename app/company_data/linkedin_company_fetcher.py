from typing import AnyStr as Str, Dict
from functools import cache
from httpx import HTTPError
from pandas.io.formats.format import return_docstring
from pymongo.asynchronous.database import AsyncDatabase

from app.shared import Company, ScrapinClient
from app.foundation.primitives import datetime

from app.foundation.server import Logger
from .data_syncer import DataFetcher


__all__ = ["LinkedInCompanyFetcher"]


class LinkedInCompanyFetcher(DataFetcher):
    def __init__(
            self,
            database: AsyncDatabase,
            scrapin_client: ScrapinClient,
            logger: Logger
    ):
        self._database = database
        self._companies_collection = database["companies"]
        self._scrapin_client = scrapin_client
        self._logger = logger

    def source_id(self) -> Str:
        return "linkedin_company"

    async def remote_id(self, company: Company) -> Str:
        db_update_payload = await self.db_update_payload(company)
        return db_update_payload.get("linkedInId")

    async def raw(self, company: Company) -> Dict:
        return await self._fetch(company._id, company.linkedInId)

    async def db_update_payload(self, company: Company) -> Dict:
        raw_data = await self.raw(company)
        if not raw_data:
            return {}
        return {
            "linkedInData": raw_data,
            "linkedInUpdatedAt": datetime.now(),
            "linkedInId": raw_data.get("linkedInId")
        }

    async def _fetch(self, company_id, linkedin_id) -> Dict:
        linkedin_url = None
        if linkedin_id:
            linkedin_url = f"https://www.linkedin.com/company/{linkedin_id}"
        else:
            linkedin_url = await self._get_linkedin_url_from_db(company_id)
        
        if not linkedin_url:
            return {}
        
        try:
            data = await self._scrapin_client.extract_company_data(linkedin_url)
            return data if data else {}
        except HTTPError as exc:
            self._logger.warning(
                "Fetch company data from scrapin failed",
                labels={
                    "company_id": company_id,
                    "linkedin_id": linkedin_id,
                    "exception": str(exc)
                }
            )
            return {}

    async def _get_linkedin_url_from_db(self, company_id):
        company = await self._companies_collection.find_one({"_id": company_id})
        if not company:
            return ""
        
        spectr_data = company.get("spectrData") or {}
        socials = spectr_data.get("socials") or {}
        linkedin = socials.get("linkedin") or {}
        return linkedin.get("url") or ""
