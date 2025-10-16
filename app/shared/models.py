from enum import Enum
from typing import Optional, List, Union
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
    page: Union[int, str, None] = None
    type: Optional[str] = None  # It should be SourceType, but there is not validation at rivet site
    quote: Optional[str] = None
    url: Optional[str] = None
    value: Optional[str] = None


class Feature(BaseModel):
    criterion: str
    value: Union[List[str], str, float, int, bool, None]
    source: Optional[List[SourceRef]] = Field(default_factory=list) # Its should be sources but keep for compatibility


class Startup(BaseModel):
    name: str
    website: Optional[str] = None
    email: Optional[str] = None
    foundation_year: Union[str, int, None] = None
    features: Optional[dict[str, Feature]] = Field(default_factory=dict)


class Person(BaseModel):
    name: str
    linkedin_url: Optional[str] = None
    features: Optional[dict[str, Feature]] = Field(default_factory=dict)


class Source(BaseModel):
    type: Optional[str]  # It should be SourceType, but there is not validation at rivet site
    url: Optional[str]
    value: Optional[str] = None
