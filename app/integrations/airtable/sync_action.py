import typing
from urllib.parse import urlparse

import yaml

from pathlib import Path
from typing import Dict, List

from .client import AirTableClient, AirTable
from ...foundation import models
from ...foundation.server.logger import Logger


__all__ = ['AirSyncAction']


class AirSyncAction(object):

    def __init__(
            self,
            airtable_client: AirTableClient,
            deal_table_id: str,
            people_table_id: str,
            logger: Logger,
            field_mapping_file: str = None
    ):
        self.airtable_client = airtable_client
        self.deal_table_id = deal_table_id
        self.people_table_id = people_table_id
        self._tables = {}
        self.logger = logger
        self._mapping_schema = self._load_field_mapping(field_mapping_file)

    async def push(
            self,
            startup: models.Startup,
            people: List[models.Person],
            sources: List[models.Source]
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
        return sum([
            await self._push_main(startup, people, sources),
            await self._push_people(people, sources)
        ])

    async def _update_base_data(self) -> Dict[str, AirTable]:
        base_config = await self.airtable_client.get_base_data()
        self._tables = {t.id: t for t in base_config}

    async def _push_people(
            self,
            people: List[models.Person],
            sources: List[models.Source]
    ) -> int:
        records = 0
        for person in people:
            data = {k: {'value': v} for k, v in person.model_dump(exclude='features').items()}
            data |= {f: v.model_dump() for f, v in person.features.items()}
            fields = self._make_fields_for_table(data, self.people_table_id, "people_table", sources)

            if not fields:
                continue

            await self.airtable_client.create_record(self.people_table_id, fields)
            records += 1
        return records

    async def _push_main(
            self,
            startup: models.Startup,
            people: List[models.Person],
            sources: List[models.Source]
    ) -> int:
        data = {k: {'value': v} for k, v in startup.model_dump(exclude='features').items()}
        features = startup.features | _additional_meta_features(startup, people, sources)
        features['Unknown'] = models.Feature(criterion="Unknown Fields", value='\n'.join(_get_unknown_fields(features)))

        data |= {f: v.model_dump() for f, v in features.items()}
        fields = self._make_fields_for_table(data, self.deal_table_id, "startup_table", sources)

        if not fields:
            return 0

        await self.airtable_client.create_record(self.deal_table_id, fields)
        return 1


    def _make_fields_for_table(self, data, air_table_id, mapping_table_id, sources: List[models.Source]) -> typing.Dict:
        target_table: AirTable | None = self._tables.get(air_table_id) or None
        if target_table is None:
            self.logger.error(f"Table {self.deal_table_id} not found in base {self.airtable_client.base_id}")
            return {}

        mapped_data = self._apply_mapping(data, mapping_table_id)
        mapped_data_with_sources = self._update_sources(mapped_data, sources)
        target_table.clear_data().set_data(mapped_data_with_sources)
        record = target_table.model_dump()
        fields = record.get('fields') or {}
        fields = {k: v for k, v in fields.items() if v is not None}
        return fields

    def _update_sources(self, data: typing.Dict[str, typing.Dict], sources: List[models.Source]) -> typing.Dict:
        '''
        Replace the urls for the sources for pitch_deck and other internal sources.
        '''
        pitch_deck_url, email_update_url = None, None
        for source in sources:
            if source.type == models.SourceType.PITCH_DECK:
                pitch_deck_url = source.url
            if source.type == models.SourceType.EMAIL_UPDATE:
                email_update_url = source.url

        for key, value in data.items():
            mappend_sources = []
            sources = value.get('source') or []
            for source_index, source in enumerate(sources):
                type = source.get('type')
                quote = source.get('quote')
                v = source.get('value')
                url = source.get('url')
                page = source.get('page')

                if type == models.SourceType.PITCH_DECK:
                    url = pitch_deck_url
                    if page and url:
                        url += f'#page={page}'

                if type == models.SourceType.EMAIL_UPDATE:
                    url = email_update_url
                    continue

                if not url and v and isinstance(v, str):
                    parsed_url = urlparse(v)
                    if all([parsed_url.scheme, parsed_url.netloc]):
                        url = parsed_url.geturl()
                if url:
                    mappend_sources.append(models.SourceRef(url=url, type=type, quote=quote, page=page))

            value['source'] = mappend_sources
        return data


    def _apply_mapping(self, data: typing.Dict[str, typing.Any], table) -> typing.Dict:
        result = {}  # It can be more efficient inplace, however, this is a simple and easier to debug
        table_mapping = self._mapping_schema.get(table) or {}
        for key, field_mapping in table_mapping.items():
            airtable_field_name = field_mapping.get('airtable_field')
            if not airtable_field_name:
                self.logger.warning(f'No "airtable_field" mapping found for field "{key}" in table "{table}"')
                continue
            mapped_value = field_mapping.get('value')
            if mapped_value:
                result[airtable_field_name] = {
                    "value": mapped_value,
                }
                continue
            # Remove data from the original data to eliminated duplicates with different keys
            data_value = data.pop(key, None) or None
            if data_value is None:
                self.logger.debug(f'No value for field "{key}" -> "{airtable_field_name}" in table "{table}"')
            else:
                result[airtable_field_name] = data_value
        for key in set(data.keys()) - set(result.keys()):
            result[key] = data[key]
        return result

    def _load_field_mapping(self, field_mapping_file) -> Dict[str, Dict]:
        if not field_mapping_file:
            return {}
        mapping_file = Path('resources') / field_mapping_file
        if not mapping_file.exists() or not mapping_file.is_file():
            self.logger.debug(f"Field mapping file not found: {mapping_file}")
            return {}
        try:
            with mapping_file.open('r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            self.logger.error(f"Field mapping file not found: {mapping_file}")
            return {}
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML file: {e}")
            return {}


def _additional_meta_features(
        startup: models.Startup,
        people: List[models.Person],
        sources: List[models.Source]) -> Dict[str, models.Feature]:
    pitch_deck_url, email_update_url = None, None
    for source in sources:
        if source.type == models.SourceType.PITCH_DECK:
            pitch_deck_url = source.url
        if source.type == models.SourceType.EMAIL_UPDATE:
            email_update_url = source.url

    more_features = {
        'Founders': _founders_summary_feature(people),
        'pitch_deck_url': models.Feature(criterion="Pitch Deck URL", value=pitch_deck_url),
        'email_update_url': models.Feature(criterion="Email Update URL", value=email_update_url)
    }

    return more_features


def _get_unknown_fields(data: Dict[str, models.Feature]) -> List[str]:
    result = []
    for key, feature in data.items():
        if key in ['email_update_url', 'pitch_deck_url', 'Founders']:
            continue
        if not feature.value:
            result.append(feature.criterion)
            continue
        value = ','.join([str(v) for v in feature.value]) if isinstance(feature.value, list) else feature.value
        if str(value).lower() in ['unknown', 'n/a', 'none']:
            result.append(feature.criterion)
    return result


def _founders_summary_feature(founders: List[models.Person]) -> models.Feature:
    """
    Returns Markdown with Founder name as link to the linkedin_url
    :param founders:
    :return:
    """
    summaries = []
    for founder in founders:
        name = founder.name
        linkedin_url = founder.linkedin_url
        founder_summary_feature: models.Feature = founder.features.get('Founder Summary')
        bio = founder_summary_feature.value if founder_summary_feature else ''

        founder_summary = f"[{name}]({linkedin_url}):\n{bio}\n" if linkedin_url else f"{name}:\n{bio}\n"
        summaries.append(founder_summary)
    value = '\n'.join(summaries)
    return models.Feature(
        criterion="Founders Summary",
        value=value
    )
