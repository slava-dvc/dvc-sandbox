from typing import List, Dict, Any, Optional
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
    company_name: Optional[str] = Field(None, alias="companyName")
    title: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    extensions: List[str] = Field(default_factory=list)
    job_highlights: Optional[List[JobHighlight]] = Field(None, alias="jobHighlights")
    apply_options: List[ApplyOption] = Field(default_factory=list, alias="applyOptions")
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
    via: Optional[str] = None

    @field_validator('id', mode='before')
    @classmethod
    def validate_object_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        populate_by_name = True