import gzip
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Dict

from bson import ObjectId
from google.cloud import storage
from pymongo.asynchronous.database import AsyncDatabase

from app.foundation import as_async
from app.foundation.primitives import datetime, json
from app.foundation.server import Logger
from app.shared import Company


@dataclass
class FetchResult:
    raw_data: Dict
    remote_id: str
    db_update_fields: Dict
    updated_at: datetime.datetime


class DataFetcher(metaclass=ABCMeta):

    @abstractmethod
    def source_id(self) -> str:
        """
        Source identifier (e.g., 'linkedin', 'googleplay')
        """
        pass

    def should_update(self, company: Company):
        return True

    @abstractmethod
    async def fetch_company_data(self, company: Company) -> FetchResult:
        """
        Fetch raw data and return transformed result
        """
        pass


class DataSyncer:
    def __init__(
            self,
            dataset_bucket: storage.Bucket,
            database: AsyncDatabase,
            data_fetcher: DataFetcher,
            logger: Logger
    ):
        self._dataset_bucket = dataset_bucket
        self._database = database
        self._data_fetcher = data_fetcher
        self._logger = logger
        self._companies_collection = database["companies"]

    async def sync_one(self, company: Company):
        source_id = self._data_fetcher.source_id()
        if not self._data_fetcher.should_update(company):
            self._logger.info(f"Company is up-to-date", labels={
                "company": company.model_dump(),
                "source": source_id,
            })
            return

        result = await self._data_fetcher.fetch_company_data(company)

        # Only store in bucket if there's meaningful data
        if result.raw_data:
            await self.store_raw_data(company, result)

        if result.db_update_fields:
            await self.store_db_data(company, result)

        if result.raw_data or result.db_update_fields:
            self._logger.info(f"Synced company data", labels={
                "company": company.model_dump(),
                "source": source_id,
                "updated_at": result.updated_at,
            })

    async def store_raw_data(self, company: Company, result: FetchResult):
        bucket_path = '/'.join([
            source_id,
            company.website_id(),
            f"{result.updated_at:%Y-%m-%d}.json.gz"
        ])
        result.raw_data['fetchedAt'] = datetime.now()
        data = json.dumps(result.raw_data)
        compressed_data = gzip.compress(data.encode('utf-8'))
        blob = self._dataset_bucket.blob(bucket_path)

        blob.content_encoding = 'gzip'
        await as_async(
            blob.upload_from_string,
            data=compressed_data,
            content_type='application/json',
        )

    async def store_db_data(self, company: Company, result: FetchResult):
        update_result = await self._companies_collection.update_one(
            {
                '_id': ObjectId(company.id)
            },
            {
                "$set": result.db_update_fields
            },
        )
