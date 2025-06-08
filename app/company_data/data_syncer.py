import gzip
from abc import ABCMeta, abstractmethod
from typing import AnyStr as Str, Dict

from google.cloud import storage
from pymongo.asynchronous.database import AsyncDatabase

from app.foundation import as_async
from app.foundation.primitives import datetime, json
from app.foundation.server import Logger
from app.shared import Company


class DataFetcher(metaclass=ABCMeta):

    def __init__(self):
        self.company = None
        self._raw = {}

    @abstractmethod
    def source_id(self) -> Str:
        """
        Id of these source, for example linkedin, spectr,
        """
        pass

    @abstractmethod
    def remote_id(self) -> Str:
        """
        remote_id - object id in source
        """
        pass

    @abstractmethod
    def db_update(self) -> Dict:
        """
        Fields to update in database
        """
        pass

    @abstractmethod
    async def _fetch(self, company: Company):
        pass

    def updated_at(self) -> datetime.datetime:
        """
        When this data was last updated at source. If not available, return current time.
        """
        return datetime.now()

    def raw(self) -> Dict:
        """
        Return raw response from the source
        """
        return self._raw

    def __call__(self, company: Company):
        self.company = company
        return self

    async def __aenter__(self):
        self._raw = await self._fetch(self.company)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
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
        async with self._data_fetcher(company):
            raw_data = self._data_fetcher.raw()
            remote_id = self._data_fetcher.remote_id()
            updated_at = self._data_fetcher.updated_at()
            db_update_payload = self._data_fetcher.db_update()
            source_id = self._data_fetcher.source_id()

        bucket_path = '/'.join([
            source_id,
            company.website_id(),
            f"{updated_at:%Y-%m-%d}.json.gz"
        ])
        data = json.dumps(raw_data)
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
                "$set": db_update_payload
            },
        )

        self._logger.info(f"Synced company data", labels={
            "company": company.model_dump(),
            "source": source_id,
            "remote_id": remote_id,
            "updated_at": updated_at,
            "db_update_result": update_result.raw_result,
        })
