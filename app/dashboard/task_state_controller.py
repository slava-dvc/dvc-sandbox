"""
Centralized Task State Controller for consistent task lifecycle management
"""
import streamlit as st
from datetime import date, datetime, timezone, timedelta
from typing import List, Optional
from app.shared.task import Task, TaskStatus
from app.shared.task_config import ACTIVE_STATES, is_active_status, is_completed_status
from app.dashboard.data import update_task

# Team members list for filtering
TEAM_MEMBERS = ["Marina", "Nick", "Mel", "Charles", "Alexey", "Tony", "Elena", "Vlad", "Slava"]


def initialize_session_state():
    """Initialize session state for task management"""
    if "tasks" not in st.session_state:
        st.session_state["tasks"] = []
    if "active_dialog_task_id" not in st.session_state:
        st.session_state["active_dialog_task_id"] = None
    if "active_tab" not in st.session_state:
        st.session_state["active_tab"] = "Active"


def get_current_user_for_tasks() -> Optional[str]:
    """Get current user for task assignment - checks session state first (testing), then st.user"""
    # Check session state first (for testing with user selector)
    if 'current_user' in st.session_state and st.session_state['current_user']:
        return st.session_state['current_user']
    
    # Fall back to st.user (production)
    if hasattr(st, 'user'):
        try:
            if hasattr(st.user, 'given_name') and hasattr(st.user, 'family_name'):
                return f"{st.user.given_name} {st.user.family_name}"
            elif hasattr(st.user, 'name'):
                return st.user.name
            elif hasattr(st.user, 'email'):
                return st.user.email
        except:
            pass
    
    return None


def get_user_id() -> str:
    """Get current user ID for session key scoping"""
    return get_current_user_for_tasks() or "anon"


def get_dialog_key(task_id: str, user_id: str) -> str:
    """Get user-scoped dialog session key"""
    return f"{user_id}_{task_id}_show_dialog"


def get_task_info_key(task_id: str, user_id: str) -> str:
    """Get user-scoped task info session key"""
    return f"{user_id}_{task_id}_task_info"


def clear_task_dialog_state(task_id: str, user_id: str) -> None:
    """Clear both dialog and task info session keys atomically"""
    dialog_key = get_dialog_key(task_id, user_id)
    task_info_key = get_task_info_key(task_id, user_id)
    
    # Atomic deletion
    keys_to_delete = [k for k in [dialog_key, task_info_key] if k in st.session_state]
    for key in keys_to_delete:
        del st.session_state[key]


def update_task_status(task_id: str, new_status: TaskStatus):
    """Update a task's status"""
    for task_data in st.session_state["tasks"]:
        if isinstance(task_data, dict) and task_data.get('id') == task_id:
            task_data['status'] = new_status.value
            break
        elif hasattr(task_data, 'id') and task_data.id == task_id:
            task_data.status = new_status.value
            break


def open_result_dialog(task_id: str):
    """Open result dialog for a task and set status to pending_result"""
    st.session_state["active_dialog_task_id"] = task_id
    update_task_status(task_id, TaskStatus.PENDING_RESULT)


def save_result(task_id: str, result_text: str, task: Optional[Task] = None):
    """Save task result and mark as completed with history tracking"""
    from app.dashboard.task_result_history import add_result_to_history, migrate_legacy_outcome_to_history
    
    # Get current user and user ID for session key scoping
    current_user = get_current_user_for_tasks() or "Anonymous"
    user_id = get_user_id()
    
    # Handle history management
    if task is not None:
        # Migrate legacy outcome to history if needed
        migrate_legacy_outcome_to_history(task)
        
        # Add new entry to history
        new_entry = add_result_to_history(task, result_text, current_user)
        task.result_history.append(new_entry)
        
        # Update the task status to completed
        update_task_status(task_id, TaskStatus.COMPLETED)
        
        # Clear ALL dialog-related state for this task using scoped keys
        st.session_state["active_dialog_task_id"] = None
        clear_task_dialog_state(task_id, user_id)
        
        # Update the task in the data layer with history
        try:
            update_task(
                task_id,
                status=TaskStatus.COMPLETED.value,
                completed_at=datetime.now(timezone.utc),
                completed_by=current_user,
                outcome=result_text.strip(),  # Latest result for backward compatibility
                result_history=task.result_history  # Full history
            )
        except Exception as e:
            st.error(f"Error saving task result: {str(e)}")
    else:
        # Fallback for when task object is not provided (shouldn't happen with new implementation)
        # Update the task status to completed
        update_task_status(task_id, TaskStatus.COMPLETED)
        
        # Clear ALL dialog-related state for this task using scoped keys
        st.session_state["active_dialog_task_id"] = None
        clear_task_dialog_state(task_id, user_id)
        
        # Update the task in the data layer
        try:
            update_task(
                task_id,
                status=TaskStatus.COMPLETED.value,
                completed_at=datetime.now(timezone.utc),
                completed_by=current_user,
                outcome=result_text.strip()
            )
        except Exception as e:
            st.error(f"Error saving task result: {str(e)}")


def cancel_result(task_id: str):
    """Cancel result dialog and revert task to active"""
    # Get user ID for session key scoping
    user_id = get_user_id()
    
    # Update the task status back to active
    update_task_status(task_id, TaskStatus.ACTIVE)
    
    # Clear ALL dialog-related state for this task using scoped keys
    st.session_state["active_dialog_task_id"] = None
    clear_task_dialog_state(task_id, user_id)
    
    # Update the task in the data layer
    try:
        update_task(
            task_id,
            status=TaskStatus.ACTIVE.value,
            completed_at=None,
            completed_by=None,
            outcome=None
        )
    except Exception as e:
        st.error(f"Error reverting task: {str(e)}")


def get_filtered_tasks(all_tasks: List[Task], view_mode: str) -> List[Task]:
    """
    Filter tasks by view mode (Active/Completed/All)
    Single source of truth for task filtering
    """
    if view_mode == "Active":
        return [t for t in all_tasks if is_active_status(t.status)]
    elif view_mode == "Completed":
        return [t for t in all_tasks if is_completed_status(t.status)]
    else:  # "All"
        return all_tasks


def apply_secondary_filter(tasks: List[Task], filter_option: str, current_user: Optional[str]) -> List[Task]:
    """
    Apply secondary filters like "My tasks", "Overdue", etc.
    """
    today = date.today()
    
    if filter_option == "All tasks":
        return tasks
    elif filter_option == "My active tasks":
        if current_user:
            return [t for t in tasks if is_active_status(t.status) and t.assignee and current_user.lower() in t.assignee.lower()]
        else:
            return []
    elif filter_option == "Created by me":
        if current_user:
            return [t for t in tasks if t.created_by and current_user.lower() in t.created_by.lower()]
        else:
            return []
    elif filter_option == "Overdue":
        return [t for t in tasks if is_active_status(t.status) and t.due_date and t.due_date < today]
    elif filter_option == "Due today":
        return [t for t in tasks if is_active_status(t.status) and t.due_date and t.due_date == today]
    elif filter_option == "Due this week":
        week_end = today + timedelta(days=7)
        return [t for t in tasks if is_active_status(t.status) and t.due_date and today <= t.due_date <= week_end]
    
    return tasks


def set_tab(tab_name: str):
    """Set the active tab"""
    st.session_state["active_tab"] = tab_name


def clear_orphaned_dialog_flags(company_id: str, previous_view: str, current_view: str):
    """Clear orphaned dialog flags when switching tabs"""
    if previous_view != current_view:
        # Clear controller state
        st.session_state["active_dialog_task_id"] = None
        
        # Clear ALL legacy dialog flags (both old and new scoped format)
        dialog_flags = [k for k in st.session_state.keys() if k.startswith("show_results_dialog_") or k.endswith("_show_dialog")]
        for flag in dialog_flags:
            if flag in st.session_state:
                del st.session_state[flag]
        
        # Clear ALL task info keys (both old and new scoped format)
        task_info_keys = [k for k in st.session_state.keys() if k.startswith("completed_task_info_") or k.endswith("_task_info")]
        for key in task_info_keys:
            if key in st.session_state:
                del st.session_state[key]


def migrate_session_state():
    """Migrate old session state structure to new centralized structure"""
    # This function handles migration from old scattered session state
    # to the new centralized structure
    pass  # Implementation will be added as needed based on existing session state patterns
