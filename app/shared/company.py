from enum import StrEnum
from typing import Optional, List, ClassVar, Set, Any
from urllib.parse import urlparse

from pydantic import BaseModel, Field
from app.foundation.primitives import datetime


__all__ = ["Company", "CompanyStatus"]

BLOCKLISTED_DOMAINS = {'google.com', 'docsend.com', 'linkedin.com'}

class CompanyStatus(StrEnum):
    NEW_COMPANY = "New Company"
    DILIGENCE = "Diligence"
    IN_PROGRESS = "In Progress"
    OFFERED_TO_INVEST = "Offered to Invest"
    GOING_TO_PASS = "Going to Pass"
    PASSED = "Passed"
    DOCS_SENT = "Docs Sent"
    RADAR = "Radar"
    INVESTED = "Invested"
    EXIT = "Exit"
    WRITE_OFF = "Write-off"


class Company(BaseModel):

    DATA_FIELDS: ClassVar[Set[str]] = {
        "linkedInData", "spectrData", "googlePlayData", "appStoreData", "ourData"
    }

    airtableId: str
    name: str
    website: str | None = ""
    status: CompanyStatus | None = None
    id: str | None = None
    ourData: dict[str, Any] = Field(default_factory=dict, description="Company data we collected")
    blurb: str | None = Field(None, description="Company blurb")

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
            blurb=data.get('blurb'),
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
