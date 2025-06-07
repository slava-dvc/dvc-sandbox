from typing import AnyStr as Str, Dict
from functools import lru_cache

from pymongo.asynchronous.database import AsyncDatabase

from app.shared import Company, ScrapinClient
from .data_syncer import DataFetcher


__all__ = ["LinkedInCompanyFetcher"]


class LinkedInCompanyFetcher(DataFetcher):
    def __init__(
            self,
            database: AsyncDatabase,
            scrapin_client: ScrapinClient
    ):
        self._database = database
        self._companies_collection = database["companies"]

    def source_id(self) -> Str:
        return "linkedin_company"

    async def remote_id(self, company: Company) -> Str:
        pass

    async def raw(self, company: Company) -> Dict:
        pass

    async def db_update_payload(self, company: Company) -> Dict:
        pass

    @lru_cache(maxsize=1024)
    async def _fetch(self, company_id, linkedin_id) -> Dict:
        linkedin_url = None
        if linkedin_id:
            linkedin_url = f"https://www.linkedin.com/company/{linkedin_id}"
        if not linkedin_id:
            linkedin_url = await self._companies_collection.find_one({"_id": company_id})
        if not linkedin_url:
            return {}


    @lru_cache(maxsize=1024)
    async def _get_linkedin_url_from_db(self, company_id):
        company = await self._companies_collection.find_one({"_id": company_id})
        spectrData = company.get("spectrData") or {}
        socials = spectrData.get("socials") or {}
        linkedin = socials.get("linkedin") or {}
        return linkedin.get("url") or ""
