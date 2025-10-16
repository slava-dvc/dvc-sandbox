"""
Standalone Tasks Dashboard - Cross-company task management
"""
import streamlit as st
from datetime import date, datetime, timedelta
from typing import List, Dict
from collections import defaultdict
from app.shared.task import Task, TaskStatus
from app.dashboard.data import get_all_tasks, get_companies_v2
from app.dashboard.task_state_controller import (
    initialize_session_state, get_filtered_tasks, apply_secondary_filter,
    get_current_user_for_tasks, set_tab
)
from app.dashboard.dialog_utils import show_task_results_dialog

# Team members list for filtering
TEAM_MEMBERS = ["Marina", "Nick", "Mel", "Charles", "Alexey", "Tony", "Elena", "Vlad", "Slava"]


def tasks_dashboard_page():
    """Main standalone tasks dashboard page"""
    st.title("📋 All Tasks")
    
    # Initialize centralized session state
    initialize_session_state()
    
    # GUARD: Clear dialog state when switching tabs
    current_tab = st.session_state.get("active_tab", "Active")
    last_tab_key = "last_active_tab"
    
    if st.session_state.get(last_tab_key) != current_tab:
        # Tab switch detected - clear all dialog state
        st.session_state["active_dialog_task_id"] = None
        dialog_flags = [k for k in st.session_state.keys() if k.startswith("show_results_dialog_")]
        for flag in dialog_flags:
            if flag in st.session_state:
                del st.session_state[flag]
        task_info_keys = [k for k in st.session_state.keys() if k.startswith("completed_task_info_")]
        for key in task_info_keys:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state[last_tab_key] = current_tab
    
    # Get all tasks across all companies
    all_tasks = get_all_tasks()
    
    if not all_tasks:
        st.info("No tasks found. Create tasks from individual company pages.")
        return
    
    # Initialize default filter to "My active tasks"
    if "task_filter_view_dashboard" not in st.session_state:
        st.session_state["task_filter_view_dashboard"] = "My active tasks"
    
    # Task input section with company selector
    show_add_task_form_cross_company()
    
    # Filter controls
    col_segments, col_filter = st.columns([3, 1])
    
    with col_segments:
        show_task_view_segmented_control(all_tasks)
    
    with col_filter:
        filter_option = st.selectbox(
            "View",
            options=["All tasks", "My active tasks", "Created by me", "Overdue", "Due today", "Due this week"],
            label_visibility="collapsed",
            key="task_filter_view_dashboard"
        )
    
    # Apply filters
    current_user = get_current_user_for_tasks()
    active_tab = st.session_state.get("active_tab", "Active")
    filtered_tasks = get_filtered_tasks(all_tasks, active_tab)
    filtered_tasks = apply_secondary_filter(filtered_tasks, filter_option, current_user)
    
    # Group tasks by company
    if filtered_tasks:
        show_tasks_grouped_by_company(filtered_tasks)
    else:
        show_no_tasks_message(active_tab)


def show_add_task_form_cross_company():
    """Add task form with company selector for cross-company dashboard"""
    # Get all companies for the selector
    companies = get_companies_v2()
    company_options = {company.name: company.id for company in companies}
    
    if not company_options:
        st.warning("No companies found. Please create a company first.")
        return
    
    with st.form(key="add_task_form_cross_company", clear_on_submit=True):
        col_company, col_input, col_add = st.columns([2, 3, 1])
        
        with col_company:
            selected_company_name = st.selectbox(
                "Company",
                options=list(company_options.keys()),
                key="selected_company_for_task",
                label_visibility="collapsed"
            )
        
        with col_input:
            task_input = st.text_input(
                "Add new task",
                placeholder="Add task e.g., setup call on 10/11 @Nick",
                key="task_input_cross_company",
                label_visibility="collapsed"
            )
        
        with col_add:
            submitted = st.form_submit_button("Add task", type="secondary", use_container_width=True)
        
        if submitted and task_input and task_input.strip():
            selected_company_id = company_options[selected_company_name]
            # Import the parsing function from tasks.py
            from app.dashboard.tasks import parse_task_input
            
            # Parse the input
            title, due_date, assignee, error_msg = parse_task_input(task_input)
            
            if error_msg:
                st.error(error_msg)
            elif title:
                # Get current user as creator
                creator = get_current_user_for_tasks() or "Anonymous"
                
                # If no assignee was parsed, default to current user
                if not assignee:
                    assignee = creator
                
                try:
                    from app.dashboard.data import add_task
                    task = add_task(selected_company_id, title, due_date, assignee, created_by=creator)
                    st.success(f"✅ Task added to {selected_company_name}: {title}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding task: {str(e)}")
            else:
                st.warning("Please enter a task description")


def show_task_view_segmented_control(all_tasks: List[Task]):
    """Display segmented control for task view with counts"""
    # Calculate counts
    active_count = len([t for t in all_tasks if t.status == TaskStatus.ACTIVE.value])
    completed_count = len([t for t in all_tasks if t.status == TaskStatus.COMPLETED.value])
    total_count = len(all_tasks)
    
    # Options with counts
    options = [
        f"Active Tasks ({active_count})",
        f"Completed ({completed_count})",
        f"All ({total_count})"
    ]
    
    # Native segmented control
    selected = st.segmented_control(
        label="Filter tasks by status",
        options=options,
        default=f"Active Tasks ({active_count})",
        label_visibility="collapsed",
        key="task_segment_dashboard"
    )
    
    # Update session state
    previous_view = st.session_state.get("active_tab", "Active")
    if selected and "Active Tasks" in selected:
        set_tab("Active")
    elif selected and "Completed" in selected:
        set_tab("Completed")
    elif selected and "All" in selected:
        set_tab("All")
    else:
        set_tab("Active")  # Default


def show_tasks_grouped_by_company(filtered_tasks: List[Task]):
    """Display tasks grouped by company with collapsible sections"""
    # Group tasks by company_id
    tasks_by_company = defaultdict(list)
    for task in filtered_tasks:
        tasks_by_company[task.company_id].append(task)
    
    # Get company names for display
    companies = get_companies_v2()
    company_names = {company.id: company.name for company in companies}
    
    # Sort companies by name for consistent ordering
    sorted_company_ids = sorted(tasks_by_company.keys(), 
                               key=lambda cid: company_names.get(cid, "Unknown"))
    
    for company_id in sorted_company_ids:
        company_tasks = tasks_by_company[company_id]
        company_name = company_names.get(company_id, "Unknown Company")
        
        # Sort tasks within company by due date and creation date
        company_tasks.sort(key=lambda t: (
            t.due_date if t.due_date else date.max,
            t.created_at
        ))
        
        with st.expander(f"🏢 {company_name} ({len(company_tasks)} tasks)", expanded=True):
            show_company_tasks_table(company_tasks)


def show_company_tasks_table(tasks: List[Task]):
    """Display tasks for a specific company in a table format"""
    if not tasks:
        return
    
    # Prepare data for display
    import pandas as pd
    from app.dashboard.tasks import prepare_tasks_dataframe
    
    df = prepare_tasks_dataframe(tasks)
    
    # Configure columns
    column_config = {
        "id": None,  # Hide ID column
        "status": None,  # Hide status column
        "created_at": None,  # Hide created_at column
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
        "owner": st.column_config.SelectboxColumn(
            "Owner",
            help="Task assignee",
            options=["Unassigned"] + TEAM_MEMBERS,
            default="Unassigned"
        ),
        "due_date": st.column_config.DateColumn(
            "Due",
            help="Due date - click to edit",
            min_value=date.today(),
            format="MMM DD, YYYY"
        ),
        "due_display": None,  # Hide display column
        "notes": st.column_config.TextColumn(
            "Notes",
            help="Task notes and context",
            max_chars=500
        ),
        "outcome": st.column_config.TextColumn(
            "Results",
            help="Task outcome/result",
            max_chars=500
        ),
    }
    
    # Show completed tasks differently
    active_tab = st.session_state.get("active_tab", "Active")
    if active_tab == "Completed":
        # For completed tasks, show different columns and make outcome editable
        column_config.update({
            "completed": st.column_config.CheckboxColumn(
                "Done",
                help="Uncheck to return task to active status",
                default=True
            ),
            "due_date": st.column_config.DateColumn(
                "Completed",
                help="Completion date",
                format="MMM DD, YYYY"
            ),
            "outcome": st.column_config.TextColumn(
                "Results",
                help="Task outcome/result",
                max_chars=500
            ),
            "notes": None,  # Hide notes in completed view
        })
        disabled_columns = ["id", "status", "created_at", "due_date"]
    else:
        # For active tasks, hide outcome column
        column_config["outcome"] = None
        disabled_columns = ["id", "status", "created_at", "outcome"]
    
    # Display data editor
    edited_df = st.data_editor(
        df,
        column_config=column_config,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        disabled=disabled_columns,
        key=f"tasks_editor_dashboard_{tasks[0].company_id if tasks else 'unknown'}"
    )
    
    # Handle edits
    if not edited_df.equals(df):
        from app.dashboard.tasks import handle_task_edits, handle_completed_task_edits
        if active_tab == "Completed":
            handle_completed_task_edits(edited_df, df, tasks[0].company_id, tasks)
        else:
            handle_task_edits(edited_df, df, tasks[0].company_id, tasks)
        st.rerun()


def show_no_tasks_message(active_tab: str):
    """Show appropriate message when no tasks match the filter"""
    if active_tab == "Active":
        st.info("No active tasks found.")
    elif active_tab == "Completed":
        st.info("No completed tasks found.")
    else:  # "All"
        st.info("No tasks found.")


# Import the necessary functions from tasks.py that we're reusing
def show_task_results_dialog_wrapper(task: Task):
    """Wrapper to show task results dialog"""
    show_task_results_dialog(task)
