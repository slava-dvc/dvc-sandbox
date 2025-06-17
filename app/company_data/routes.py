from http import HTTPStatus

from fastapi import APIRouter, Body, Depends
from google.cloud import pubsub, storage
from pydantic import BaseModel
from pymongo.asynchronous.database import AsyncDatabase

from app.foundation.server import dependencies, Logger
from app.foundation.server.config import AppConfig
from app.shared import Company
from app.shared.dependencies import get_scrapin_clinet, get_serpapi_client
from .job_dispatcher import JobDispatcher
from .data_syncer import DataSyncer
from .linkedin_fetcher import LinkedInFetcher
from .googleplay_fetcher import GooglePlayFetcher
from .apple_appstore_fetcher import AppleAppStoreFetcher

router = APIRouter(
    prefix="/company_data",
)


class SyncRequest(BaseModel):
    sources: list[str]
    max_items: int = 100000


@router.post('/pull', status_code=HTTPStatus.ACCEPTED)
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
    logger.info(f"Starting company data pull", labels={
        "sources": data.sources,
        "max_items": data.max_items,
    })
    cnt = await job_dispatcher.trigger_many(max_items=data.max_items, sources=data.sources)
    if cnt:
        logger.info(f"Finished company data pull", labels={
            "sources": data.sources,
            "count": cnt,
            "max_items": data.max_items,
        })
    return


@router.post('/pull/linkedin', status_code=HTTPStatus.ACCEPTED)
async def sync_company_linkedin(
        data: Company = Body(),
        database: AsyncDatabase = Depends(dependencies.get_default_database),
        dataset_bucket: storage.Bucket = Depends(dependencies.get_dataset_bucket),
        scrapin_client = Depends(get_scrapin_clinet),
        logger: Logger = Depends(dependencies.get_logger),
):
    fetcher = LinkedInFetcher(
        database=database,
        scrapin_client=scrapin_client,
        logger=logger,
    )
    
    data_syncer = DataSyncer(
        dataset_bucket=dataset_bucket,
        database=database,
        data_fetcher=fetcher,
        logger=logger,
    )
    
    await data_syncer.sync_one(company=data)
    return


@router.post('/pull/googleplay', status_code=HTTPStatus.ACCEPTED)
async def sync_company_googleplay(
        data: Company = Body(),
        database: AsyncDatabase = Depends(dependencies.get_default_database),
        dataset_bucket: storage.Bucket = Depends(dependencies.get_dataset_bucket),
        serpapi_client = Depends(get_serpapi_client),
        logger: Logger = Depends(dependencies.get_logger),
):
    fetcher = GooglePlayFetcher(
        database=database,
        serpapi_client=serpapi_client,
        logger=logger,
    )
    
    data_syncer = DataSyncer(
        dataset_bucket=dataset_bucket,
        database=database,
        data_fetcher=fetcher,
        logger=logger,
    )
    
    await data_syncer.sync_one(company=data)
    return


@router.post('/pull/appstore', status_code=HTTPStatus.ACCEPTED)
async def sync_company_appstore(
        data: Company = Body(),
        database: AsyncDatabase = Depends(dependencies.get_default_database),
        dataset_bucket: storage.Bucket = Depends(dependencies.get_dataset_bucket),
        serpapi_client = Depends(get_serpapi_client),
        logger: Logger = Depends(dependencies.get_logger),
):
    fetcher = AppleAppStoreFetcher(
        database=database,
        serpapi_client=serpapi_client,
        logger=logger,
    )
    
    data_syncer = DataSyncer(
        dataset_bucket=dataset_bucket,
        database=database,
        data_fetcher=fetcher,
        logger=logger,
    )
    
    await data_syncer.sync_one(company=data)
    return