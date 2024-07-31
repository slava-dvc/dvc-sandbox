from typing import Dict, List

import httpx

from .client import *
from .sync_action import *
from ...foundation import models


async def push_deal_to_airtable(
        http_client: httpx.AsyncClient,
        api_key,
        base_id,
        deal_table_id,
        people_table_id,
        startup: models.Feature,
        features: Dict[str, models.Feature],
        people: List[models.Person]
) -> bool:
    if not all([startup, features, api_key, base_id, deal_table_id]):
        return False
    airtable_client = AirTableClient(api_key, base_id, http_client)
    sync_action = AirSyncAction(airtable_client, deal_table_id, people_table_id)
    return await sync_action.push(startup, features, people)
