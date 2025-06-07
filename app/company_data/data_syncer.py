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

    @abstractmethod
    def source_id(self) -> Str:
        """
        Id of these source, for example linkedin, spectr,
        """
        pass

    async def updated_at(self, company: Company) -> datetime.datetime:
        """
        When this data was last updated at source. If not available, return current time.
        """
        return datetime.now()

    @abstractmethod
    async def remote_id(self, company: Company) -> Str:
        """
        remote_id - object id in source
        """
        pass

    @abstractmethod
    async def raw(self, company: Company) -> Dict:
        """
        Return raw response from the source
        """
        pass

    @abstractmethod
    async def db_update_payload(self, company: Company) -> Dict:
        """
        Fields to update in database
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
        raw_data = await self._data_fetcher.raw(company)
        remote_id = await self._data_fetcher.remote_id(company)
        updated_at = await self._data_fetcher.updated_at(company)
        db_update_payload = await self._data_fetcher.db_update_payload(company)
        source_id = self._data_fetcher.source_id()

        data = json.dumps(raw_data)
        compressed_data = gzip.compress(data.encode('utf-8'))
        blob = self._dataset_bucket.blob(f"{source_id}/{remote_id}/{updated_at}/.json.gz")

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
