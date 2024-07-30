from enum import Enum
from pydantic import BaseModel, Field


class Startup(BaseModel):
    name: str
    website: str | None = None
    email: str | None = None
    foundation_year: str | int | None = None


class SourceType(str, Enum):
    PITCH_DECK = "pitch_deck"
    COMPANY_WEBSITE = "company_website"
    COMPANY_LINKEDIN = "company_linkedin"
    EXTERNAL_WEBSITE = "external_website"
    EMAIL_UPDATE = "email_update"


class Source(BaseModel):
    type: SourceType
    url: str | None
    value: str | None


class SourceRef(BaseModel):
    page: int | None = Field(ge=0)
    type: SourceType | None
    quote: str | None
    value: str | None


class Value(BaseModel):
    value: str | list | None
    source: list[SourceRef] | None


class DataType(str, Enum):
    STRING = 'string',
    NUMBER = 'number',
    DATE = "date",
    URL = 'url',
    LIST = 'list'
    TEXT = 'text'
    BOOLEAN = 'boolean'


class Feature(BaseModel):
    criterion: str
    value: list[str] | str | float | int | bool | None
    source: list[SourceRef] | None
