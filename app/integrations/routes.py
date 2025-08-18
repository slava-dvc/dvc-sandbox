from http import HTTPStatus

from fastapi import APIRouter, Body, Depends, Response, Query
from pymongo import MongoClient
from .http_models import SyncDealRequest
from .airtable import push_deal_to_airtable, AirTableConfig, pull_companies_from_airtable, AirTableClient
from ..foundation import get_env
from ..shared import dependencies
from ..foundation.server.dependencies import get_mongo_client, get_logger, get_http_client

__all__ = ['router']

router = APIRouter(
    prefix="/integrations",
)


@router.post('/sync/deal')
async def push_deal(
        data: SyncDealRequest = Body(),
        workspace: dict = Depends(dependencies.workspace_by_user_email),
        http_client = Depends(get_http_client),
        logger = Depends(get_logger),
):
    if not workspace:
        return Response(status_code=HTTPStatus.NO_CONTENT)
    records_created = 0
    for integration in workspace.get('integrations', []):
        if integration.get('type') == 'airtable':
            airtable_config = AirTableConfig(
                api_key=integration.get('api_key'),
                base_id=integration.get('base_id'),
                deal_table_id=integration.get('deal_table_id'),
                people_table_id=integration.get('people_table_id'),
                field_mapping_file = integration.get('field_mapping_file'),
            )
            records_created += await push_deal_to_airtable(
                http_client=http_client,
                airtable_config=airtable_config,
                startup=data.startup,
                people=data.people,
                sources=data.sources,
                logger=logger
            )
    logger.info(f"Synced {records_created} records to Airtable workspace {workspace.get('domain')}")
    if not records_created:
        return Response(status_code=HTTPStatus.NO_CONTENT)
    return Response(status_code=HTTPStatus.CREATED)


@router.post('/airtable/pull_companies', status_code=HTTPStatus.NO_CONTENT)
async def airtable_pull_companies(
        http_client = Depends(get_http_client),
        mongo_client: MongoClient = Depends(get_mongo_client),
        logger = Depends(get_logger),
):
    """
    Pull companies from Airtable and store them to MongoDB.
    """

    airtable_client = AirTableClient(
        api_key=get_env('AIRTABLE_API_KEY'),
        base_id='appRfyOgGDu7UKmeD',
        http_client=http_client
    )

    await pull_companies_from_airtable(
        airtable_client=airtable_client,
        mongo_client=mongo_client,
        table_id='tblJL5aEsZFa0x6zY',
        logger=logger
    )


