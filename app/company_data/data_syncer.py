import gzip
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Dict

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
        Source identifier (e.g., 'linkedin_company')
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
        if not self._data_fetcher.should_update(company):
            return

        result = await self._data_fetcher.fetch_company_data(company)
        source_id = self._data_fetcher.source_id()

        bucket_path = '/'.join([
            source_id,
            company.website_id(),
            f"{result.updated_at:%Y-%m-%d}.json.gz"
        ])
        data = json.dumps(result.raw_data)
        compressed_data = gzip.compress(data.encode('utf-8'))
        blob = self._dataset_bucket.blob(bucket_path)

        blob.content_encoding = 'gzip'
        await as_async(
            blob.upload_from_string,
            data=compressed_data,
            content_type='application/json',
        )

        update_result = await self._companies_collection.update_one(
            {
                '_id': company._id
            },
            {
                "$set": result.db_update_fields
            },
        )

        self._logger.info(f"Synced company data", labels={
            "company": company.model_dump(),
            "source": source_id,
            "remote_id": result.remote_id,
            "updated_at": result.updated_at,
            "db_update_result": update_result.raw_result,
        })
