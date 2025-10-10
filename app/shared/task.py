"""
Task data model for the DVC Portfolio Dashboard
"""
import uuid
from datetime import datetime, date
from typing import Literal
from enum import StrEnum
from pydantic import BaseModel, Field


class Task(BaseModel):
    """Task model for company task management"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str
    title: str
    due_date: date
    assignee: str
    status: Literal["active", "completed"] = "active"
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        # Allow date serialization
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }


class TaskStatus(StrEnum):
    """Task status enum"""
    ACTIVE = "active"
    COMPLETED = "completed"
