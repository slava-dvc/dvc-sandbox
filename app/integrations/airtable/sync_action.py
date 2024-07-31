import asyncio
import logging
from typing import Dict, List
from .client import AirTableClient, Table
from ...foundation import models


__all__ = ['AirSyncAction']


class AirSyncAction(object):

    def __init__(
            self,
            airtable_client: AirTableClient,
            startup_table_id: str,
            people_table_id: str
    ):
        self.airtable_client = airtable_client
        self.startup_table_id = startup_table_id
        self.people_table_id = people_table_id
        self._tables = {}

    async def push(
            self,
            startup: models.Startup,
            features: Dict[str, models.Feature],
            people: List[models.Person]
    ) -> int:
        """
        Pushes startup, features, and people data to Airtable.

        This method updates the base data and then pushes the provided startup,
        features, and people information to their respective tables in Airtable.

        Parameters:
        -----------
        startup : models.Startup
            The startup object containing information to be pushed to Airtable.
        features : Dict[str, models.Feature]
            A dictionary of features associated with the startup.
        people : List[models.Person]
            A list of person objects to be pushed to Airtable.

        Returns:
        --------
        int
            The total number of records successfully pushed to Airtable.
        """
        await self._update_base_data()
        return sum(await asyncio.gather(
            self._push_startup(startup, features),
            self._push_people(people)
        ))

    async def _update_base_data(self) -> Dict[str, Table]:
        base_config = await self.airtable_client.get_base_data()
        self._tables = {t.id: t for t in base_config}

    async def _push_people(self, people: List[models.Person]) -> int:
        target_table = self._tables.get(self.people_table_id) or None
        if target_table is None:
            logging.error(f"Table {self.startup_table_id} not found in base {self.airtable_client.base_id}")
            return False
        records = 0
        for person in people:
            data = person.model_dump(exclude='features') | {f: v.value for f, v in person.features.items()}
            fields = self._prepare_fields(data, target_table)
            if not fields:
                continue
            await self.airtable_client.create_record(self.people_table_id, fields)
            records += 1
        return records


    async def _push_startup(self, startup: models.Startup, features: dict[str, models.Feature]) -> int:
        target_table = self._tables.get(self.startup_table_id) or None
        if target_table is None:
            logging.error(f"Table {self.startup_table_id} not found in base {self.airtable_client.base_id}")
            return 0

        data = startup.model_dump() | {f: v.value for f, v in features.items()}

        fields = self._prepare_fields(data, target_table)
        if not fields:
            return 0

        await self.airtable_client.create_record(self.startup_table_id, fields)
        return 1

    def _prepare_fields(self, data: Dict[str, str], table_config: Table):
        fields_cfg = {f.name: f for f in table_config.fields}

        def make_value(v):
            if isinstance(v, list):
                return ','.join(v)
            return v

        fields = {
            k: make_value(v) for k, v in data.items()
            if k in fields_cfg
        }
        if not fields:
            logging.error(f"Table {table_config.id} in base {self.airtable_client.base_id} misconfigured")
            return None
        return fields
