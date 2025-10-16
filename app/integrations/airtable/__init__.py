from dataclasses import dataclass
from typing import Dict, List

import httpx
from app.foundation.server import Logger
from app.shared import AirTableClient, models
from .sync_action import *
from .pull_companies import pull_companies_from_airtable


__all__ = ['AirTableConfig', 'push_deal_to_airtable', 'pull_companies_from_airtable']


@dataclass
class AirTableConfig():
    api_key: str
    base_id: str
    deal_table_id: str
    people_table_id: str
    field_mapping_file: str


async def push_deal_to_airtable(
        http_client: httpx.AsyncClient,
        airtable_config: AirTableConfig,
        startup: models.Feature,
        people: List[models.Person],
        sources: list[models.Source],
        logger: Logger
) -> bool:
    airtable_client = AirTableClient(
        api_key=airtable_config.api_key,
        base_id=airtable_config.base_id,
        http_client=http_client
    )
    sync_action = AirSyncAction(
        airtable_client=airtable_client,
        deal_table_id=airtable_config.deal_table_id,
        people_table_id=airtable_config.people_table_id,
        logger=logger,
        field_mapping_file=airtable_config.field_mapping_file
    )

    return await sync_action.push(startup, people, sources)
