from http import HTTPStatus
from typing import Optional, List

from fastapi import APIRouter, Body, Depends, Response
from google.cloud import storage
from pydantic import BaseModel, Field
from pymongo.asynchronous.database import AsyncDatabase

from app.foundation.server import dependencies, Logger
from app.shared import Company
from app.shared.dependencies import get_scrapin_clinet, get_serpapi_client, get_genai_client, get_spectr_client
from .constants import ACTIVE_COMPANY_STATUSES
from .data_syncer import DataSyncer
from .linkedin_fetcher import LinkedInFetcher
from .googleplay_fetcher import GooglePlayFetcher
from .apple_appstore_fetcher import AppleAppStoreFetcher
from .google_jobs import GoogleJobsFetcher, GoogleJobsDataSyncer
from .spectr_fetcher import SpectrFetcher
from .data_freshness_monitor import DataFreshnessMonitor
from .dependencies import get_job_dispatcher
from .job_dispatcher import JobDispatcher

router = APIRouter(
    prefix="/company_data",
)


class SyncRequest(BaseModel):
    sources: List[str]
    max_items: int = 100000
    statuses: Optional[List[str]] = Field(default_factory=lambda: ACTIVE_COMPANY_STATUSES)


@router.post('/pull', status_code=HTTPStatus.ACCEPTED)
async def trigger_sync(
        data: SyncRequest = Body(),
        job_dispatcher: JobDispatcher = Depends(get_job_dispatcher),
        logger: Logger = Depends(dependencies.get_logger),
):
    logger.info(f"Starting company data pull", labels={
        "sources": data.sources,
        "maxItems": data.max_items,
        "statuses": data.statuses,
    })
    cnt = await job_dispatcher.trigger_many(max_items=data.max_items, sources=data.sources, statuses=data.statuses)
    if cnt:
        logger.info(f"Finished company data pull", labels={
            "sources": data.sources,
            "count": cnt,
            "maxItems": data.max_items,
        })
    return


@router.get('/freshness')
async def get_data_freshness_report(
    response: Response,
    database: AsyncDatabase = Depends(dependencies.get_default_database),
    logger: Logger = Depends(dependencies.get_logger),
):
    """Get data freshness monitoring report for active companies"""
    monitor = DataFreshnessMonitor(database, logger)
    report = await monitor.check_data_freshness()

    if not report["isHealthy"]:
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    return report


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


@router.post('/pull/google_jobs', status_code=HTTPStatus.ACCEPTED)
async def sync_company_google_jobs(
        data: Company = Body(),
        database: AsyncDatabase = Depends(dependencies.get_default_database),
        dataset_bucket: storage.Bucket = Depends(dependencies.get_dataset_bucket),
        serpapi_client=Depends(get_serpapi_client),
        genai_client=Depends(get_genai_client),
        logger: Logger = Depends(dependencies.get_logger),
):
    fetcher = GoogleJobsFetcher(
        database=database,
        serpapi_client=serpapi_client,
        logger=logger,
        genai_client=genai_client,
    )

    data_syncer = GoogleJobsDataSyncer(
        dataset_bucket=dataset_bucket,
        database=database,
        data_fetcher=fetcher,
        logger=logger,
    )

    await data_syncer.sync_one(company=data)
    return


@router.post('/pull/spectr', status_code=HTTPStatus.ACCEPTED)
async def sync_company_spectr(
        data: Company = Body(),
        database: AsyncDatabase = Depends(dependencies.get_default_database),
        dataset_bucket: storage.Bucket = Depends(dependencies.get_dataset_bucket),
        spectr_client = Depends(get_spectr_client),
        logger: Logger = Depends(dependencies.get_logger),
):
    fetcher = SpectrFetcher(
        spectr_client=spectr_client,
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