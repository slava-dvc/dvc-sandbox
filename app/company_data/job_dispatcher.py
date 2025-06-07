from typing import List, AnyStr as Str

from google.cloud import pubsub
from pymongo.asynchronous.database import AsyncDatabase

from app.foundation.server import Logger
from app.shared import Company
from infrastructure.queues import company_data

__all__ = ["JobDispatcher"]


class JobDispatcher(object):
    def __init__(
            self,
            database: AsyncDatabase,
            publisher_client: pubsub.PublisherClient,
            project_id: str,
            logger: Logger,
    ):
        self._database = database
        self._publisher_client = publisher_client
        self._logger = logger
        self._source_to_topic_mapping = {
            "linkedin": publisher_client.topic_path(project_id, company_data.linkedin_topic_name),
            "spectr": publisher_client.topic_path(project_id, company_data.spectr_topic_name),
        }

    def is_supported(self, source: Str) -> bool:
        return source in self._source_to_topic_mapping

    async def trigger_many(self, max_items: int, sources: List[Str]) -> int:
        companies = await self.get_companies(max_items)
        count = 0
        for company in companies:
            for source in sources:
                if self.is_supported(source):
                    await self.trigger_one(company, source)
                    count += 1
            self._logger.info("Dispatch company data pull", labels={
                "company": company.model_dump(),
                "sources": sources,
            })
        return count

    async def trigger_one(self, company: Company, source: Str):
        if not self.is_supported(source):
            self._logger.warning("Unsupported source", labels={
                "company_id": company._id,
                "source": source,
            })
            return
        
        topic_path = self._source_to_topic_mapping[source]
        data = company.model_dump_json().encode('utf-8')
        
        future = self._publisher_client.publish(topic_path, data)
        message_id = future.result()
        
        self._logger.info("Published company data pull message", labels={
            "company_id": company._id,
            "source": source,
            "message_id": message_id,
            "topic": topic_path,
        })

    async def get_companies(self, max_items: int = 1000) -> List[Company]:
        companies_collection = self._database["companies"]
        projection = {f: 0 for f in Company.DATA_FIELDS}
        cursor = companies_collection.find(projection=projection).limit(max_items)
        companies = []
        failed_count = 0
        
        async for doc in cursor:
            companies.append(Company.from_dict(doc))

        return companies
