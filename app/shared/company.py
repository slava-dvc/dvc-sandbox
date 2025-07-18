from typing import Optional, List, Literal, ClassVar, Set
from urllib.parse import urlparse

from pydantic import BaseModel, Field
from app.foundation.primitives import datetime


BLOCKLISTED_DOMAINS = {'google.com', 'docsend.com', 'linkedin.com'}


class Company(BaseModel):

    DATA_FIELDS: ClassVar[Set[str]] = {
        "linkedInData", "spectrData", "googlePlayData", "appStoreData",
    }

    id: str
    airtableId: str
    name: str
    website: str = ""
    blurb: str = Field(None, description="Company blurb")

    createdAt: datetime.datetime | None = None
    updatedAt: datetime.datetime | None = None

    linkedInId: str | None = None
    linkedInData: dict | None = None
    linkedInUpdatedAt: datetime.datetime | None = None

    spectrId: str | None = None
    spectrUpdatedAt: datetime.datetime | None = None
    spectrData: dict | None = None

    googlePlayId: str | None = None
    googlePlayData: dict | None = None
    googlePlayUpdatedAt: datetime.datetime | None = None

    appStoreId: str | None = None
    appStoreData: dict | None = None
    appStoreUpdatedAt: datetime.datetime | None = None

    googleJobsUpdatedAt: datetime.datetime | None = None

    def has_valid_website(self):
        if not self.website:
            return False
        for domain in BLOCKLISTED_DOMAINS:
            if domain in self.website:
                return False
        return True

    def website_id(self):
        if not self.has_valid_website():
            return None
        website = self.website.lower()
        if not website.startswith('http'):
            website = 'http://' + website
        parsed = urlparse(website)
        domain = '.'.join(parsed.netloc.split('.')[-2:])
        return domain

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=str(data['_id']),
            airtableId=data['airtableId'],
            name=data['name'],
            createdAt=datetime.any_to_datetime(data.get('createdAt')),
            updatedAt=datetime.any_to_datetime(data.get('updatedAt')),
            website=data['website'],
            linkedInId=data.get('linkedInId'),
            linkedInData=data.get('linkedInData'),
            linkedInUpdatedAt=datetime.any_to_datetime(data.get('linkedInUpdatedAt')),
            spectrId=data.get('spectrId'),
            spectrUpdatedAt=datetime.any_to_datetime(data.get('spectrUpdatedAt')),
            spectrData=data.get('spectrData'),
            googlePlayId=data.get('googlePlayId'),
            googlePlayData=data.get('googlePlayData'),
            googlePlayUpdatedAt=datetime.any_to_datetime(data.get('googlePlayUpdatedAt')),
            appStoreId=data.get('appStoreId'),
            appStoreData=data.get('appStoreData'),
            appStoreUpdatedAt=datetime.any_to_datetime(data.get('appStoreUpdatedAt')),
        )
