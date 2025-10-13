"""
Tasks UI components for the DVC Portfolio Dashboard
"""
import streamlit as st
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional, Tuple
import re
from app.shared.task import Task
from app.dashboard.data import get_tasks, add_task, update_task, delete_task


def parse_task_input(input_text: str) -> Tuple[str, Optional[date], Optional[str]]:
    """
    Parse task input in format: "setup call on 10/11 @Nick"
    Returns: (title, due_date, assignee)
    """
    if not input_text or not input_text.strip():
        return "", None, None
    
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
    
    # Clean up title
    title = re.sub(r'\s+', ' ', text).strip()
    
    return title, due_date, assignee


def show_tasks_section(company):
    """Main tasks section for company pages"""
    # Remove the Tasks header to match wireframe
    
    # Get company ID from the company object
    company_id = company.id
    if not company_id:
        st.error("No company selected")
        return
    
    # Get tasks for this company
    all_tasks = get_tasks(company_id)
    
    # Add task form (separate from filter)
    show_add_task_form(company_id)
    
    # Add filter as separate component
    col_filter_header, col_filter_dropdown = st.columns([4, 1])
    with col_filter_header:
        st.markdown("")  # Empty space for alignment
    with col_filter_dropdown:
        filter_option = st.selectbox(
            "Filter",
            options=["All tasks", "Active", "Completed", "Overdue", "My tasks"],
            label_visibility="collapsed",
            key="task_filter",
            index=0
        )
    
    # Apply filters
    today = date.today()
    # Get current user name safely
    current_user = None
    if hasattr(st, 'user'):
        try:
            # Try to get user name from different possible attributes
            if hasattr(st.user, 'given_name') and hasattr(st.user, 'family_name'):
                current_user = f"{st.user.given_name} {st.user.family_name}"
            elif hasattr(st.user, 'name'):
                current_user = st.user.name
            elif hasattr(st.user, 'email'):
                current_user = st.user.email
        except:
            current_user = None
    
    if filter_option == "Active":
        tasks = [t for t in all_tasks if t.status == "active" and (t.due_date is None or t.due_date >= today)]
    elif filter_option == "Completed":
        tasks = [t for t in all_tasks if t.status == "completed"]
    elif filter_option == "Overdue":
        tasks = [t for t in all_tasks if t.status == "active" and t.due_date and t.due_date < today]
    elif filter_option == "My tasks":
        if current_user:
            # Match assignee with current user (flexible matching)
            tasks = [t for t in all_tasks if t.assignee and current_user.lower() in t.assignee.lower()]
        else:
            tasks = all_tasks
    else:  # "All tasks"
        tasks = all_tasks
    
    # Separate active and completed tasks
    active_tasks = [t for t in tasks if t.status == "active"]
    completed_tasks = [t for t in tasks if t.status == "completed"]
    
    # Sort tasks
    active_tasks.sort(key=lambda t: t.due_date if t.due_date else date.max)
    completed_tasks.sort(key=lambda t: t.completed_at if t.completed_at else datetime.min, reverse=True)
    
    # Show active tasks
    if active_tasks:
        st.subheader(f"📋 Active Tasks ({len(active_tasks)})")
        show_task_list(active_tasks, company_id, is_completed=False)
    else:
        st.info("No active tasks")
    
    # Show completed tasks (collapsible)
    if completed_tasks:
        with st.expander(f"✅ Completed Tasks ({len(completed_tasks)})", expanded=False):
            show_task_list(completed_tasks, company_id, is_completed=True)
    
    # Handle complete modal trigger (inline editing is handled in show_task_list)
    for task in all_tasks:
        if st.session_state.get(f"completing_task_{task.id}", False):
            show_complete_task_modal(task)


def show_add_task_form(company_id: str):
    """Form to add a new task with auto-parsing"""
    # Add sticky positioning CSS for the input bar with comprehensive styling
    st.markdown("""
    <style>
    /* Sticky positioning and layout */
    [data-testid="stForm"] {
        position: sticky;
        top: 0;
        background: white;
        z-index: 100;
        padding: 16px 20px;
        border-bottom: 1px solid #e5e7eb;
        margin-bottom: 20px;
        display: flex !important;
        align-items: center !important;
    }
    
    /* Consistent heights */
    [data-testid="stForm"] input,
    [data-testid="stForm"] button,
    [data-testid="stForm"] [data-baseweb="select"] {
        min-height: 40px !important;
        height: 40px !important;
    }
    
    /* Input field styling */
    [data-testid="stForm"] input {
        padding: 12px 16px !important;
        background: #F7F8FA !important;
        border-radius: 6px !important;
        border: 1px solid #e5e7eb !important;
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.05) !important;
    }
    
    /* Primary Add button - emphasized with white background */
    [data-testid="stForm"] button[kind="primary"],
    [data-testid="stForm"] button[data-testid="baseButton-primary"],
    [data-testid="stForm"] button[data-testid="stBaseButton-primary"],
    [data-testid="stForm"] button[data-testid="stBaseButton-primaryFormSubmit"] {
        background: white !important;
        color: #1a1a1a !important;
        border: 1px solid #e5e7eb !important;
        font-weight: 500 !important;
        border-radius: 6px !important;
    }
    
    /* Override Streamlit's default primary button styling */
    [data-testid="stForm"] button[data-testid="baseButton-primary"]:hover,
    [data-testid="stForm"] button[data-testid="stBaseButton-primary"]:hover,
    [data-testid="stForm"] button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
        background: #f8f9fa !important;
        color: #1a1a1a !important;
        border: 1px solid #e5e7eb !important;
    }
    
    /* Filter dropdown - secondary styling */
    [data-testid="stForm"] [data-baseweb="select"] {
        background: #F7F8FA !important;
        border-radius: 6px !important;
    }
    
    /* Add spacing between elements */
    [data-testid="stForm"] [data-testid="column"] {
        gap: 12px !important;
    }
    
    /* Ensure form content has proper padding */
    [data-testid="stForm"] > div {
        padding: 0 4px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.form(key=f"add_task_form_{company_id}", clear_on_submit=True):
        col_input, col_add = st.columns([5, 1])
        
        with col_input:
            task_input = st.text_input(
                "Add new task",
                placeholder='e.g., "setup call on 10/11 @Nick" or "review deck tomorrow @Marina"',
                key=f"task_input_{company_id}",
                label_visibility="collapsed"
            )
        
        with col_add:
            submitted = st.form_submit_button("➕ Add", use_container_width=True, type="primary")
        
        if submitted and task_input and task_input.strip():
            # Parse the input
            title, due_date, assignee = parse_task_input(task_input)
            
            if title:
                # Get current user as creator
                creator = "Anonymous"
                if hasattr(st, 'user'):
                    try:
                        if hasattr(st.user, 'given_name') and hasattr(st.user, 'family_name'):
                            creator = f"{st.user.given_name} {st.user.family_name}"
                        elif hasattr(st.user, 'name'):
                            creator = st.user.name
                        elif hasattr(st.user, 'email'):
                            creator = st.user.email.split('@')[0]  # Use email prefix as name
                    except:
                        creator = "Anonymous"
                
                # If no assignee was parsed, default to creator
                if not assignee:
                    assignee = creator
                
                try:
                    task = add_task(company_id, title, due_date, assignee, created_by=creator)
                    st.success(f"✅ Task added: '{title}' → @{assignee} (Due: {due_date.strftime('%m/%d')})")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error adding task: {str(e)}")
            else:
                st.warning("Please enter a task description")
    
    # Filter is now handled separately, no need to return it


def show_task_list(tasks: List[Task], company_id: str, is_completed: bool = False):
    """Display a list of tasks with clean Todoist-style design"""
    # Add CSS for clean, airy task cards
    st.markdown("""
    <style>
    .task-card {
        background: #FAFAFA !important;
        border: 1px solid #E9E9E9 !important;
        border-radius: 8px !important;
        margin: 8px 0 !important;
        padding: 12px 16px !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }
    .task-card:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
        transform: translateY(-1px) !important;
    }
    .task-title {
        font-weight: 500 !important;
        font-size: 16px !important;
        line-height: 1.4 !important;
        margin: 0 0 8px 0 !important;
        color: #1a1a1a !important;
    }
    .task-metadata {
        font-size: 14px !important;
        color: #666 !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
    }
    .task-owner {
        display: flex !important;
        align-items: center !important;
        gap: 4px !important;
    }
    .task-due-date {
        display: flex !important;
        align-items: center !important;
        gap: 4px !important;
    }
    .due-date-overdue { color: #ef4444 !important; }
    .due-date-soon { color: #f97316 !important; }
    .due-date-upcoming { color: #22c55e !important; }
    .due-date-gray { color: #9ca3af !important; }
    .task-expanded {
        background: white !important;
        border: 1px solid #E9E9E9 !important;
        border-radius: 8px !important;
        margin: 8px 0 !important;
        padding: 16px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }
    .task-actions {
        opacity: 0;
        transition: opacity 0.2s ease;
    }
    .task-card:hover .task-actions {
        opacity: 1;
    }
    
    /* Hide empty button containers that appear as gray boxes */
    [data-testid="stBaseButton-secondary"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Style action buttons to be compact */
    .action-button {
        min-width: auto !important;
        width: auto !important;
        padding: 4px 8px !important;
        margin: 0 2px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    for task in tasks:
        if is_completed:
            # Completed task display with inline editing
            
            # Check if this task is being edited inline
            is_editing = st.session_state.get(f"inline_editing_{task.id}", False)
            
            if is_editing:
                # Inline edit mode for completed task
                col_title, col_date = st.columns([3, 2])
                
                with col_title:
                    new_title = st.text_input(
                        "Title",
                        value=task.text,
                        key=f"inline_title_{task.id}",
                        label_visibility="collapsed"
                    )
                
                with col_date:
                    new_due_date = st.date_input(
                        "Due date",
                        value=task.due_date if task.due_date else date.today(),
                        key=f"inline_date_{task.id}",
                        label_visibility="collapsed"
                    )
                
                # Notes section
                new_notes = st.text_area(
                    "Notes / Description",
                    value=task.notes if task.notes else "",
                    key=f"inline_notes_{task.id}",
                    height=80,
                    placeholder="Add notes or description..."
                )
                
                # Action buttons
                col_save, col_cancel = st.columns([1, 1])
                with col_save:
                    if st.button("💾 Save", key=f"save_inline_{task.id}", use_container_width=True):
                        update_task(task.id, text=new_title, due_date=new_due_date, notes=new_notes)
                        st.session_state[f"inline_editing_{task.id}"] = False
                        st.success("✅ Task updated!")
                        st.rerun()
                with col_cancel:
                    if st.button("❌ Cancel", key=f"cancel_inline_{task.id}", use_container_width=True):
                        st.session_state[f"inline_editing_{task.id}"] = False
                        st.rerun()
            else:
                # Normal display mode
                col_title, col_actions = st.columns([5, 1])
                
                with col_title:
                    # Use a clickable button with strikethrough styling for completed tasks
                    if st.button(
                        f"~~{task.text}~~",
                        key=f"title_btn_{task.id}",
                        help="Click to edit completed task",
                        use_container_width=True,
                        type="secondary"
                    ):
                        st.session_state[f"inline_editing_{task.id}"] = True
                        st.rerun()
                    
                    # Notes/description if exists
                    if task.notes and task.notes.strip():
                        st.markdown(f"""
                        <div style='color: #495057; font-size: 14px; margin-top: 4px; padding: 8px; 
                                    background-color: #f8f9fa; border-left: 3px solid #adb5bd; border-radius: 3px;'>
                            📝 {task.notes}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Outcome box
                    if task.outcome:
                        st.markdown(f"""
                        <div style='background-color: #d4edda; color: #155724; padding: 8px 12px; 
                                    border-radius: 4px; margin-top: 8px; border: 1px solid #c3e6cb;'>
                            ✅ <strong>Outcome:</strong> {task.outcome}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Metadata
                    created_date = task.created_at.strftime('%b %d, %Y') if task.created_at else 'Unknown'
                    st.markdown(f"<div style='color: #6c757d; font-size: 14px; margin-top: 8px;'>👤 {task.assignee} · 🧾 Created by {task.created_by} on {created_date}</div>", unsafe_allow_html=True)
                
                with col_actions:
                    st.markdown('<div class="task-actions">', unsafe_allow_html=True)
                    if st.button("↩️", key=f"reopen_{task.id}", help="Reopen task", type="secondary"):
                        update_task(task.id, status="active", outcome=None, completed_at=None)
                        st.success("Task reopened!")
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Active task display with inline editing
            
            # Check if this task is being edited inline
            is_editing = st.session_state.get(f"inline_editing_{task.id}", False)
            
            if is_editing:
                # Expanded edit mode
                with st.container():
                    st.markdown(f'<div class="task-expanded">', unsafe_allow_html=True)
                    
                    with st.form(key=f"edit_task_{task.id}"):
                        # Edit mode - show form fields
                        new_title = st.text_input(
                            "Title",
                            value=task.text,
                            key=f"edit_title_{task.id}",
                            placeholder="Enter task title..."
                        )
                        
                        # Notes/description
                        new_notes = st.text_area(
                            "Description",
                            value=task.notes or "",
                            key=f"edit_notes_{task.id}",
                            placeholder="Add notes or description..."
                        )
                        
                        # Due date picker
                        col_date, col_actions = st.columns([3, 1])
                        with col_date:
                            new_due_date = st.date_input(
                                "⏰ Due date",
                                value=task.due_date,
                                key=f"edit_due_date_{task.id}"
                            )
                        
                        with col_actions:
                            st.markdown('<br>', unsafe_allow_html=True)  # Spacer
                            col_save, col_cancel = st.columns([1, 1])
                            with col_save:
                                if st.form_submit_button("Save", type="primary"):
                                    if new_title and new_title.strip():
                                        update_task(task.id, text=new_title.strip(), due_date=new_due_date, notes=new_notes.strip() or None)
                                        st.session_state[f"inline_editing_{task.id}"] = False
                                        st.success("Task updated!")
                                        st.rerun()
                                    else:
                                        st.warning("Please enter a task title")
                            
                            with col_cancel:
                                if st.form_submit_button("Cancel"):
                                    st.session_state[f"inline_editing_{task.id}"] = False
                                    st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                # Collapsed view - clean two-line card
                # Determine due date color class
                today = date.today()
                due_date_class = "due-date-gray"
                due_date_str = "No due date"
                
                if task.due_date:
                    days_until_due = (task.due_date - today).days
                    due_date_str = task.due_date.strftime('%m/%d/%Y')
                    
                    if days_until_due < 0:
                        due_date_class = "due-date-overdue"
                    elif days_until_due <= 2:
                        due_date_class = "due-date-soon"
                    else:
                        due_date_class = "due-date-upcoming"
                
                # Clean task card without buttons - just display
                st.markdown(f'<div class="task-card">', unsafe_allow_html=True)
                
                # Two-line layout
                st.markdown(f"""
                <div class="task-title">{task.text}</div>
                <div class="task-metadata">
                    <div class="task-owner">👤 {task.assignee}</div>
                    <div class="task-due-date {due_date_class}">⏰ {due_date_str}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Add action buttons below the card
                col_edit, col_complete = st.columns([1, 1])
                
                with col_edit:
                    if st.button("✏️ Edit", key=f"edit_{task.id}", help="Edit task", type="secondary"):
                        st.session_state[f"inline_editing_{task.id}"] = True
                        st.rerun()
                
                with col_complete:
                    if st.button("✓ Complete", key=f"complete_{task.id}", help="Complete task", type="secondary"):
                        st.session_state[f"completing_task_{task.id}"] = True
                        st.rerun()


@st.dialog("Edit Task")
def show_task_edit_modal(task: Task):
    """Modal to edit an existing task"""
    st.markdown(f"**{task.text}**")
    st.markdown("---")
    
    # Edit fields
    new_title = st.text_input("Task Title", value=task.text, key=f"modal_edit_title_{task.id}")
    new_assignee = st.text_input("Assignee", value=task.assignee, key=f"modal_edit_assignee_{task.id}")
    new_due_date = st.date_input("Due Date", value=task.due_date if task.due_date else date.today(), key=f"modal_edit_due_{task.id}")
    new_notes = st.text_area("Notes", value=task.notes if task.notes else "", key=f"modal_edit_notes_{task.id}")
    
    st.markdown("---")
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save", type="primary", use_container_width=True, key=f"modal_save_{task.id}"):
            try:
                update_task(task.id, 
                          text=new_title,
                          assignee=new_assignee,
                          due_date=new_due_date,
                          notes=new_notes)
                st.success("✅ Task updated successfully!")
                st.session_state[f"editing_task_{task.id}"] = False
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error updating task: {str(e)}")
    
    with col2:
        if st.button("❌ Cancel", use_container_width=True, key=f"modal_cancel_{task.id}"):
            st.session_state[f"editing_task_{task.id}"] = False
            st.rerun()
    
    with col3:
        if st.button("🗑️ Delete", use_container_width=True, key=f"modal_delete_{task.id}"):
            try:
                delete_task(task.id)
                st.success("✅ Task deleted successfully!")
                st.session_state[f"editing_task_{task.id}"] = False
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error deleting task: {str(e)}")


@st.dialog("Complete Task")
def show_complete_task_modal(task: Task):
    """Modal to complete a task with outcome"""
    st.markdown(f"**{task.text}**")
    st.markdown("---")
    
    outcome = st.text_area(
        "Outcome / Decision:",
        placeholder="Enter the outcome or decision from this task...",
        key=f"modal_outcome_{task.id}"
    )
    
    st.markdown("---")
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Complete Task", type="primary", use_container_width=True, key=f"modal_complete_{task.id}"):
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
    
    with col2:
        if st.button("❌ Cancel", use_container_width=True, key=f"modal_complete_cancel_{task.id}"):
            st.session_state[f"completing_task_{task.id}"] = False
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
        <div style="text-align: left; font-size: 13px; color: #7a7d81; margin-bottom: 12px; font-weight: normal; font-style: italic;">
            Last updated: Today {time_ago}
        </div>
        """.format(time_ago=time_ago), unsafe_allow_html=True)
        
        # LAST DISCUSSED section with consistent padding
        st.markdown("""
        <div style="
            font-size: 12px; 
            color: #8c9a9e; 
            font-variant: all-small-caps; 
            letter-spacing: 0.4px; 
            margin-bottom: 6px;
            margin-left: 0;
        ">
            LAST DISCUSSED
        </div>
        """, unsafe_allow_html=True)
        
        if completed_tasks_last_week:
            for task in completed_tasks_last_week:
                # Normalize bullet content tone - short declarative sentences
                task_text = task.text.rstrip('.') + '.' if not task.text.endswith('.') else task.text
                st.markdown(f"""
                <div style="margin-left: 1.4rem; line-height: 1.3; margin: 1px 0; font-size: 16px;">
                    • {task_text}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="margin-left: 1.4rem; line-height: 1.3; margin: 1px 0; font-size: 16px;">
                • No completed tasks in the past week.
            </div>
            """, unsafe_allow_html=True)
        
        # OUTCOME section with consistent padding
        st.markdown("""
        <div style="
            font-size: 12px; 
            color: #8c9a9e; 
            font-variant: all-small-caps; 
            letter-spacing: 0.4px; 
            margin-bottom: 6px;
            margin-top: 12px;
            margin-left: 0;
        ">
            OUTCOME
        </div>
        """, unsafe_allow_html=True)
        
        if completed_tasks_last_week:
            for task in completed_tasks_last_week:
                # Enforce consistent capitalization and period use in Outcomes
                outcome_text = task.outcome if task.outcome else "(no notes)"
                outcome_text = outcome_text.rstrip('.') + '.' if outcome_text != "(no notes)" and not outcome_text.endswith('.') else outcome_text
                st.markdown(f"""
                <div style="margin-left: 1.4rem; line-height: 1.3; margin: 1px 0; font-size: 16px;">
                    • {outcome_text}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="margin-left: 1.4rem; line-height: 1.3; margin: 1px 0; font-size: 16px;">
                • (no outcomes)
            </div>
            """, unsafe_allow_html=True)
        
        # Single divider only between "Outcome" and "Next Step" sections
        st.markdown("""
        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 12px 0; opacity: 0.5;">
        """, unsafe_allow_html=True)
        
        # NEXT STEP section with consistent padding
        st.markdown("""
        <div style="
            font-size: 12px; 
            color: #8c9a9e; 
            font-variant: all-small-caps; 
            letter-spacing: 0.4px; 
            margin-bottom: 6px;
            margin-left: 0;
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
                if color == "🔴":  # Overdue
                    status_badge = '<span style="background: #fee2e2; color: #dc2626; border: 1px solid #fecaca; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 500; margin-left: 8px;">Overdue</span>'
                elif color == "🟡":  # Due today
                    status_badge = '<span style="background: #dcfce7; color: #16a34a; border: 1px solid #bbf7d0; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 500; margin-left: 8px;">Today</span>'
                elif color == "🟠":  # Due soon (1-3 days)
                    status_badge = '<span style="background: #fef3c7; color: #d97706; border: 1px solid #fde68a; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 500; margin-left: 8px;">Soon</span>'
                elif color == "🟢":  # Not urgent (4+ days)
                    status_badge = '<span style="background: #e9d5ff; color: #9333ea; border: 1px solid #ddd6fe; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 500; margin-left: 8px;">This Week</span>'
            
            st.markdown(f"""
            <div style="color: #2f2f2f; font-weight: 500; line-height: 1.3; font-size: 16px; margin-bottom: 10px;">
                → <strong>{task_text}</strong> {assignee_text} {status_badge}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="color: #2f2f2f; font-weight: 500; line-height: 1.3; font-size: 16px; margin-bottom: 10px;">
                → Add the next step below.
            </div>
            """, unsafe_allow_html=True)
