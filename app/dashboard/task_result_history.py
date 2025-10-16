"""Utility functions for managing cumulative task result history"""
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.shared.task import Task


def format_result_history_for_display(task: Task) -> str:
    """
    Format result history as readable text for dialog pre-fill
    
    Returns formatted string like:
    === Result #1 (2025-10-15 14:30 by Nick) ===
    Completed initial review, found 3 issues
    
    === Result #2 (2025-10-16 09:15 by Alexey) ===
    Fixed all issues and deployed
    """
    if not hasattr(task, 'result_history') or not task.result_history:
        return ""
    
    formatted_parts = []
    for idx, entry in enumerate(task.result_history, 1):
        timestamp = entry.get("timestamp", "Unknown time")
        if isinstance(timestamp, datetime):
            timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M")
        else:
            timestamp_str = str(timestamp)
        
        user = entry.get("completed_by", "Unknown")
        text = entry.get("text", "")
        
        header = f"=== Result #{idx} ({timestamp_str} by {user}) ==="
        formatted_parts.append(f"{header}\n{text}")
    
    return "\n\n".join(formatted_parts)


def add_result_to_history(task: Task, result_text: str, user: str) -> Dict[str, Any]:
    """
    Add a new result entry to task history
    
    Returns the new entry that was added
    """
    # Ensure result_history exists
    if not hasattr(task, 'result_history'):
        task.result_history = []
    
    completion_number = len(task.result_history) + 1
    
    new_entry = {
        "text": result_text.strip(),
        "timestamp": datetime.now(timezone.utc),
        "completed_by": user,
        "completion_number": completion_number
    }
    
    return new_entry


def get_combined_outcome(task: Task) -> str:
    """
    Get combined outcome text from all history entries
    For backward compatibility with code that reads outcome field
    """
    if not hasattr(task, 'result_history') or not task.result_history:
        return task.outcome or ""
    
    # Return just the latest entry for brevity, or all if needed
    return format_result_history_for_display(task)


def migrate_legacy_outcome_to_history(task: Task) -> None:
    """
    Migrate existing outcome to result_history for backward compatibility
    Call this when a task without history is first saved
    """
    if not hasattr(task, 'result_history'):
        task.result_history = []
    
    # If task has outcome but no history, create initial history entry
    if task.outcome and task.outcome.strip() and not task.result_history:
        initial_entry = {
            "text": task.outcome.strip(),
            "timestamp": task.completed_at or datetime.now(timezone.utc),
            "completed_by": task.completed_by or "Unknown",
            "completion_number": 1
        }
        task.result_history.append(initial_entry)


def get_result_count(task: Task) -> int:
    """Get the number of result entries in history"""
    if not hasattr(task, 'result_history'):
        return 0
    return len(task.result_history)


def get_latest_result(task: Task) -> Optional[str]:
    """Get the latest result text from history"""
    if not hasattr(task, 'result_history') or not task.result_history:
        return task.outcome
    
    latest_entry = task.result_history[-1]
    return latest_entry.get("text", "")
