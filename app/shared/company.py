import uuid
from enum import Enum
from typing import Optional, List, ClassVar, Set, Any
from urllib.parse import urlparse
from bson import ObjectId

from pydantic import BaseModel, Field, AliasChoices, field_validator
from app.foundation.primitives import datetime
from .user import User

__all__ = ["Company", "CompanyStatus"]

BLOCKLISTED_DOMAINS = {'google.com', 'docsend.com', 'linkedin.com'}

class CompanyStatus(str, Enum):
    PROCESSING = "Processing"
    NEW_COMPANY = "New Company"
    DILIGENCE = "Diligence"
    CONTACTED = "Contacted"
    MEETING = "Meeting"
    CHECKIN = "Checkin"
    OFFERED_TO_INVEST = "Offered to Invest"
    SUBMITTED_AL = "Submitted AL"
    GOING_TO_PASS = "Going to Pass"
    PASSED = "Passed"
    DOCS_SENT = "Docs Sent"
    RADAR = "Radar"
    INVESTED = "Invested"
    EXIT = "Exit"
    WRITE_OFF = "Write-off"


class Comment(BaseModel):
    text: str
    user: User
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    createdAt: datetime.datetime = Field(default_factory=datetime.now)


class Company(BaseModel):

    DATA_FIELDS: ClassVar[Set[str]] = {
        "linkedInData", "spectrData", "googlePlayData", "appStoreData", "ourData", "comments"
    }

    id: Optional[str] = Field(..., validation_alias=AliasChoices("_id", 'id'))

    @field_validator('id', mode='before')
    @classmethod
    def validate_object_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    airtableId: Optional[str] = None
    name: str
    website: Optional[str] = None
    domain: Optional[str] = None
    status: Optional[CompanyStatus] = None
    ourData: dict[str, Any] = Field(default_factory=dict, description="Company data we collected")
    blurb: Optional[str] = Field(None, description="Company blurb")
    memorandum: Optional[str] = Field(None, description="Company memorandum")
    comments: Optional[List[Comment]] = Field(default_factory=list)
    concerns: Optional[List[str]] = Field(default_factory=list)

    createdAt: Optional[datetime.datetime] = None
    updatedAt: Optional[datetime.datetime] = None

    linkedInId: Optional[str] = None
    linkedInData: Optional[dict] = None
    linkedInUpdatedAt: Optional[datetime.datetime] = None

    spectrId: Optional[str] = None
    spectrUpdatedAt: Optional[datetime.datetime] = None
    spectrData: Optional[dict] = None

    googlePlayId: Optional[str] = None
    googlePlayData: Optional[dict] = None
    googlePlayUpdatedAt: Optional[datetime.datetime] = None

    appStoreId: Optional[str] = None
    appStoreData: Optional[dict] = None
    appStoreUpdatedAt: Optional[datetime.datetime] = None

    googleJobsUpdatedAt: Optional[datetime.datetime] = None

    def model_dump_for_logs(self):
        return self.model_dump(exclude_none=True, exclude=list(self.DATA_FIELDS) + ["blurb"])

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
