from enum import StrEnum
from typing import Optional, List, ClassVar, Set, Any
from urllib.parse import urlparse

from pydantic import BaseModel, Field, AliasChoices
from app.foundation.primitives import datetime


__all__ = ["Company", "CompanyStatus"]

BLOCKLISTED_DOMAINS = {'google.com', 'docsend.com', 'linkedin.com'}

class CompanyStatus(StrEnum):
    NEW_COMPANY = "New Company"
    DILIGENCE = "Diligence"
    CONTACTED = "Contacted"
    MEETING = "Meeting"
    CHECKIN = "Checkin"
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
        "linkedInData", "spectrData", "googlePlayData", "appStoreData", "ourData", "blurb"
    }

    id: str | None = Field(..., validation_alias=AliasChoices("_id", 'id'))
    airtableId: str
    name: str
    website: str | None = None
    status: CompanyStatus | None = None
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

    def model_dump_for_logs(self):
        return self.model_dump(exclude_none=True, exclude=self.DATA_FIELDS)

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
