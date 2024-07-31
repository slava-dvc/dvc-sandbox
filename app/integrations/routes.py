import logging
from http import HTTPStatus

from fastapi import APIRouter, Body, Depends, Response
from .http_models import SyncDealRequest
from .airtable import AirTableClient, AirSyncAction
from ..foundation import env
from ..lifespan_objects import lifespan_objects, LifespanObjects

__all__ = ['router']

router = APIRouter(
    prefix="/integrations",
)


@router.post('/sync/deal')
async def push_deal(
        data: SyncDealRequest = Body(),
        lifespan_objects: LifespanObjects = Depends(lifespan_objects),
):
    user_email: str = data.user_email
    api_key, base_id, table_id = None, None, None

    if user_email.endswith('@ingainer.pro'):
        base_id = 'appVRbLTU7hLVGn32'
        table_id = 'tblwJiW7t4LZJS0fS'
        api_key = str(env.get_env('AIRTABLE_INGAINER'))

    if not all([api_key, base_id, table_id]):
        logging.info(f"Integration for {user_email} not found")
        return Response(status_code=HTTPStatus.NO_CONTENT)

    airtable_client = AirTableClient(api_key, base_id, lifespan_objects.http_client)
    sync_action = AirSyncAction(airtable_client, table_id)
    success = await sync_action.push(data.startup, data.features)
    if success:
        return Response(status_code=HTTPStatus.CREATED)
    else:
        return Response(status_code=HTTPStatus.BAD_REQUEST)
