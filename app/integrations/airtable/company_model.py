from typing import Optional
from pydantic import BaseModel, Field
from ...foundation.primitives.datetime import to_utc, datetime


class Company(BaseModel):
    """Model representing a company from Airtable data."""
    
    name: str = Field(description="Company name")
    website: str = Field(None, description="Company website URL")
    updatedAt: datetime = Field(default_factory=lambda: to_utc(datetime.now()), description="Last time record was updated")
    airtableId: str | None = Field(description="Unique identifier from Airtable")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Example Corp",
                "website": "https://example.com",
                "airtableId": "rec123456",
                "updatedAt": "2025-04-03T12:00:00"
            }
        }