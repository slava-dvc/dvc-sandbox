from typing import Optional, List, Literal, ClassVar, Set
from urllib.parse import urlparse

from pydantic import BaseModel
from app.foundation.primitives import datetime


BLOCKLISTED_DOMAINS = {'google.com', 'docsend.com', 'linkedin.com'}


class Company(BaseModel):

    DATA_FIELDS: ClassVar[Set[str]] = {
        "linkedInData", "spectrData",
    }

    _id: str
    airtableId: str
    name: str
    website: str = ""

    createdAt: datetime.datetime
    updatedAt: datetime.datetime | None

    linkedInId: str | None = None
    linkedInData: dict | None = None
    linkedInUpdatedAt: datetime.datetime | None = None

    spectrId: str | None
    spectrUpdatedAt: datetime.datetime | None = None
    spectrData: dict | None = None

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
        parsed = urlparse(self.website)
        domain = '.'.join(parsed.netloc.split('.')[-2:])
        return domain

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            _id=data['_id'],
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
        )
