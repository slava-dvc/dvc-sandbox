from typing import List, Dict, Any
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field, AliasChoices, field_validator


class ApplyOption(BaseModel):
    title: str
    link: str


class JobHighlight(BaseModel):
    title: str
    items: List[str]


class Job(BaseModel):
    id: str = Field(validation_alias=AliasChoices("_id", "id"))
    company_name: str | None = Field(None, alias="companyName")
    title: str | None = None
    location: str | None = None
    description: str | None = None
    extensions: List[str] = Field(default_factory=list)
    job_highlights: List[JobHighlight] | None = Field(None, alias="jobHighlights")
    apply_options: List[ApplyOption] = Field(default_factory=list, alias="applyOptions")
    created_at: datetime | None = Field(None, alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")
    via: str | None = None

    @field_validator('id', mode='before')
    @classmethod
    def validate_object_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        populate_by_name = True