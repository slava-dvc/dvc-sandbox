import logging
from typing import Dict
from .client import AirTableClient, Table
from ...foundation import models


class AirSyncAction(object):

    def __init__(
            self,
            airtable_client: AirTableClient,
            startup_table_id: str
    ):
        self.airtable_client = airtable_client
        self.startup_table_id = startup_table_id

    async def push(
            self,
            startup: models.Startup,
            features: dict[str, models.Feature]
    ):
        """
        :param startup:
        :param features:
        :return:
        """
        data = startup.model_dump() | {f: v.value for f, v in features.items()}
        base_config = await self.airtable_client.get_base_data()
        tables = {t.id: t for t in base_config}
        target_table = tables.get(self.startup_table_id) or None
        if target_table is None:
            logging.error(f"Table {self.startup_table_id} not found in base {self.airtable_client.base_id}")
            return False

        fields = self._prepare_fields(data, target_table)
        if not fields:
            logging.error(f"Table {self.startup_table_id} in base {self.airtable_client.base_id} misconfigured")
            return None

        return await self.airtable_client.create_record(self.startup_table_id, fields)

    def _prepare_fields(self, data: Dict[str, str], table_config: Table):
        fields_cfg = {f.name: f for f in table_config.fields}

        def make_value(v):
            if isinstance(v, list):
                return ','.join(v)
            return str(v)

        fields = {
            k: make_value(v) for k, v in data.items()
            if k in fields_cfg
        }
        if not fields:
            return None
        return fields