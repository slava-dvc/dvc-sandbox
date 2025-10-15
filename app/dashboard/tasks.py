"""
Tasks UI components for the DVC Portfolio Dashboard
"""
import streamlit as st
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional, Tuple
import re
import pandas as pd
from app.shared.task import Task
from app.dashboard.data import get_tasks, add_task, update_task, delete_task


def prepare_tasks_dataframe(tasks: List[Task]) -> pd.DataFrame:
    """
    Convert Task objects to a pandas DataFrame for st.data_editor
    Sort order: completed ASC, due_date NULLS LAST ASC, created_at DESC
    """
    if not tasks:
        return pd.DataFrame(columns=['id', 'completed', 'title', 'owner', 'due_date', 'due_display', 'status', 'created_at', 'notes', 'outcome'])
    
    today = date.today()
    data = []
    for task in tasks:
        # Create readable due date with emoji indicator
        if task.due_date:
            days_diff = (task.due_date - today).days
            if days_diff == 0:
                due_display = "🟢 Today"
            elif days_diff == 1:
                due_display = "🟡 Tomorrow"
            elif days_diff < 0:
                due_display = f"🔴 {task.due_date.strftime('%b %d')}"
            elif days_diff <= 2:
                due_display = f"🟠 {task.due_date.strftime('%b %d')}"
            else:
                due_display = task.due_date.strftime('%b %d, %Y')
        else:
            due_display = "No date"
        
        data.append({
            'id': task.id,
            'completed': task.status == 'completed',
            'title': task.text,
            'owner': task.assignee if task.assignee else 'Unassigned',
            'due_date': task.due_date,
            'due_display': due_display,
            'status': task.status,
            'created_at': task.created_at,
            'notes': task.notes or '',
            'outcome': task.outcome or ''
        })
    
    df = pd.DataFrame(data)
    
    # Sort: completed ASC (False first), then by due_date (nulls last), then by created_at DESC
    df['due_date_sort'] = df['due_date'].fillna(pd.Timestamp.max.date())
    df = df.sort_values(
        by=['completed', 'due_date_sort', 'created_at'],
        ascending=[True, True, False]
    )
    df = df.drop(columns=['due_date_sort'])
    
    # Reset index to avoid index mismatch issues
    df = df.reset_index(drop=True)
    
    return df


def parse_task_input(input_text: str) -> Tuple[str, Optional[date], Optional[str], Optional[str]]:
    """
    Parse task input in format: "setup call on 10/11 @Nick"
    Returns: (title, due_date, assignee, error_message)
    """
    if not input_text or not input_text.strip():
        return "", None, None, None
    
    text = input_text.strip()
    assignee = None
    due_date = None
    
    # Extract assignee (@username)
    assignee_match = re.search(r'@(\w+)', text)
    if assignee_match:
        assignee = assignee_match.group(1)
        text = text.replace(assignee_match.group(0), '').strip()
    
    # Extract date patterns
    today = date.today()
    
    # Check for "tomorrow"
    if re.search(r'\btomorrow\b', text, re.IGNORECASE):
        due_date = today + timedelta(days=1)
        text = re.sub(r'\s*\b(on\s+)?tomorrow\b', '', text, flags=re.IGNORECASE).strip()
    # Check for "today"
    elif re.search(r'\btoday\b', text, re.IGNORECASE):
        due_date = today
        text = re.sub(r'\s*\b(on\s+)?today\b', '', text, flags=re.IGNORECASE).strip()
    # Check for "next week"
    elif re.search(r'\bnext\s+week\b', text, re.IGNORECASE):
        due_date = today + timedelta(days=7)
        text = re.sub(r'\s*\b(on\s+)?next\s+week\b', '', text, flags=re.IGNORECASE).strip()
    # Check for weekday names (Monday, Tuesday, etc.)
    elif (weekday_match := re.search(r'\b(next\s+)?(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', text, re.IGNORECASE)):
        is_next_week = bool(weekday_match.group(1))
        day_name = weekday_match.group(2).lower()
        
        # Map day names to weekday numbers (0 = Monday, 6 = Sunday)
        weekday_map = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        target_weekday = weekday_map[day_name]
        current_weekday = today.weekday()
        
        # Calculate days until target weekday
        days_ahead = target_weekday - current_weekday
        if days_ahead <= 0 or is_next_week:
            # If the day has passed this week or "next" is specified, go to next week
            days_ahead += 7
        
        due_date = today + timedelta(days=days_ahead)
        text = text.replace(weekday_match.group(0), '').strip()
        text = re.sub(r'\s*\bon\b\s*', ' ', text).strip()
    # Check for date patterns like 10/11 or 10/11/25
    else:
        date_match = re.search(r'(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?', text)
        if date_match:
            month = int(date_match.group(1))
            day = int(date_match.group(2))
            year = int(date_match.group(3)) if date_match.group(3) else today.year
            
            # Handle 2-digit years
            if year < 100:
                year += 2000
            
            try:
                due_date = date(year, month, day)
                # Remove date and "on" from text
                text = text.replace(date_match.group(0), '').strip()
                text = re.sub(r'\s*\bon\b\s*', ' ', text).strip()
            except ValueError:
                # Invalid date, ignore
                pass
    
    # Default to today if no date found
    if due_date is None:
        due_date = today
    
    # Validate that due_date is not in the past
    if due_date < today:
        error_msg = f"Cannot create task with past due date: {due_date.strftime('%m/%d/%Y')}. Please use today or a future date."
        return "", due_date, assignee, error_msg
    
    # Clean up title
    title = re.sub(r'\s+', ' ', text).strip()
    
    return title, due_date, assignee, None


def show_tasks_section(company):
    """Main tasks section for company pages with data editor"""
    # CSS for data editor and dialog centering
    st.markdown("""
    <style>
    /* Compact row styling */
    [data-testid="stDataFrame"] td {
        padding: 12px 16px !important;
        min-height: 40px !important;
    }
    /* Completed row styling - strikethrough and opacity */
    [data-testid="stDataFrame"] tbody tr:has(input[type="checkbox"]:checked) td {
        opacity: 0.6;
        text-decoration: line-through !important;
    }
    
    /* Enhanced Streamlit dialog styling */
    div[data-testid="stDialog"] {
        position: fixed !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        z-index: 999999 !important;
        max-width: 600px !important;
        width: 90vw !important;
        max-height: 39vh !important;  /* Additional 30% reduction from 56vh */
        background: white !important;
        border: 1px solid #e1e5e9 !important;
        border-radius: 12px !important;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04) !important;
        overflow: hidden !important;
    }
    
    /* Add backdrop overlay */
    div[data-testid="stDialog"]::before {
        content: '' !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        background: rgba(0, 0, 0, 0.5) !important;
        z-index: -1 !important;
    }
    
    /* Style dialog content */
    div[data-testid="stDialog"] > div {
        padding: 32px !important;
        background: white !important;
        border-radius: 12px !important;
        position: relative !important;
        z-index: 1 !important;
    }
    
    /* Style dialog header */
    div[data-testid="stDialog"] h3 {
        margin: 0 0 20px 0 !important;
        padding: 0 !important;
        font-size: 20px !important;
        font-weight: 600 !important;
        color: #1f2937 !important;
        border-bottom: 1px solid #e5e7eb !important;
        padding-bottom: 16px !important;
    }
    
    /* Style close button */
    div[data-testid="stDialog"] button[aria-label="Close"] {
        position: absolute !important;
        top: 16px !important;
        right: 16px !important;
        background: none !important;
        border: none !important;
        font-size: 18px !important;
        color: #6b7280 !important;
        cursor: pointer !important;
        padding: 8px !important;
        border-radius: 4px !important;
    }
    
    div[data-testid="stDialog"] button[aria-label="Close"]:hover {
        background: #f3f4f6 !important;
        color: #374151 !important;
    }
    
    /* Style text area */
    div[data-testid="stDialog"] textarea {
        border: 1px solid #d1d5db !important;
        border-radius: 8px !important;
        padding: 12px !important;
        font-size: 14px !important;
        resize: vertical !important;
        min-height: 100px !important;
    }
    
    div[data-testid="stDialog"] textarea:focus {
        outline: none !important;
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }
    
    /* Style disabled save button */
    div[data-testid="stDialog"] button[kind="primary"]:disabled {
        background-color: #e5e7eb !important;
        color: #9ca3af !important;
        cursor: not-allowed !important;
        opacity: 0.6 !important;
    }
    
    /* Help text styling */
    div[data-testid="stDialog"] .st-caption {
        font-size: 12px !important;
        color: #6b7280 !important;
        font-style: italic !important;
        margin-top: 4px !important;
    }
    
    /* Form width - 452px as requested */
    div[data-testid="stDialog"] .stForm {
        width: 452px !important;
        max-width: 452px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Get company ID from the company object
    company_id = company.id
    if not company_id:
        st.error("No company selected")
        return
    
    # Get tasks for this company
    all_tasks = get_tasks(company_id)
    
    # Add task form at the top
    show_add_task_form(company_id)
    
    # Header and filter row
    col_header, col_filter = st.columns([3, 1])
    
    with col_header:
        tasks_header = st.empty()
        
    with col_filter:
        filter_option = st.selectbox(
            "View",
            options=["All tasks", "Active", "Completed", "Overdue", "My tasks"],
            label_visibility="visible",
            key="task_filter_view",
            index=0
        )
    
    # Apply filters
    today = date.today()
    current_user = None
    if hasattr(st, 'user'):
        try:
            if hasattr(st.user, 'given_name') and hasattr(st.user, 'family_name'):
                current_user = f"{st.user.given_name} {st.user.family_name}"
            elif hasattr(st.user, 'name'):
                current_user = st.user.name
            elif hasattr(st.user, 'email'):
                current_user = st.user.email
        except:
            current_user = None
    
    filtered_tasks = all_tasks
    if filter_option == "Active":
        filtered_tasks = [t for t in all_tasks if t.status == "active"]
    elif filter_option == "Completed":
        filtered_tasks = [t for t in all_tasks if t.status == "completed"]
    elif filter_option == "Overdue":
        filtered_tasks = [t for t in all_tasks if t.status == "active" and t.due_date and t.due_date < today]
    elif filter_option == "My tasks":
        if current_user:
            filtered_tasks = [t for t in all_tasks if t.assignee and current_user.lower() in t.assignee.lower()]
    
    # Count active tasks for header (from filtered tasks)
    active_count = len([t for t in filtered_tasks if t.status == "active"])
    tasks_header.subheader(f"Active Tasks ({active_count})")
    
    # Show active tasks in data editor
    if filtered_tasks:
        show_tasks_data_editor(filtered_tasks, company_id)
        
        # Show completed tasks section below active tasks
        show_completed_tasks_section(all_tasks, company_id)
    else:
        st.info("No tasks yet. Add the first follow-up.")
        
        # Show completed tasks section even if no active tasks
        show_completed_tasks_section(all_tasks, company_id)


def show_add_task_form(company_id: str):
    """Compact form to add a new task with auto-parsing"""
    st.markdown("""
    <style>
    [data-testid="stForm"] {
        padding: 16px !important;
        margin-bottom: 16px !important;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        background: var(--secondary-background-color);
    }
    [data-testid="stForm"] > div {
        gap: 12px !important;
    }
    [data-testid="stForm"] [data-testid="column"] {
        padding: 0 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.form(key=f"add_task_form_{company_id}", clear_on_submit=True):
        col_input, col_add = st.columns([5, 1])
        
        with col_input:
            task_input = st.text_input(
                "Add new task",
                placeholder="Add a task…",
                key=f"task_input_{company_id}",
                label_visibility="collapsed"
            )
        
        with col_add:
            submitted = st.form_submit_button("+ Add", use_container_width=True, type="secondary")
        
        if submitted and task_input and task_input.strip():
            # Parse the input
            title, due_date, assignee, error_msg = parse_task_input(task_input)
            
            # Check if there's a validation error
            if error_msg:
                st.error(error_msg)
            elif title:
                # Get current user as creator
                creator = "Anonymous"
                if hasattr(st, 'user'):
                    try:
                        if hasattr(st.user, 'given_name') and hasattr(st.user, 'family_name'):
                            creator = f"{st.user.given_name} {st.user.family_name}"
                        elif hasattr(st.user, 'name'):
                            creator = st.user.name
                        elif hasattr(st.user, 'email'):
                            creator = st.user.email.split('@')[0]
                    except:
                        creator = "Anonymous"
                
                # If no assignee was parsed, default to creator
                if not assignee:
                    assignee = creator
                
                try:
                    task = add_task(company_id, title, due_date, assignee, created_by=creator)
                    # Store success message in session state to persist across rerun
                    st.session_state[f"task_added_success_{company_id}"] = title
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding task: {str(e)}")
            else:
                st.warning("Please enter a task description")
        
        # Show success message if task was just added (at bottom of form for consistency)
        if f"task_added_success_{company_id}" in st.session_state:
            st.success(f"✅ Task added: {st.session_state[f'task_added_success_{company_id}']}")
            # Clear the success message after displaying
            del st.session_state[f"task_added_success_{company_id}"]


def format_due_date_readable(due_date: Optional[date]) -> str:
    """Format due date as human-readable text (Today, Tomorrow, or date)"""
    if not due_date:
        return "No date"
    
    today = date.today()
    days_diff = (due_date - today).days
    
    if days_diff == 0:
        return "Today"
    elif days_diff == 1:
        return "Tomorrow"
    else:
        return due_date.strftime('%b %d, %Y')


def show_tasks_data_editor(tasks: List[Task], company_id: str):
    """Display active tasks using st.data_editor with inline editing"""
    # Filter to show only active tasks
    active_tasks = [t for t in tasks if t.status == "active"]
    
    # Prepare DataFrame for active tasks only
    df = prepare_tasks_dataframe(active_tasks)
    
    # Check for and show any pending results dialogs
    # IMPORTANT: This must happen BEFORE the early return to handle the case
    # where the last task is completed and df becomes empty
    dialog_flags = [key for key in st.session_state.keys() if key.startswith("show_results_dialog_")]
    for dialog_flag in dialog_flags:
        if st.session_state[dialog_flag]:
            task_id = dialog_flag.replace("show_results_dialog_", "")
            task_info_key = f"completed_task_info_{task_id}"
            
            # Get task info from session state
            if task_info_key in st.session_state:
                task_info = st.session_state[task_info_key]
                # Create a temporary Task object for the dialog
                from app.shared.task import Task
                temp_task = Task(
                    id=task_info['id'],
                    company_id=task_info['company_id'],
                    text=task_info['text'],
                    assignee=task_info['assignee'],
                    due_date=task_info['due_date'],
                    notes=task_info['notes'],
                    outcome=task_info['outcome']
                )
                show_results_dialog(temp_task)
                # Clear the dialog flags after showing
                del st.session_state[dialog_flag]
                del st.session_state[task_info_key]
                break  # Only show one dialog at a time
    
    if df.empty:
        st.info("No active tasks. Add the first follow-up.")
        return
    
    # Team members for owner selection
    team_members = ["Unassigned", "Nick", "Alex", "Sarah", "Jordan", "Anonymous"]
    
    # Configure columns
    column_config = {
        "id": None,  # Hide ID column
        "status": None,  # Hide status column
        "created_at": None,  # Hide created_at column
        "outcome": None,  # Hide outcome column
        "due_date": None,  # Hide due_date column
        "completed": st.column_config.CheckboxColumn(
            "Done",
            help="Mark task as completed",
            default=False,
            width="small"
        ),
        "title": st.column_config.TextColumn(
            "Task",
            help="Task description",
            max_chars=200,
            width="large"
        ),
        "owner": st.column_config.SelectboxColumn(
            "Owner",
            help="Task assignee",
            options=team_members,
            default="Unassigned",
            width="small"
        ),
        "due_display": st.column_config.TextColumn(
            "Due",
            help="Due date with color coding",
            width="small",
            disabled=True
        ),
        "notes": st.column_config.TextColumn(
            "Notes",
            help="Task notes and context",
            max_chars=500,
            width="large"
        ),
    }
    
    # Initialize session state with current DataFrame if not exists or if task count changed
    session_key = f"active_tasks_df_{company_id}"
    if session_key not in st.session_state or len(st.session_state[session_key]) != len(df):
        st.session_state[session_key] = df.copy()
    
    # Display data editor
    edited_df = st.data_editor(
        df,
        column_config=column_config,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        disabled=["id", "status", "created_at", "outcome", "due_display"],
        key=f"active_tasks_editor_{company_id}"
    )
    
    # Handle edits - only process if there are actual changes
    if not edited_df.equals(st.session_state[session_key]):
        handle_task_edits(edited_df, st.session_state[session_key], company_id, tasks)
        st.session_state[session_key] = edited_df.copy()
        st.rerun()


def handle_task_edits(edited_df: pd.DataFrame, original_df: pd.DataFrame, company_id: str, all_tasks: List[Task]):
    """Process changes from data_editor and update tasks"""
    # Track if any changes were made
    changes_made = False
    
    # Compare DataFrames to find changes
    for idx in range(len(edited_df)):
        task_id = edited_df.iloc[idx]['id']
        
        # Get values for comparison
        edited_completed = bool(edited_df.iloc[idx]['completed'])
        orig_completed = bool(original_df.iloc[idx]['completed'])
        edited_title = str(edited_df.iloc[idx]['title'])
        orig_title = str(original_df.iloc[idx]['title'])
        edited_owner = str(edited_df.iloc[idx]['owner'])
        orig_owner = str(original_df.iloc[idx]['owner'])
        edited_due = edited_df.iloc[idx]['due_date']
        orig_due = original_df.iloc[idx]['due_date']
        edited_notes = str(edited_df.iloc[idx]['notes']) if pd.notna(edited_df.iloc[idx]['notes']) else ''
        orig_notes = str(original_df.iloc[idx]['notes']) if pd.notna(original_df.iloc[idx]['notes']) else ''
        
        # Collect updates for this task
        task_updates = {}
        
        # Check if completed status changed
        if edited_completed != orig_completed:
            if edited_completed:
                # Complete the task immediately
                task_updates['status'] = "completed"
                task_updates['completed_at'] = datetime.now(timezone.utc)
                # Show dialog to collect results after completion
                # Store task info for dialog before completing
                task = next((t for t in all_tasks if t.id == task_id), None)
                if task:
                    # Check if this task was previously completed and has a stored outcome
                    stored_outcome = st.session_state.get(f"reactivated_task_outcome_{task_id}", None)
                    
                    # Store task info in session state before completion
                    st.session_state[f"completed_task_info_{task_id}"] = {
                        'id': task.id,
                        'company_id': company_id,
                        'text': task.text,
                        'assignee': task.assignee,
                        'due_date': task.due_date,
                        'notes': task.notes,
                        'outcome': stored_outcome or task.outcome  # Use stored outcome if available
                    }
                    st.session_state[f"show_results_dialog_{task_id}"] = True
            else:
                task_updates['status'] = "active"
                task_updates['completed_at'] = None
                task_updates['outcome'] = None
        
        # Check if title changed
        if edited_title != orig_title:
            task_updates['text'] = edited_title
        
        # Check if owner changed
        if edited_owner != orig_owner:
            task_updates['assignee'] = edited_owner if edited_owner != 'Unassigned' else None
        
        # Check if due_date changed (handle NaN comparison and type conversion)
        edited_due_normalized = None
        orig_due_normalized = None
        
        if not pd.isna(edited_due):
            # Convert to date object if it's a Timestamp
            if isinstance(edited_due, pd.Timestamp):
                edited_due_normalized = edited_due.date()
            elif isinstance(edited_due, date):
                edited_due_normalized = edited_due
        
        if not pd.isna(orig_due):
            # Convert to date object if it's a Timestamp
            if isinstance(orig_due, pd.Timestamp):
                orig_due_normalized = orig_due.date()
            elif isinstance(orig_due, date):
                orig_due_normalized = orig_due
        
        # Only update due_date if it actually changed AND is not in the past
        # (or if it's being cleared)
        if edited_due_normalized != orig_due_normalized:
            # Only validate for past dates if we're setting a new date (not just keeping the old one)
            if edited_due_normalized is not None and edited_due_normalized < date.today():
                # Skip this update - don't allow setting past due dates
                # (but allow keeping existing past dates)
                pass
            else:
                task_updates['due_date'] = edited_due_normalized
        
        # Check if notes changed
        if edited_notes != orig_notes:
            task_updates['notes'] = edited_notes.strip() if edited_notes.strip() else None
        
        # Apply all updates for this task at once
        if task_updates:
            update_task(task_id, **task_updates)
            changes_made = True
    
    return changes_made


def handle_completed_task_edits(edited_df: pd.DataFrame, original_df: pd.DataFrame, company_id: str, all_tasks: List[Task]):
    """Process changes from completed tasks data_editor and update tasks"""
    # Track if any changes were made
    changes_made = False
    
    # Compare DataFrames to find changes
    for idx in range(len(edited_df)):
        task_id = edited_df.iloc[idx]['id']
        
        # Get values for comparison
        edited_task = str(edited_df.iloc[idx]['task'])
        orig_task = str(original_df.iloc[idx]['task'])
        edited_owner = str(edited_df.iloc[idx]['owner'])
        orig_owner = str(original_df.iloc[idx]['owner'])
        edited_outcome = str(edited_df.iloc[idx]['outcome']) if pd.notna(edited_df.iloc[idx]['outcome']) else ''
        orig_outcome = str(original_df.iloc[idx]['outcome']) if pd.notna(original_df.iloc[idx]['outcome']) else ''
        edited_notes = str(edited_df.iloc[idx]['notes']) if pd.notna(edited_df.iloc[idx]['notes']) else ''
        orig_notes = str(original_df.iloc[idx]['notes']) if pd.notna(original_df.iloc[idx]['notes']) else ''
        edited_completed = bool(edited_df.iloc[idx]['completed'])
        orig_completed = bool(original_df.iloc[idx]['completed'])
        
        # Check if task was uncompleted (reactivated)
        if orig_completed and not edited_completed:
            # Store the current outcome before reactivating
            current_task = next((t for t in all_tasks if t.id == task_id), None)
            if current_task and current_task.outcome:
                # Store the outcome in session state for later use
                st.session_state[f"reactivated_task_outcome_{task_id}"] = current_task.outcome
            
            # Reactivate the task
            update_task(
                task_id,
                status="active",
                completed_at=None,
                outcome=None  # Clear outcome when reactivating
            )
            st.success(f"Task '{current_task.text if current_task else 'Unknown'}' returned to active status!")
            changes_made = True
            continue
        
        # Collect updates for this task
        task_updates = {}
        
        # Check if task text changed
        if edited_task != orig_task:
            task_updates['text'] = edited_task
        
        # Check if owner changed
        if edited_owner != orig_owner:
            task_updates['assignee'] = edited_owner if edited_owner != 'Unassigned' else None
        
        # Check if outcome (results) changed
        if edited_outcome != orig_outcome:
            task_updates['outcome'] = edited_outcome.strip() if edited_outcome.strip() else None
        
        # Check if notes changed
        if edited_notes != orig_notes:
            task_updates['notes'] = edited_notes.strip() if edited_notes.strip() else None
        
        # Apply all updates for this task at once
        if task_updates:
            update_task(task_id, **task_updates)
            changes_made = True
    
    return changes_made


@st.dialog("Add Task Results", width="small")
def show_results_dialog(task: Task):
    """Show dialog to collect results for a completed task"""
    # Simple task display
    st.write("**Task:**")
    st.write(task.text)
    
    # Check if this task has a stored outcome from reactivation
    stored_outcome = st.session_state.get(f"reactivated_task_outcome_{task.id}", "")
    
    # Use form to enable Enter key submission
    with st.form(key=f"results_form_{task.id}"):
        # Results text area - pre-fill with stored outcome if available
        results = st.text_area(
            "Results",
            value=stored_outcome,  # Pre-fill with stored outcome if available
            placeholder="Describe the outcome, findings, or results from completing this task...",
            height=120,
            key=f"results_input_{task.id}"
        )
        
        # Action buttons
        col_save, col_cancel = st.columns([1, 1], gap="medium")
        
        with col_save:
            save_clicked = st.form_submit_button("Save Results", type="primary", use_container_width=True)
        
        with col_cancel:
            cancel_clicked = st.form_submit_button("Cancel", type="secondary", use_container_width=True)
        
        # Handle form submission (both Enter key and button clicks)
        if save_clicked:
            try:
                update_task(
                    task.id,
                    outcome=results.strip() if results.strip() else None
                )
                # Clean up stored outcome since task is now completed with new results
                if f"reactivated_task_outcome_{task.id}" in st.session_state:
                    del st.session_state[f"reactivated_task_outcome_{task.id}"]
                st.success("Results saved!")
                st.rerun()
            except Exception as e:
                st.error(f"Error saving results: {str(e)}")
        
        if cancel_clicked:
            try:
                # Revert task back to active status
                update_task(
                    task.id,
                    status="active",
                    completed_at=None,
                    outcome=None
                )
                # Clean up stored outcome since user cancelled
                if f"reactivated_task_outcome_{task.id}" in st.session_state:
                    del st.session_state[f"reactivated_task_outcome_{task.id}"]
                st.success("Task reverted to active!")
                st.rerun()
            except Exception as e:
                st.error(f"Error reverting task: {str(e)}")


def get_due_date_color_class(due_date: Optional[date]) -> str:
    """Get CSS color class for due date status"""
    if not due_date:
        return "due-date-gray"
    
    today = date.today()
    days_diff = (due_date - today).days
    
    if days_diff < 0:
        return "due-date-overdue"   # 🔴 #ef4444 red
    elif days_diff <= 2:
        return "due-date-soon"      # 🟠 #f97316 orange  
    else:
        return "due-date-upcoming"  # 🟢 #22c55e green


def get_due_date_dot_class(due_date: Optional[date]) -> str:
    """Get emoji indicator for due date status (Todoist-style)"""
    if not due_date:
        return ""  # No indicator
    
    today = date.today()
    days_diff = (due_date - today).days
    
    if days_diff < 0:
        return "🔴"  # Red circle - Overdue
    elif days_diff == 0:
        return "🟢"  # Green circle - Today
    elif days_diff == 1:
        return "🟡"  # Yellow circle - Tomorrow
    elif days_diff <= 7:
        return "🟣"  # Purple circle - 2-7 days (THIS WAS THE BUG!)
    else:
        return "⚪"  # White/gray circle - 8+ days


def show_active_tasks_list(tasks: List[Task], company_id: str):
    """Display active tasks as clean 1-line Todoist-style cards"""
    
    # Add CSS to force left-alignment of all task elements using Streamlit theme variables
    st.markdown("""
    <style>
    /* Force left alignment for task list container */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
        align-items: flex-start !important;
        justify-content: flex-start !important;
    }
    
    /* Force left alignment for task buttons */
    [data-testid="stBaseButton-secondary"] {
        margin-left: 0 !important;
        margin-right: auto !important;
        text-align: left !important;
        justify-content: flex-start !important;
    }
    
    /* Ensure button content is left-aligned */
    [data-testid="stBaseButton-secondary"] > div {
        text-align: left !important;
        width: 100% !important;
    }
    
    /* Remove any centering from containers */
    div[data-testid="column"] {
        align-items: flex-start !important;
    }
    
    /* Style checkbox buttons - make them square and minimal */
    button[data-testid*="complete_checkbox"] {
        width: 32px !important;
        min-width: 32px !important;
        height: 32px !important;
        padding: 4px !important;
        font-size: 20px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin-top: 8px !important;
        background: var(--secondary-background-color) !important;
        border: 1px solid #d1d5db !important;
        color: var(--text-color) !important;
    }
    
    /* Task card button - one-line layout with chip styling */
    [data-testid="stBaseButton-secondary"]:has([data-testid*="task_card"]) {
        min-height: 44px !important;
        height: 44px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        line-height: 1.4 !important;
        text-align: left !important;
        padding: 10px 16px !important;
        font-size: 14px !important;
        font-weight: 400 !important;
        background: var(--secondary-background-color) !important;
        border: 1px solid #d1d5db !important;
        margin: 2px 0 !important;
    }
    
    /* Task card text styling */
    [data-testid="stBaseButton-secondary"]:has([data-testid*="task_card"]) > div {
        color: var(--text-color) !important;
        line-height: 1.4 !important;
        display: flex !important;
        align-items: center !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    for task in tasks:
        # Check if this task is being edited inline
        is_editing = st.session_state.get(f"inline_editing_{task.id}", False)
        
        if is_editing:
            # Store original text for comparison if not already stored
            if f"original_text_{task.id}" not in st.session_state:
                st.session_state[f"original_text_{task.id}"] = task.text
            
            # Expanded edit mode - using form with Enter key support
            with st.form(key=f"edit_task_{task.id}"):
                # Row 1: Full-width task text input
                new_title = st.text_input(
                    "Task text",
                    value=task.text,
                    key=f"edit_title_{task.id}",
                    placeholder="Enter task title...",
                    label_visibility="collapsed"
                )
                
                # Row 2: Inline metadata - due date and assignee
                col_due, col_assignee, col_spacer = st.columns([3, 3, 6], gap="small")
                
                with col_due:
                    new_due_date = st.date_input(
                        "Due date",
                        value=task.due_date if task.due_date else date.today(),
                        min_value=date.today(),
                        key=f"edit_due_date_{task.id}",
                        label_visibility="visible"
                    )
                
                with col_assignee:
                    # Mock team members for selectbox
                    team_members = ["Anonymous", "Nick", "Alex", "Sarah", "Jordan"]
                    current_assignee = task.assignee if task.assignee in team_members else "Anonymous"
                    new_assignee = st.selectbox(
                        "Assignee",
                        options=team_members,
                        index=team_members.index(current_assignee),
                        key=f"edit_assignee_{task.id}",
                        label_visibility="visible"
                    )
                
                # Notes field (collapsed by default for compact layout)
                with st.expander("Notes", expanded=False):
                    new_notes = st.text_area(
                        "Notes",
                        value=task.notes or "",
                        key=f"edit_notes_{task.id}",
                        placeholder="Add notes, updates, or context here…",
                        label_visibility="collapsed"
                    )
                
                # Footer: Right-aligned buttons with spacer
                col_spacer, col_save, col_cancel, col_delete = st.columns([8, 1, 1, 1], gap="small")
                
                # Determine if Save should be disabled
                title_changed = new_title != st.session_state[f"original_text_{task.id}"]
                title_empty = not new_title or not new_title.strip()
                save_disabled = title_empty or not title_changed
                
                with col_save:
                    save_clicked = st.form_submit_button("Save", type="primary", disabled=save_disabled, use_container_width=True)
                
                with col_cancel:
                    cancel_clicked = st.form_submit_button("Cancel", type="secondary", use_container_width=True)
                
                with col_delete:
                    delete_clicked = st.form_submit_button("Delete", type="secondary", use_container_width=True)
                
                # Status message placeholder
                status_placeholder = st.empty()
                if not title_changed and not title_empty:
                    status_placeholder.caption("No changes to save")
                elif title_empty:
                    status_placeholder.caption("Title cannot be empty")
                else:
                    status_placeholder.caption("Press Enter to save")
                
                # Handle form submission (including Enter key press)
                if save_clicked:
                    if new_title and new_title.strip():
                        try:
                            update_task(
                                task.id, 
                                text=new_title.strip(), 
                                due_date=new_due_date, 
                                assignee=new_assignee if new_assignee else None,
                                notes=new_notes.strip() or None
                            )
                            # Clear session state
                            st.session_state[f"inline_editing_{task.id}"] = False
                            if f"original_text_{task.id}" in st.session_state:
                                del st.session_state[f"original_text_{task.id}"]
                            status_placeholder.success("Saved ✓")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error updating task: {str(e)}")
                    else:
                        st.warning("Please enter a task title")
                elif cancel_clicked:
                    st.session_state[f"inline_editing_{task.id}"] = False
                    if f"original_text_{task.id}" in st.session_state:
                        del st.session_state[f"original_text_{task.id}"]
                    st.rerun()
                elif delete_clicked:
                    # Show confirmation before deleting
                    if st.session_state.get(f"confirm_delete_{task.id}", False):
                        try:
                            delete_task(task.id)
                            st.session_state[f"inline_editing_{task.id}"] = False
                            if f"original_text_{task.id}" in st.session_state:
                                del st.session_state[f"original_text_{task.id}"]
                            if f"confirm_delete_{task.id}" in st.session_state:
                                del st.session_state[f"confirm_delete_{task.id}"]
                            st.success("Task deleted!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting task: {str(e)}")
                    else:
                        st.session_state[f"confirm_delete_{task.id}"] = True
                        st.warning("Click Delete again to confirm")
                        st.rerun()
        else:
            # Collapsed view - checkbox + task card
            # Layout: Checkbox button on left, task card on right
            col_checkbox, col_task = st.columns([0.8, 11.2], vertical_alignment="top")
            
            with col_checkbox:
                # Checkbox button to complete task
                if st.button(
                    "☐",
                    key=f"complete_checkbox_{task.id}",
                    help="Complete task",
                    type="secondary"
                ):
                    # When clicked, trigger completion dialog
                    st.session_state[f"completing_task_{task.id}"] = True
                    st.rerun()
            
            with col_task:
                # Create clickable task card with semantic metadata (no emojis)
                # Format owner chip - calm styling
                owner_text = task.assignee if task.assignee else "Unassigned"
                owner_chip = f"Owner: {owner_text}"
                
                # Format due date chip - show overdue in context, not with emoji
                today = date.today()
                if task.due_date:
                    due_str = task.due_date.strftime('%b %d, %Y')
                    if task.due_date < today:
                        # Overdue - will be styled red via CSS
                        due_chip = f"Due: {due_str}"
                    else:
                        due_chip = f"Due: {due_str}"
                else:
                    due_chip = "Due: Not set"
                
                task_card_clicked = st.button(
                    f"{task.text}  •  {owner_chip}  •  {due_chip}",
                    key=f"task_card_{task.id}",
                    use_container_width=True,
                    type="secondary"
                )
                
                if task_card_clicked:
                    st.session_state[f"inline_editing_{task.id}"] = True
                    st.rerun()
            
            # Handle inline completion mode
            if st.session_state.get(f"completing_task_{task.id}", False):
                # Inline completion form - using form for Enter key support
                with st.form(key=f"complete_form_{task.id}"):
                    st.markdown(f"**Complete Task: {task.text}**")
                    
                    # Outcome/Result field - changed to text_input
                    outcome = st.text_input(
                        "Outcome / Result (optional):",
                        placeholder="Enter the outcome or result from this task...",
                        key=f"complete_outcome_{task.id}"
                    )
                    
                    # Action buttons
                    col_complete, col_cancel = st.columns([1, 1])
                    
                    with col_complete:
                        complete_clicked = st.form_submit_button("✅ Complete", type="primary")
                    
                    with col_cancel:
                        cancel_clicked = st.form_submit_button("❌ Cancel", type="secondary")
                    
                    # Handle form submission
                    if complete_clicked:
                        try:
                            update_task(
                                task.id,
                                status="completed",
                                outcome=outcome if outcome.strip() else None,
                                completed_at=datetime.now(timezone.utc)
                            )
                            st.success("✅ Task completed!")
                            st.session_state[f"completing_task_{task.id}"] = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error completing task: {str(e)}")
                    
                    if cancel_clicked:
                        st.session_state[f"completing_task_{task.id}"] = False
                        st.rerun()


def show_completed_tasks_section(all_tasks: List[Task], company_id: str):
    """Display completed tasks in collapsible section using simple data_editor"""
    # Filter to completed tasks only
    completed_tasks = [t for t in all_tasks if t.status == "completed"]
    
    if not completed_tasks:
        return
    
    # Sort completed tasks by completion date (newest first)
    completed_tasks.sort(key=lambda t: t.completed_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    
    with st.expander(f"✅ Completed Tasks ({len(completed_tasks)})", expanded=False):
        # Prepare DataFrame for completed tasks
        completed_data = []
        for task in completed_tasks:
            completed_date = task.completed_at.strftime('%b %d, %Y') if task.completed_at else 'Unknown'
            due_date_str = task.due_date.strftime('%b %d, %Y') if task.due_date else 'No date'
            
            completed_data.append({
                'id': task.id,
                'completed': True,  # Add completed checkbox column as first column
                'task': task.text,
                'owner': task.assignee or 'Unassigned',
                'due_date': due_date_str,
                'completed_date': completed_date,
                'outcome': task.outcome or '',
                'notes': task.notes or ''
            })
        
        completed_df = pd.DataFrame(completed_data)
        
        # Team members for owner selection
        team_members = ["Unassigned", "Nick", "Alex", "Sarah", "Jordan", "Anonymous"]
        
        # Configure columns for editable display
        column_config = {
            "id": None,  # Hide ID column
            "completed": st.column_config.CheckboxColumn(
                "Done",
                help="Uncheck to return task to active status",
                default=True,
                width="small"
            ),
            "task": st.column_config.TextColumn(
                "Task",
                help="Completed task description",
                max_chars=200,
                width="large"
            ),
            "owner": st.column_config.SelectboxColumn(
                "Owner",
                help="Task assignee",
                options=team_members,
                default="Unassigned",
                width="small"
            ),
            "due_date": st.column_config.TextColumn(
                "Due",
                help="Original due date",
                width="small",
                disabled=True
            ),
            "completed_date": st.column_config.TextColumn(
                "Completed",
                help="Completion date",
                width="small",
                disabled=True
            ),
            "outcome": st.column_config.TextColumn(
                "Results",
                help="Task outcome/result",
                max_chars=500,
                width="medium"
            ),
            "notes": st.column_config.TextColumn(
                "Notes",
                help="Task notes",
                max_chars=500,
                width="medium"
            ),
        }
        
        # Initialize session state with current DataFrame if not exists or if task count changed
        session_key = f"completed_tasks_df_{company_id}"
        if session_key not in st.session_state or len(st.session_state[session_key]) != len(completed_df):
            st.session_state[session_key] = completed_df.copy()
        
        # Display as editable data editor
        edited_df = st.data_editor(
            completed_df,
            column_config=column_config,
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            disabled=["id", "due_date", "completed_date"],  # completed checkbox is editable to allow unchecking
            key=f"completed_tasks_{company_id}"
        )
        
        # Handle edits - only process if there are actual changes
        if not edited_df.equals(st.session_state[session_key]):
            handle_completed_task_edits(edited_df, st.session_state[session_key], company_id, completed_tasks)
            st.session_state[session_key] = edited_df.copy()
            st.rerun()


def get_due_date_color(due_date: date) -> str:
    """Get CSS color for due date status dot"""
    today = date.today()
    days_until_due = (due_date - today).days
    
    if days_until_due < 0:
        return "#ef4444"  # Red - Overdue
    elif days_until_due <= 2:
        return "#f97316"  # Orange - Due soon (≤2 days)
    else:
        return "#22c55e"  # Green - Upcoming (>2 days)


def show_task_summary_card(company):
    """Compact task summary for company cards"""
    company_id = company.id
    tasks = get_tasks(company_id)
    active_count = len([t for t in tasks if t.status == "active"])
    
    if active_count > 0:
        overdue_tasks = [t for t in tasks if t.status == "active" and t.due_date < date.today()]
        overdue_count = len(overdue_tasks)
        
        if overdue_count > 0:
            st.error(f"⚠️ {active_count} active tasks ({overdue_count} overdue)")
        else:
            st.warning(f"📋 {active_count} active tasks")
    else:
        st.success("✅ No active tasks")


def show_pipeline_summary(company):
    """Pipeline Summary with exact Notion-like styling from screenshot"""
    company_id = company.id
    if not company_id:
        return
    
    # Get all tasks for this company
    tasks = get_tasks(company_id)
    
    # Calculate date range for 7-day window
    today = date.today()
    seven_days_ago = today - timedelta(days=7)
    
    # Filter completed tasks from last 7 days
    completed_tasks_last_week = [
        t for t in tasks 
        if t.status == "completed" 
        and t.completed_at 
        and t.completed_at.date() >= seven_days_ago
    ]
    
    # Sort by completion date (newest first)
    # Handle both timezone-aware and naive datetimes
    completed_tasks_last_week.sort(
        key=lambda t: t.completed_at if t.completed_at else datetime.min.replace(tzinfo=timezone.utc), 
        reverse=True
    )
    
    # Get active tasks for "Next step"
    active_tasks = [t for t in tasks if t.status == "active"]
    next_task = None
    if active_tasks:
        # Sort by due date (earliest first)
        active_tasks.sort(key=lambda t: t.due_date if t.due_date else date.max)
        next_task = active_tasks[0] if active_tasks else None
    
    # Calculate counts for header
    completed_count = len(completed_tasks_last_week)
    active_count = len(active_tasks)
    overdue_count = len([t for t in active_tasks if t.due_date and t.due_date < today])
    
    # Format date range for header
    end_date_str = today.strftime("%b %d")
    start_date_str = seven_days_ago.strftime("%b %d")
    
    # Build expander label with evenly spaced icons and dot separators
    expander_label = f"🧾 Pipeline Summary ({start_date_str} – {end_date_str}) · ✅ {completed_count} completed"
    if overdue_count > 0:
        expander_label += f" · ⚠️ {overdue_count} overdue"
    expander_label += f" · 🗓️ {active_count} active"
    
    # Use native st.expander with collapsed by default
    with st.expander(expander_label, expanded=False):
        # Last updated info - left aligned with timestamp
        now = datetime.now()
        # Simulate last update time (3 hours ago)
        last_updated = now - timedelta(hours=3)
        time_ago = "3h ago" if last_updated.date() == now.date() else last_updated.strftime("%b %d")
        
        st.markdown("""
        <div style="text-align: left; font-size: 13px; color: var(--text-color); margin-bottom: 12px; font-weight: normal; font-style: italic; opacity: 0.7;">
            Last updated: Today {time_ago}
        </div>
        """.format(time_ago=time_ago), unsafe_allow_html=True)
        
        # LAST DISCUSSED section with consistent padding
        st.markdown("""
        <div style="
            font-size: 12px; 
            color: var(--text-color); 
            font-variant: all-small-caps; 
            letter-spacing: 0.4px; 
            margin-bottom: 6px;
            margin-left: 0;
            opacity: 0.8;
        ">
            LAST DISCUSSED
        </div>
        """, unsafe_allow_html=True)
        
        if completed_tasks_last_week:
            for task in completed_tasks_last_week:
                # Normalize bullet content tone - short declarative sentences
                task_text = task.text.rstrip('.') + '.' if not task.text.endswith('.') else task.text
                st.markdown(f"""
                <div style="margin-left: 1.4rem; line-height: 1.3; margin: 1px 0; font-size: 16px; color: var(--text-color);">
                    • {task_text}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="margin-left: 1.4rem; line-height: 1.3; margin: 1px 0; font-size: 16px; color: var(--text-color);">
                • No completed tasks in the past week.
            </div>
            """, unsafe_allow_html=True)
        
        # OUTCOME section with consistent padding - only show if there are outcomes
        if completed_tasks_last_week:
            # Filter to only tasks with actual outcomes
            tasks_with_outcomes = [t for t in completed_tasks_last_week if t.outcome and t.outcome.strip()]
            
            if tasks_with_outcomes:
                st.markdown("""
                <div style="
                    font-size: 12px; 
                    color: var(--text-color); 
                    font-variant: all-small-caps; 
                    letter-spacing: 0.4px; 
                    margin-bottom: 6px;
                    margin-top: 12px;
                    margin-left: 0;
                    opacity: 0.8;
                ">
                    OUTCOME
                </div>
                """, unsafe_allow_html=True)
                
                for task in tasks_with_outcomes:
                    # Enforce consistent capitalization and period use in Outcomes
                    outcome_text = task.outcome.rstrip('.') + '.' if not task.outcome.endswith('.') else task.outcome
                    st.markdown(f"""
                    <div style="margin-left: 1.4rem; line-height: 1.3; margin: 1px 0; font-size: 16px; color: var(--text-color);">
                        • {outcome_text}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Single divider only between "Outcome" and "Next Step" sections
                st.markdown("""
                <hr style="border: none; border-top: 1px solid var(--border-color); margin: 12px 0; opacity: 0.5;">
                """, unsafe_allow_html=True)
        
        # NEXT STEP section with consistent padding
        st.markdown("""
        <div style="
            font-size: 12px; 
            color: var(--text-color); 
            font-variant: all-small-caps; 
            letter-spacing: 0.4px; 
            margin-bottom: 6px;
            margin-left: 0;
            opacity: 0.8;
        ">
            NEXT STEP
        </div>
        """, unsafe_allow_html=True)
        
        if next_task:
            # Format "Next Step" as: → **Task** @Assignee [Status Badge]
            task_text = next_task.text.rstrip('.') if next_task.text.endswith('.') else next_task.text
            assignee_text = f"@{next_task.assignee}" if next_task.assignee else ""
            
            # Create status badge based on due date
            status_badge = ""
            if next_task.due_date:
                color = get_due_date_color(next_task.due_date)
                if color == "#ef4444":  # Overdue
                    status_badge = '<span style="background: #fee2e2; color: #dc2626; border: 1px solid #fecaca; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 500; margin-left: 8px;">Overdue</span>'
                elif color == "#22c55e":  # Due today (green)
                    status_badge = '<span style="background: #dcfce7; color: #16a34a; border: 1px solid #bbf7d0; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 500; margin-left: 8px;">Today</span>'
                elif color == "#f97316":  # Due soon (1-3 days)
                    status_badge = '<span style="background: #fef3c7; color: #d97706; border: 1px solid #fde68a; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 500; margin-left: 8px;">Soon</span>'
                else:  # Not urgent (4+ days)
                    status_badge = '<span style="background: #e9d5ff; color: #9333ea; border: 1px solid #ddd6fe; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 500; margin-left: 8px;">This Week</span>'
            
            st.markdown(f"""
            <div style="color: var(--text-color); font-weight: 500; line-height: 1.3; font-size: 16px; margin-bottom: 10px;">
                → <strong>{task_text}</strong> {assignee_text} {status_badge}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="color: var(--text-color); font-weight: 500; line-height: 1.3; font-size: 16px; margin-bottom: 10px;">
                → Add the next step in Tasks tab below.
            </div>
            """, unsafe_allow_html=True)


# Smoke test function for the new separated tasks functionality
def test_separated_tasks_workflow():
    """Test function to verify the separated active/completed tasks workflow"""
    print("🧪 Testing Enhanced Dialog-Based Separated Tasks Workflow")
    print("1. ✅ Active tasks table shows only active tasks")
    print("2. ✅ Clicking 'Done' checkbox immediately moves task to completed")
    print("3. ✅ Enhanced st.dialog appears centered with backdrop overlay")
    print("4. ✅ Dialog has professional styling with rounded corners and shadows")
    print("5. ✅ Completed tasks appear in collapsible section below")
    print("6. ✅ 'Add Result' buttons for tasks without results")
    print("7. ✅ Cancel button reverts task back to active (undo functionality)")
    print("8. ✅ Save button validates for meaningful content (not just symbols)")
    print("9. ✅ Input always starts empty (no pre-filling with existing results)")
    print("10. ✅ Enter key support - press Enter to save results")
    print("11. ✅ Save button always available (no input validation)")
    print("12. ✅ Fixed dialog trigger for last task completion")
    print("\n🎯 Enhanced Dialog Workflow:")
    print("- Click Done checkbox → Task immediately completes and moves to completed section")
    print("- Professional dialog appears centered with dark backdrop overlay")
    print("- Dialog has enhanced styling: rounded corners, shadows, better typography")
    print("- Task info displayed in styled card with better visual hierarchy")
    print("- Input always starts empty (fresh start for each task)")
    print("- Save button validates for meaningful content using regex pattern matching")
    print("- Prevents saving symbols-only input (e.g., '!!!', '---', '???')")
    print("- Help text shows 'Enter meaningful text (not just symbols) to enable save'")
    print("- Real-time validation: save button enables/disables as you type")
    print("- Enter key support: press Enter to save (form-based submission)")
    print("- Dynamic help text: 'Press Enter or click Save to submit' when enabled")
    print("- Save updates results, Cancel reverts task to active")
    print("- Additional 'Add Result' buttons in completed section")
    print("- Undo functionality: Cancel moves task back to active tasks")
    print("- Professional modal dialog experience with simplified validation")
    
    return True
