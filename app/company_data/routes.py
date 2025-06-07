from fastapi import APIRouter, Body, Depends
from google.cloud import pubsub
from pydantic import BaseModel
from pymongo.asynchronous.database import AsyncDatabase
from watchfiles import awatch

from app.foundation.server import dependencies, Logger
from app.shared import Company
from .config import AppConfig
from .job_dispatcher import JobDispatcher
from .data_syncer import  DataSyncer
from .linkedin_company_fetcher import LinkedInCompanyFetcher

router = APIRouter(
    prefix="/company_data",
)


class SyncRequest(BaseModel):
    sources: list
    max_items: int = 100000


@router.post('pull')
async def trigger_sync(
        data: SyncRequest = Body(),
        database: AsyncDatabase = Depends(dependencies.get_default_database),
        publisher_client: pubsub.PublisherClient = Depends(dependencies.get_publisher_client),
        logger: Logger = Depends(dependencies.get_logger),
        config: AppConfig = Depends(dependencies.get_config),

):
    job_dispatcher = JobDispatcher(
        database=database,
        publisher_client=publisher_client,
        project_id=config.project_id,
    )
    sources = [s for s in data.sources if job_dispatcher.is_supported(s)]
    logger.info(f"Starting company data pull", labels={
        "sources": sources,
        "max_items": data.max_items,
    })
    cnt = await job_dispatcher.trigger_many(max_items=data.max_items, sources=sources)
    logger.info(f"Finished company data pull", labels={
        "sources": sources,
        "count": cnt,
        "max_items": data.max_items,
    })


@router.post('pull/linkedin')
async def sync_company_linkedin(
        data: Company = Body(),
):
    fetcher = LinkedInCompanyFetcher(

    )
    data_syncer = DataSyncer(

    )
    await data_syncer.sync_one(company=data)