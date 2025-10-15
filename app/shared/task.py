"""
Task data model for the DVC Portfolio Dashboard
"""
import uuid
from datetime import datetime, date, timezone
from typing import Literal, Optional
from enum import Enum
from pydantic import BaseModel, Field


class Task(BaseModel):
    """Task model for company task management"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str
    text: str  # Changed from 'title' to 'text' to match ACs
    due_date: Optional[date] = None  # Made optional for parsing flexibility
    assignee: str
    status: Literal["active", "completed"] = "active"
    outcome: Optional[str] = None  # For completion results
    notes: Optional[str] = None  # For edit form notes
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = "Unknown"  # User who created the task
    completed_at: Optional[datetime] = None  # For 7-day window logic
    
    class Config:
        # Allow date serialization
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }


class TaskStatus(str, Enum):
    """Task status enum"""
    ACTIVE = "active"
    COMPLETED = "completed"
