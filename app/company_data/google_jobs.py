from typing import Dict
from urllib.parse import urlparse

from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from app.shared import Company, SerpApiClient
from app.foundation.primitives import datetime
from app.foundation.server import Logger
from .data_syncer import DataFetcher, FetchResult, DataSyncer


__all__ = ["GoogleJobsDataSyncer", "GoogleJobsFetcher"]


class GoogleJobsDataSyncer(DataSyncer):
    async def store_db_data(self, company: Company, result: FetchResult):
        update_result = await self._companies_collection.update_one(
            {
                '_id': ObjectId(company.id)
            },
            {
                "$set": {
                    "googleJobsUpdatedAt": result.updated_at,
                }
            },
        )
        googleJobsData = result.db_update_fields.get("googleJobsData") or []
        jobs_collection = self._database["jobs"]
        for job in googleJobsData:
            result = await jobs_collection.update_one(
                filter={
                    'companyId': company.id,
                    'title': job.get('title'),
                    'location': job.get('location')
                },
                update={
                    '$set': {
                        'updatedAt': datetime.now(),
                        'applyOptions': job.get('apply_options'),
                        'companyId': company.id,
                        'companyName': job.get('company_name'),
                        'description': job.get('description'),
                        'extensions': job.get('extensions'),
                        'jobHighlights': job.get('job_highlights'),
                        'location': job.get('location'),
                        'title': job.get('title'),
                        'via': job.get('via'),
                    },
                    '$setOnInsert': {
                        'createdAt': datetime.now(),
                    }
                },
                upsert=True,
            )


class GoogleJobsFetcher(DataFetcher):
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
        return "google-jobs"

    def should_update(self, company: Company):
        return company.googleJobsUpdatedAt is None or (
            company.googleJobsUpdatedAt < datetime.now() - datetime.timedelta(days=3)
        )

    async def fetch_company_data(self, company: Company) -> FetchResult:
        website = f"https://{company.website}" if not company.website.startswith('http') else company.website
        domain = urlparse(website).netloc.replace('www.', '') if website else None
        raw_data = await self._serpapi_client.search_google_jobs(domain)
        search_metadata = raw_data.get('search_metadata') or {}
        jobs_results = raw_data.get('jobs_results') or []

        return FetchResult(
            raw_data=raw_data,
            remote_id=None,
            db_update_fields={
                "googleJobsData": jobs_results,
                "googleJobsUpdatedAt": datetime.now()
            } if jobs_results else {},
            updated_at=datetime.now()
        )
