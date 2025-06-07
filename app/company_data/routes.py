from fastapi import APIRouter, Body, Depends
from google.cloud import pubsub, storage
from pydantic import BaseModel
from pymongo.asynchronous.database import AsyncDatabase

from app.foundation.server import dependencies, Logger
from app.foundation.server.config import AppConfig
from app.shared import Company
from app.shared.dependencies import get_scrapin_clinet
from .job_dispatcher import JobDispatcher
from .data_syncer import DataSyncer
from .linkedin_company_fetcher import LinkedInCompanyFetcher

router = APIRouter(
    prefix="/company_data",
)


class SyncRequest(BaseModel):
    sources: list[str]
    max_items: int = 100000


@router.post('/pull')
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
        logger=logger,
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
    return {"dispatched": cnt, "sources": sources}


@router.post('/pull/linkedin')
async def sync_company_linkedin(
        data: Company = Body(),
        database: AsyncDatabase = Depends(dependencies.get_default_database),
        dataset_bucket: storage.Bucket = Depends(dependencies.get_dataset_bucket),
        scrapin_client = Depends(get_scrapin_clinet),
        logger: Logger = Depends(dependencies.get_logger),
):
    fetcher = LinkedInCompanyFetcher(
        database=database,
        scrapin_client=scrapin_client,
    )
    
    data_syncer = DataSyncer(
        dataset_bucket=dataset_bucket,
        database=database,
        data_fetcher=fetcher,
        logger=logger,
    )
    
    await data_syncer.sync_one(company=data)
    return {"status": "completed", "company_id": data._id}