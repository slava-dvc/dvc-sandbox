import logging
from http import HTTPStatus

from fastapi import APIRouter, Body, Depends, Response
from .http_models import SyncDealRequest
from .airtable import push_deal_to_airtable
from ..shared import dependencies, LifespanObjects

__all__ = ['router']

router = APIRouter(
    prefix="/integrations",
)


@router.post('/sync/deal')
async def push_deal(
        data: SyncDealRequest = Body(),
        workspace: dict = Depends(dependencies.workspace_by_user_email),
        lifespan_objects: LifespanObjects = Depends(dependencies.lifespan_objects),
):
    if not workspace:
        return Response(status_code=HTTPStatus.NO_CONTENT)
    records_created = 0
    for integration in workspace.get('integrations', []):
        if integration.get('type') == 'airtable':
            records_created += await push_deal_to_airtable(
                http_client=lifespan_objects.http_client,
                api_key=integration.get('api_key'),
                base_id=integration.get('base_id'),
                deal_table_id=integration.get('deal_table_id'),
                people_table_id=integration.get('people_table_id'),
                startup=data.startup,
                features=data.features,
                people=data.people,
            )
    logging.info(f"Synced {records_created} records to Airtable workspace {workspace.get('domain')}")
    if not records_created:
        return Response(status_code=HTTPStatus.NO_CONTENT)
    return Response(status_code=HTTPStatus.CREATED)
