from enum import Enum
from pydantic import BaseModel, Field


class SourceType(str, Enum):
    PITCH_DECK = "pitch_deck"
    COMPANY_WEBSITE = "company_website"
    COMPANY_LINKEDIN = "company_linkedin"
    EXTERNAL_WEBSITE = "external_website"
    EMAIL_UPDATE = "email_update"


SOURCE_TYPES = {
    SourceType.COMPANY_WEBSITE,
    SourceType.COMPANY_LINKEDIN,
    SourceType.EXTERNAL_WEBSITE,
    SourceType.PITCH_DECK,
    SourceType.EMAIL_UPDATE
}


INTERNAL_SOURCES = {
    SourceType.PITCH_DECK,
    SourceType.EMAIL_UPDATE
}


class DataType(str, Enum):
    STRING = 'string',
    NUMBER = 'number',
    DATE = "date",
    URL = 'url',
    LIST = 'list'
    TEXT = 'text'
    BOOLEAN = 'boolean'


class SourceRef(BaseModel):
    page: int | None = None
    type: str | None = None  # It should be SourceType, but there is not validation at rivet site
    quote: str | None = None
    url: str | None = None
    value: str | None = None


class Feature(BaseModel):
    criterion: str
    value: list[str] | str | float | int | bool | None
    source: list[SourceRef] | None = Field(default_factory=list) # Its should be sources but keep for compatibility


class Startup(BaseModel):
    name: str
    website: str | None = None
    email: str | None = None
    foundation_year: str | int | None = None
    features: dict[str, Feature] | None = Field(default_factory=dict)


class Person(BaseModel):
    name: str
    linkedin_url: str | None = None
    features: dict[str, Feature] | None = Field(default_factory=dict)


class Source(BaseModel):
    type: str | None  # It should be SourceType, but there is not validation at rivet site
    url: str | None
    value: str | None = None
