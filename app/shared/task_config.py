"""
Centralized Task Status Configuration
Provides a single source of truth for task status logic across the application.
"""
from enum import Enum
from typing import Set
from app.shared.task import TaskStatus


# Centralized status constants
ACTIVE_STATES: Set[str] = {TaskStatus.ACTIVE.value, TaskStatus.PENDING_RESULT.value}
COMPLETED_STATES: Set[str] = {TaskStatus.COMPLETED.value}


def is_active_status(status: str) -> bool:
    """Check if a status is considered active (not completed)"""
    return status in ACTIVE_STATES


def is_completed_status(status: str) -> bool:
    """Check if a status is completed"""
    return status in COMPLETED_STATES


def is_pending_result_status(status: str) -> bool:
    """Check if a status is pending result (waiting for completion dialog)"""
    return status == TaskStatus.PENDING_RESULT.value
