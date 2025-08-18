from typing import List, AnyStr as Str

from google.cloud import pubsub
from pymongo.asynchronous.database import AsyncDatabase

from app.foundation.server import Logger
from app.shared import Company, CompanyStatus
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
            "googleplay": publisher_client.topic_path(project_id, company_data.googleplay_topic_name),
            "appstore": publisher_client.topic_path(project_id, company_data.appstore_topic_name),
            "google_jobs": publisher_client.topic_path(project_id, company_data.google_jobs_topic_name),
        }

    def is_supported(self, source: Str) -> bool:
        return source in self._source_to_topic_mapping

    async def trigger_many(self, max_items: int, sources: List[Str]) -> int:
        supported_sources = [source for source in sources if self.is_supported(source)]
        if not supported_sources:
            self._logger.warning("No supported sources", labels={
                "sources": sources,
            })
            return count
        if len(supported_sources) != len(sources):
            self._logger.warning("Some sources are not supported", labels={
                "sources": sources,
                "supported_sources": supported_sources,
            })
            sources = supported_sources

        companies_collection = self._database["companies"]
        projection = {f: 0 for f in Company.DATA_FIELDS}
        query = {'status': str(CompanyStatus.INVESTED)}
        cursor = companies_collection.find(query, projection=projection).limit(max_items)
        count = 0
        async for company_data in cursor:
            try:
                company = Company.model_validate(company_data)
                if not company.has_valid_website():
                    self._logger.warning("Company has no valid website", labels={
                        "company": company.model_dump(exclude_none=True, exclude=['blurb']),
                        "sources": sources,
                    })
                    continue

                for source in supported_sources:
                    await self.trigger_one(company, source)
                    count += 1
            except Exception as e:
                self._logger.error("Failed to dispatch company data pull", exc_info=e, labels={
                    "company": {
                        "id": str(company_data.get("_id")),
                        "airtableId": company_data.get("airtableId"),
                        "name": company_data.get("name"),
                        "website": company_data.get("website"),
                        "status": company_data.get("status"),
                    },
                    "exception": str(e),
                    "sources": sources,
                })
                continue
        return count

    async def trigger_one(self, company: Company, source: Str):
        if not self.is_supported(source):
            self._logger.warning("Unsupported source", labels={
                "company": company.model_dump(exclude_none=True),
                "source": source,
            })
            return
        
        topic_path = self._source_to_topic_mapping[source]
        data = company.model_dump_json().encode('utf-8')
        
        future = self._publisher_client.publish(topic_path, data)
        message_id = future.result()
        
        self._logger.info("Dispatch company data pull", labels={
            "company": company.model_dump(exclude_none=True),
            "source": source,
            "messageId": str(message_id),
            "topic": topic_path,
        })
