from urllib.parse import urlparse
from functools import cached_property
from typing import Dict, Any, List
from pydantic import BaseModel, model_serializer, Field
from .serializers import field_serializers
from ...foundation import models
from ...foundation.server.logger import Logger


__all__ = ['AirTable', 'AirField']


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

        return '\n'.join([
            f"* [{make_quote(source)}]({source.url})" for source in self.sources if source.url
        ])


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
