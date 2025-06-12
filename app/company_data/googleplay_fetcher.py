from typing import Dict
from urllib.parse import urlparse

from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from app.shared import Company, SerpApiClient
from app.foundation.primitives import datetime
from app.foundation.server import Logger
from .data_syncer import DataFetcher, FetchResult


__all__ = ["GooglePlayFetcher"]


class GooglePlayFetcher(DataFetcher):
    def __init__(
            self,
            database: AsyncDatabase,
            serpapi_client: SerpApiClient,
            logger: Logger
    ):
        self._database = database
        self._companies_collection = database["companies"]
        self._serpapi_client = serpapi_client
        self._logger = logger

    def source_id(self) -> str:
        return "googleplay"

    def should_update(self, company: Company):
        # Only check for updates if company has Google Play data or hasn't been checked yet
        return company.googlePlayUpdatedAt is None or (
            company.googlePlayData is not None and 
            company.googlePlayUpdatedAt < datetime.now() - datetime.timedelta(days=7)
        )

    async def fetch_company_data(self, company: Company) -> FetchResult:
        developer_id = await self._get_developer_id_from_db(company.id)
        
        raw_data = {}
        app_highlight = None
        google_play_id = None
        
        if developer_id:
            raw_data = await self._serpapi_client.search_google_play(developer_id)
            if raw_data and 'app_highlight' in raw_data:
                app_highlight = raw_data['app_highlight']
                google_play_id = app_highlight.get('product_id') if app_highlight else None
        else:
            self._logger.info("Company has no Google Play presence", labels={
                "company_id": company.id,
                "company_name": company.name,
            })

        return FetchResult(
            raw_data=raw_data,
            remote_id=google_play_id,
            db_update_fields={
                "googlePlayData": app_highlight,
                "googlePlayId": google_play_id,
                "googlePlayUpdatedAt": datetime.now()
            },
            updated_at=datetime.now()
        )


    async def _get_developer_id_from_db(self, company_id: str) -> str:
        company = await self._companies_collection.find_one({"_id": ObjectId(company_id)})
        if not company:
            return ""
            
        spectr_data = company.get("spectrData") or {}
        socials = spectr_data.get("socials") or {}
        googleplay = socials.get("googleplay") or {}
        urls = googleplay.get("urls") or []
        
        if not urls:
            return ""
            
        # Extract developer ID from Google Play URL
        # Format: https://play.google.com/store/apps/developer?id=DeveloperID
        for url in urls:
            parsed = urlparse(url)
            if 'developer' in parsed.path and parsed.query:
                query_params = dict(param.split('=') for param in parsed.query.split('&') if '=' in param)
                if 'id' in query_params:
                    return query_params['id']
        
        return ""