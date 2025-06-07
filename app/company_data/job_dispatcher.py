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

    async def trigger_many(self, max_items: List[Str], sources) -> int:
        companies = await self.get_companies()
        for company in companies:
            for source in sources:
                await self.trigger_one(company, source)
            self._logger.info("Dispatch company data pull", labels={
                "company": company.model_dump(),
                "source": sources,
            })

    async def trigger_one(self, company: Company, source: Str):
        topic_path = self._source_to_topic_mapping[source]
        data = company.model_dump()
        pass

    async def get_companies() -> List[Company]:
        companies_collection = self._database["companies"]
        pass
