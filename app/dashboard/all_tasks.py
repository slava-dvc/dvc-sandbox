"""
All Tasks UI components for the DVC Portfolio Dashboard
Shows tasks from all companies with company name column and "My tasks" default filter
"""
import streamlit as st
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional, Tuple, Dict
import pandas as pd
from app.shared.task import Task
from app.shared.task_config import is_active_status, is_completed_status
from app.dashboard.data import get_all_tasks, update_task, delete_task, get_companies_v2
from app.dashboard.dialog_utils import show_task_results_dialog
from app.dashboard.tasks import get_current_user_for_tasks


def get_company_name_lookup() -> Dict[str, str]:
    """Get a lookup dictionary mapping company_id to company_name"""
    try:
        companies = get_companies_v2(query={}, projection=['name', 'id'])
        return {company.id: company.name for company in companies}
    except Exception as e:
        st.error(f"Error fetching company names: {str(e)}")
        return {}


def prepare_all_tasks_dataframe(tasks: List[Task]) -> pd.DataFrame:
    """
    Convert Task objects to a pandas DataFrame for st.data_editor with company names
    Sort order: completed ASC, due_date NULLS LAST ASC, created_at DESC
    """
    if not tasks:
        return pd.DataFrame(columns=['id', 'completed', 'title', 'company_name', 'owner', 'due_date', 'due_display', 'status', 'created_at', 'notes', 'outcome'])
    
    # Get company name lookup
    company_lookup = get_company_name_lookup()
    
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
        
        # Get company name from lookup
        company_name = company_lookup.get(task.company_id, "Unknown Company")
        
        data.append({
            'id': task.id,
            'completed': task.status == 'completed',
            'title': task.text,
            'company_name': company_name,
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


def get_current_user() -> Optional[str]:
    """Get current user name using same logic as tasks.py"""
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


def show_all_tasks_data_editor(tasks: List[Task]):
    """Display all tasks using st.data_editor with inline editing and company names"""
    # Filter to show only active tasks (including pending_result)
    active_tasks = [t for t in tasks if is_active_status(t.status)]
    
    # Prepare DataFrame for active tasks only
    df = prepare_all_tasks_dataframe(active_tasks)
    
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
                temp_task = Task(
                    id=task_info['id'],
                    company_id=task_info['company_id'],
                    text=task_info['text'],
                    assignee=task_info['assignee'],
                    due_date=task_info['due_date'],
                    notes=task_info['notes'],
                    outcome=task_info['outcome']
                )
                show_task_results_dialog(temp_task)
                # Clear the dialog flags after showing
                del st.session_state[dialog_flag]
                del st.session_state[task_info_key]
                break  # Only show one dialog at a time
    
    if df.empty:
        st.info("No active tasks. Tasks will appear here when added from company pages.")
        return
    
    # Team members for owner selection
    team_members = ["Unassigned", "Marina", "Nick", "Mel", "Charles", "Alexey", "Tony", "Elena", "Vlad", "Slava"]
    
    # Configure columns
    column_config = {
        "id": None,  # Hide ID column
        "status": None,  # Hide status column
        "created_at": None,  # Hide created_at column
        "outcome": None,  # Hide outcome column
        "completed": st.column_config.CheckboxColumn(
            "Done",
            help="Mark task as completed",
            default=False
        ),
        "title": st.column_config.TextColumn(
            "Task",
            help="Task description",
            max_chars=200
        ),
        "company_name": st.column_config.TextColumn(
            "Company",
            help="Company this task belongs to",
            disabled=True
        ),
        "owner": st.column_config.SelectboxColumn(
            "Owner",
            help="Task assignee",
            options=team_members,
            default="Unassigned"
        ),
        "due_date": st.column_config.DateColumn(
            "Due",
            help="Due date - click to edit",
            min_value=date.today(),
            format="MMM DD, YYYY"
        ),
        "due_display": None,  # Hide status column
        "notes": st.column_config.TextColumn(
            "Notes",
            help="Task notes and context",
            max_chars=500
        ),
    }
    
    # Initialize session state with current DataFrame if not exists or if task count changed
    session_key = "all_tasks_df"
    if session_key not in st.session_state or len(st.session_state[session_key]) != len(df):
        st.session_state[session_key] = df.copy()
    
    # Display data editor
    edited_df = st.data_editor(
        df,
        column_config=column_config,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        disabled=["id", "status", "created_at", "outcome", "company_name"],
        key="all_tasks_editor"
    )
    
    # Handle edits - only process if there are actual changes
    if not edited_df.equals(st.session_state[session_key]):
        handle_task_edits(edited_df, st.session_state[session_key], tasks)
        st.session_state[session_key] = edited_df.copy()
        st.rerun()


def handle_task_edits(edited_df: pd.DataFrame, original_df: pd.DataFrame, all_tasks: List[Task]):
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
                # Check if quick complete is enabled
                if st.session_state.get("allow_quick_complete", False):
                    # Complete immediately without dialog
                    task_updates['status'] = "completed"
                    task_updates['completed_at'] = datetime.now(timezone.utc)
                    task_updates['outcome'] = "Completed without detailed results"
                    # Get current user for completed_by
                    current_user = get_current_user_for_tasks() or "Anonymous"
                    task_updates['completed_by'] = current_user
                else:
                    # Set to pending_result and show dialog
                    task_updates['status'] = "pending_result"
                    
                    # Store task info in session state for dialog
                    task = next((t for t in all_tasks if t.id == task_id), None)
                    if task:
                        # Check if this task was previously completed and has a stored outcome
                        stored_outcome = st.session_state.get(f"reactivated_task_outcome_{task_id}", None)
                        
                        # Store task info in session state before completion
                        st.session_state[f"completed_task_info_{task_id}"] = {
                            'id': task.id,
                            'company_id': task.company_id,
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


def handle_completed_task_edits(edited_df: pd.DataFrame, original_df: pd.DataFrame, all_tasks: List[Task]):
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


# OLD DIALOG - COMMENTED OUT - REPLACED BY UNIFIED DIALOG IN dialog_utils.py
# @st.dialog("Add Task Results")
# def show_results_dialog(task: Task):
#     """Refactored dialog with minimal CSS and better state management"""
#     
#     # Minimal, focused CSS - only what's absolutely necessary
#     st.markdown("""
#     <style>
#     /* Only essential dialog styling - no conflicts */
#     .stDialog > div {
#         width: min(600px, 90vw) !important;
#         max-height: 80vh !important;
#         overflow-y: auto !important;
#     }
#     
#     .stDialog textarea {
#         width: 100% !important;
#         min-height: 120px !important;
#         resize: vertical !important;
#     }
#     
#     @media (max-width: 768px) {
#         .stDialog > div {
#             width: 95vw !important;
#             margin: 20px !important;
#         }
#     }
#     </style>
#     """, unsafe_allow_html=True)
#     
#     # Simplified content structure
#     st.markdown("### Add Task Results")
#     
#     # Task display
#     with st.container():
#         st.markdown(f"**Task:** {task.text}")
#     
#     st.markdown("---")
#     
#     # Check if this task has a stored outcome from reactivation
#     stored_outcome = st.session_state.get(f"reactivated_task_outcome_{task.id}", "")
#     
#     # Results form with better state management
#     import time
#     form_key = f"results_form_{task.id}_{int(time.time())}"  # Unique key
#     
#     with st.form(key=form_key, clear_on_submit=False):
#         results = st.text_area(
#             "Results",
#             placeholder="Describe the outcome, findings, or results from completing this task...",
#             height=150,
#             help="Enter detailed results or findings from completing this task"
#         )
#         
#         # Action buttons in a single row
#         col1, col2, col3 = st.columns([1, 1, 1])
#         
#         with col1:
#             save_clicked = st.form_submit_button("💾 Save", type="primary", use_container_width=True)
#         
#         with col2:
#             cancel_clicked = st.form_submit_button("❌ Cancel", use_container_width=True)
#         
#         with col3:
#             # Empty column for spacing
#             pass
#         
#         # Handle form submission with better error handling
#         if save_clicked:
#             if results and results.strip():
#                 try:
#                     update_task(
#                         task.id,
#                         status="completed",
#                         completed_at=datetime.now(timezone.utc),
#                         outcome=results.strip()
#                     )
#                     # Clean up stored outcome since task is now completed with new results
#                     if f"reactivated_task_outcome_{task.id}" in st.session_state:
#                         del st.session_state[f"reactivated_task_outcome_{task.id}"]
#                     st.success("✅ Results saved successfully!")
#                     time.sleep(1)  # Brief success message
#                     st.rerun()
#                 except Exception as e:
#                     st.error(f"❌ Error saving results: {str(e)}")
#             else:
#                 st.warning("⚠️ Please provide meaningful results before saving")
#         
#         if cancel_clicked:
#             try:
#                 update_task(
#                     task.id,
#                     status="active",
#                     completed_at=None,
#                     outcome=None
#                 )
#                 # Clean up stored outcome since user cancelled
#                 if f"reactivated_task_outcome_{task.id}" in st.session_state:
#                     del st.session_state[f"reactivated_task_outcome_{task.id}"]
#                 st.info("ℹ️ Task reverted to active status")
#                 time.sleep(1)
#                 st.rerun()
#             except Exception as e:
#                 st.error(f"❌ Error reverting task: {str(e)}")


def show_completed_tasks_section(all_tasks: List[Task]):
    """Display completed tasks in collapsible section using simple data_editor"""
    # Filter to completed tasks only
    completed_tasks = [t for t in all_tasks if t.status == "completed"]
    
    if not completed_tasks:
        return
    
    # Sort completed tasks by completion date (newest first)
    completed_tasks.sort(key=lambda t: t.completed_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    
    with st.expander(f"✅ Completed Tasks ({len(completed_tasks)})", expanded=False):
        # Get company name lookup
        company_lookup = get_company_name_lookup()
        
        # Prepare DataFrame for completed tasks
        completed_data = []
        for task in completed_tasks:
            completed_date = task.completed_at.strftime('%b %d, %Y') if task.completed_at else 'Unknown'
            due_date_str = task.due_date.strftime('%b %d, %Y') if task.due_date else 'No date'
            company_name = company_lookup.get(task.company_id, "Unknown Company")
            
            completed_data.append({
                'id': task.id,
                'completed': True,  # Add completed checkbox column as first column
                'task': task.text,
                'company_name': company_name,
                'owner': task.assignee or 'Unassigned',
                'due_date': due_date_str,
                'completed_date': completed_date,
                'outcome': task.outcome or '',
                'notes': task.notes or ''
            })
        
        completed_df = pd.DataFrame(completed_data)
        
        # Team members for owner selection
        team_members = ["Unassigned", "Marina", "Nick", "Mel", "Charles", "Alexey", "Tony", "Elena", "Vlad", "Slava"]
        
        # Configure columns for editable display
        column_config = {
            "id": None,  # Hide ID column
            "completed": st.column_config.CheckboxColumn(
                "Done",
                help="Uncheck to return task to active status",
                default=True
            ),
            "task": st.column_config.TextColumn(
                "Task",
                help="Completed task description",
                max_chars=200
            ),
            "company_name": st.column_config.TextColumn(
                "Company",
                help="Company this task belongs to",
                disabled=True
            ),
            "owner": st.column_config.SelectboxColumn(
                "Owner",
                help="Task assignee",
                options=team_members,
                default="Unassigned"
            ),
            "due_date": st.column_config.TextColumn(
                "Due",
                help="Original due date",
                disabled=True
            ),
            "completed_date": st.column_config.TextColumn(
                "Completed",
                help="Completion date",
                disabled=True
            ),
            "outcome": st.column_config.TextColumn(
                "Results",
                help="Task outcome/result",
                max_chars=500
            ),
            "notes": None,  # Hide notes column by default in completed tasks view
        }
        
        # Initialize session state with current DataFrame if not exists or if task count changed
        session_key = "completed_tasks_df_all"
        if session_key not in st.session_state or len(st.session_state[session_key]) != len(completed_df):
            st.session_state[session_key] = completed_df.copy()
        
        # Display as editable data editor
        edited_df = st.data_editor(
            completed_df,
            column_config=column_config,
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            disabled=["id", "due_date", "completed_date", "company_name"],  # completed checkbox is editable to allow unchecking
            key="completed_tasks_all"
        )
        
        # Handle edits - only process if there are actual changes
        if not edited_df.equals(st.session_state[session_key]):
            handle_completed_task_edits(edited_df, st.session_state[session_key], completed_tasks)
            st.session_state[session_key] = edited_df.copy()
            st.rerun()


def all_tasks_page():
    """Main All Tasks page - shows tasks from all companies with company name column"""
    # CSS for data editor and dialog centering (reused from tasks.py)
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
    </style>
    """, unsafe_allow_html=True)
    
    # Get all tasks from all companies
    all_tasks = get_all_tasks()
    
    # Header and filter row
    col_header, col_filter = st.columns([3, 1])
    
    with col_header:
        tasks_header = st.empty()
        
    with col_filter:
        filter_option = st.selectbox(
            "View",
            options=["Assigned to me", "All tasks", "My active tasks", "Created by me", "Overdue", "Due today", "Due this week"],
            label_visibility="visible",
            key="all_tasks_filter_view",
            index=0  # Default to "Assigned to me"
        )
    
    # Apply filters
    today = date.today()
    current_user = get_current_user()
    
    filtered_tasks = all_tasks
    if filter_option == "Assigned to me":
        if current_user:
            filtered_tasks = [t for t in all_tasks if t.assignee and current_user.lower() in t.assignee.lower()]
        else:
            filtered_tasks = []
    elif filter_option == "All tasks":
        # No additional filtering - keep all_tasks
        pass
    elif filter_option == "My active tasks":
        if current_user:
            filtered_tasks = [t for t in all_tasks if t.status == "active" and t.assignee and current_user.lower() in t.assignee.lower()]
        else:
            filtered_tasks = []
    elif filter_option == "Created by me":
        if current_user:
            filtered_tasks = [t for t in all_tasks if t.created_by and current_user.lower() in t.created_by.lower()]
        else:
            filtered_tasks = []
    elif filter_option == "Overdue":
        filtered_tasks = [t for t in all_tasks if t.status == "active" and t.due_date and t.due_date < today]
    elif filter_option == "Due today":
        filtered_tasks = [t for t in all_tasks if t.status == "active" and t.due_date and t.due_date == today]
    elif filter_option == "Due this week":
        week_end = today + timedelta(days=7)
        filtered_tasks = [t for t in all_tasks if t.status == "active" and t.due_date and today <= t.due_date <= week_end]
    
    # Count active tasks for header (from filtered tasks)
    active_count = len([t for t in filtered_tasks if t.status == "active"])
    tasks_header.subheader(f"Active Tasks ({active_count})")
    
    # Show active tasks in data editor
    if filtered_tasks:
        show_all_tasks_data_editor(filtered_tasks)
        
        # Show completed tasks section below active tasks
        show_completed_tasks_section(filtered_tasks)
    else:
        st.info("No tasks found. Tasks will appear here when added from company pages.")
        
        # Show completed tasks section even if no active tasks
        show_completed_tasks_section(filtered_tasks)
