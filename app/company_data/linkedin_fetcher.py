from typing import AnyStr as Str, Dict
from functools import cache

from bson import ObjectId
from httpx import HTTPError
from pymongo.asynchronous.database import AsyncDatabase

from app.shared import Company, ScrapinClient
from app.foundation.primitives import datetime

from app.foundation.server import Logger
from .data_syncer import DataFetcher, FetchResult


__all__ = ["LinkedInFetcher"]


class LinkedInFetcher(DataFetcher):
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

    def source_id(self) -> str:
        return "linkedin"

    def should_update(self, company: Company):
        return company.linkedInUpdatedAt is None or company.linkedInUpdatedAt < datetime.now() - datetime.timedelta(days=1)

    async def fetch_company_data(self, company: Company) -> FetchResult:
        raw_data = await self._fetch_raw_data(company)

        return FetchResult(
            raw_data=raw_data,
            remote_id=raw_data.get("linkedInId") if raw_data else None,
            db_update_fields={
                "linkedInData": raw_data,
                "linkedInUpdatedAt": datetime.now(),
                "linkedInId": raw_data.get("linkedInId")
            } if raw_data else {},
            updated_at=datetime.now()
        )

    async def _fetch_raw_data(self, company: Company) -> Dict:
        linkedin_url = None
        if company.linkedInId:
            linkedin_url = f"https://www.linkedin.com/company/{company.linkedInId}"
        else:
            linkedin_url = await self._linkedin_url_from_db(company.id)

        if not linkedin_url:
            self._logger.error("Company has no linkedInId or linkedInUrl", labels={
                "company": company.model_dump(),
            })
            raise RuntimeError("Company has no linkedInId or linkedInUrl")

        return await self._scrapin_client.extract_company_data(linkedin_url)

    async def _linkedin_url_from_db(self, company_id):
        company = await self._companies_collection.find_one({"_id": ObjectId(company_id)})
        if not company:
            return ""
        linkedInData = company.get("linkedInData") or {}
        linkedInUrl = linkedInData.get("linkedInUrl") or ""
        if linkedInUrl:
            return linkedInUrl
        spectr_data = company.get("spectrData") or {}
        socials = spectr_data.get("socials") or {}
        linkedin = socials.get("linkedin") or {}
        linkedin_url = linkedin.get("url")
        parts = linkedin_url.split("/")
        if len(parts) < 2:
            return None
        return f"https://www.linkedin.com/company/{parts[-1]}"
