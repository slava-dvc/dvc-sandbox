from functools import cached_property
from typing import Dict, Any, List
from urllib.parse import urlparse

import httpx
from pydantic import BaseModel, Field, model_serializer

from . import models
from .airtable_serializers import field_serializers

__all__ = ['AirTableClient', 'AirTable', 'AirField']

RECORDS_PER_PAGE = 100
MAX_RECORDS_PER_REQUEST = 1_000_000


class AirField(BaseModel):
    '''
    AirTable and AirField classes. Has mess of the AirTable schema representation. And our custom serialization.
    Possible refactoring: Split into two class verticals: One description of AirTable schema and another for dumping data in desired format.
    '''
    id: str
    type: str
    name: str
    description: str | None = None
    options: Dict[str, Any] | None = None
    value: Any | None = None
    sources: List[models.SourceRef] | None = Field(default_factory=list)

    def is_readonly(self) -> bool:
        readonly_type = self.type in _readonly_field_types
        value_is_linked = isinstance(self.options, dict) and 'fieldIdInLinkedTable' in self.options
        return readonly_type or value_is_linked

    @model_serializer()
    def serialize_value(self):
        if self.value is None:
            return None
        serializer = field_serializers.get(self.type, None)
        if not serializer:
            raise ValueError(f"No serializer found for field type {self.type}") from None
        try:
            raw_value = serializer(self.value)
            if raw_value and self.type == 'richText':
                return '\n'.join([raw_value, self.format_sources()])
            return raw_value
        except Exception as e:
            raise ValueError(f"Failed to serialize field {self.name}={self.value}: {e}") from e

    def format_sources(self) -> str:
        """
        Covert sources to bulletpoint list format as markdown links
        :return:
        """

        def make_quote(source: models.SourceRef):
            if source.quote:
                quote = source.quote.strip(' \"\n*')
                if source.page:
                    return f"Page #{source.page}: {quote}"
                return f"{quote}"
            if source.page:
                return f"(Page #{source.page})"
            if source.type == models.SourceType.PITCH_DECK:
                if source.page:
                    return f"Page #{source.page}"
                return "Pitch Deck"
            parsed_url = urlparse(source.url)
            return parsed_url.netloc

        return '\n'.join([f"* [{make_quote(source)}]({source.url})" for source in self.sources if source.url])


class AirTable(BaseModel):
    id: str
    name: str
    primaryFieldId: str
    description: str | None = None
    fields: List['AirField']
    views: List[Any]

    @cached_property
    def fields_by_name(self) -> Dict[str, 'AirField']:
        return {field.name: field for field in self.fields}

    def set_data(self, data: Dict[str, Any]) -> 'AirTable':
        for k, v in data.items():
            field = self.fields_by_name.get(k)
            if not field:
                continue
            field.value = v.get('value') or None
            field.sources = v.get('source') or []
        return self

    def clear_data(self) -> 'AirTable':
        for field in self.fields:
            field.value = None
        return self

    @model_serializer()
    def serialize_data(self, *args, **kwargs) -> Dict[str, Any]:
        fields = {}
        for field in self.fields:
            if field.is_readonly():
                continue
            fields[field.name] = field.model_dump()
        return {'id': self.id, 'name': self.name, 'primaryFieldId': self.primaryFieldId,
            'description': self.description, 'fields': fields, }


class AirTableClient(object):
    def __init__(self, api_key: str, base_id: str, http_client: httpx.AsyncClient):
        self.api_key = str(api_key)
        self.http_client = http_client
        self.base_id = base_id
        self.base_url = f"https://api.airtable.com/v0"
        self.headers = {"Authorization": f"Bearer {self.api_key.strip()}", "Content-Type": "application/json"}

    async def list_records(
            self,
            table_id: str,
            page_size=RECORDS_PER_PAGE,
            max_records=MAX_RECORDS_PER_REQUEST,
            resolve: bool = False, **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Lists records from a table.

        Args:
            table_id: The name of the table.
            resolve: If True, replace IDs with human-readable values.
            **kwargs: Additional query parameters.

        Returns:
            A list of records.
        """
        url = f"{self.base_url}/{self.base_id}/{table_id}"
        all_records = []
        params = {**kwargs, "pageSize": page_size}

        while True:
            response = await self.http_client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            response_data = response.json()

            if "records" in response_data:
                all_records.extend(response_data["records"])

            # Check if we've reached the maximum number of records
            if len(all_records) >= max_records:
                all_records = all_records[:max_records]
                break

            # Check if there's an offset for the next page
            if "offset" in response_data:
                params["offset"] = response_data["offset"]
            else:
                # No more pages
                break

        if resolve:
            all_records = await self._resolve_record_ids(table_id, all_records)
        
        return all_records

    async def get_record(self, table_id: str, record_id: str) -> Dict[str, Any]:
        """
        Gets a single record by ID.

        Args:
            table_id: The name of the table.
            record_id: The ID of the record.

        Returns:
            The record.
        """
        url = f"{self.base_url}/{self.base_id}/{table_id}/{record_id}"
        response = await self.http_client.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    async def create_record(self, table_id: str, fields: Dict[str, Any], typecast=True) -> Dict[str, Any]:
        """
        Creates a new record.

        Args:
            table_id: The name of the table.
            fields: The data for the new record.

        Returns:
            The created record.
        """
        url = f"{self.base_url}/{self.base_id}/{table_id}"
        data = {"fields": fields, "typecast": typecast}
        response = await self.http_client.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    async def update_record(self, table_id: str, record_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates an existing record.

        Args:
            table_id: The name of the table.
            record_id: The ID of the record.
            fields: The updated data for the record.

        Returns:
            The updated record.
        """
        url = f"{self.base_url}/{self.base_id}/{table_id}/{record_id}"
        response = await self.http_client.patch(url, headers=self.headers, json={"fields": fields})
        response.raise_for_status()
        return response.json()

    async def get_base_data(self, **kwargs) -> Dict[str, AirTable]:
        """
        Gets the base schema.

        Args:
            **kwargs: Additional query parameters.

        Returns:
            A dictionary mapping table IDs to AirTable objects.
        """
        url = f"{self.base_url}/meta/bases/{self.base_id}/tables"
        response = await self.http_client.get(url, headers=self.headers, params=kwargs)
        response.raise_for_status()
        data = response.json()
        tables = [AirTable(**table) for table in data["tables"]]
        return {table.id: table for table in tables}

    async def _fetch_linked_table_data(self, table_id: str, tables: Dict[str, AirTable]) -> Dict[str, str]:
        """Fetch primary field values for a linked table."""
        target_table = tables.get(table_id)
        
        if not target_table:
            return {}
        
        primary_field = None
        for field in target_table.fields:
            if field.id == target_table.primaryFieldId:
                primary_field = field.name
                break
        
        if not primary_field:
            return {}
        
        records = await self.list_records(target_table.name, **{'fields[]': primary_field})
        return {rec['id']: rec['fields'].get(primary_field) for rec in records if rec['fields'].get(primary_field)}

    def _resolve_field_value(self, field: AirField, value: Any, linked_table_cache: Dict[str, Dict[str, str]]) -> Any:
        """Resolve field value based on field type, similar to dashboard's convert_filed."""
        if value is None:
            return value
        
        field_type = field.type
        options = {opt['id']: opt['name'] for opt in (field.options or {}).get('choices', [])}
        
        if field_type == 'singleSelect':
            if isinstance(value, list) and len(value) == 1:
                value = value[0]
            return options.get(value, value)
        
        elif field_type == 'multipleSelects':
            if isinstance(value, list):
                return [options.get(v, v) for v in value]
            return value
        
        elif field_type == 'multipleRecordLinks':
            if not isinstance(value, list):
                return value
            
            linked_table_id = (field.options or {}).get('linkedTableId')
            if not linked_table_id or linked_table_id not in linked_table_cache:
                return value
            
            linked_table = linked_table_cache[linked_table_id]
            return [linked_table.get(record_id, record_id) for record_id in value]
        
        return value

    async def _resolve_record_ids(self, table_id: str, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Resolve IDs to human-readable values in record fields."""
        if not records:
            return records
        
        # Get table schema
        tables = await self.get_base_data()
        target_table = tables.get(table_id)
        
        if not target_table:
            return records
        
        # Build cache for linked tables
        linked_table_cache = {}
        for field in target_table.fields:
            if field.type == 'multipleRecordLinks':
                linked_table_id = field.options.get('linkedTableId') if field.options else None
                if linked_table_id and linked_table_id not in linked_table_cache:
                    linked_table_cache[linked_table_id] = await self._fetch_linked_table_data(linked_table_id, tables)
        
        # Resolve fields in each record
        for record in records:
            record_fields = record.get('fields', {})
            
            for field in target_table.fields:
                field_name = field.name
                if field_name in record_fields:
                    field_value = record_fields[field_name]
                    resolved_value = self._resolve_field_value(
                        field, field_value, linked_table_cache
                    )
                    record_fields[field_name] = resolved_value
        
        return records


_readonly_field_types = {
    'aiText', 'button', 'count', 'count', 'createdBy',
    'createdTime', 'formula', 'lastModifiedBy',
    'lastModifiedTime', 'multipleAttachments',
    'multipleCollaborators', 'rollup',
}
