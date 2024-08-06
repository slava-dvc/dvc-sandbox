import logging
from functools import cached_property
from typing import Dict, Any, List
from pydantic import BaseModel, model_serializer
from .serializers import field_serializers


__all__ = ['AirTable', 'AirField']


class AirField(BaseModel):
    id: str
    type: str
    name: str
    description: str | None = None
    options: Dict[str, Any] | None = None
    value: Any | None = None

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
            return serializer(self.value)
        except Exception as e:
            raise ValueError(f"Failed to serialize field {self.name}={self.value}: {e}") from e


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
                logging.debug(f"Unknown field '{k}' in data for table '{self.name}'")
                continue
            self.fields_by_name[k].value = v
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
                logging.debug(f"Skipping serialization of read-only field '{field.name}'")
                continue
            fields[field.name] = field.model_dump()
        return {
            'id': self.id,
            'name': self.name,
            'primaryFieldId': self.primaryFieldId,
            'description': self.description,
            'fields': fields,
        }


_readonly_field_types = {
    'aiText',
    'button',
    'count',
    'count',
    'createdBy',
    'createdTime',
    'formula',
    'lastModifiedBy',
    'lastModifiedTime',
    'multipleAttachments',
    'multipleCollaborators',
    'rollup',
}