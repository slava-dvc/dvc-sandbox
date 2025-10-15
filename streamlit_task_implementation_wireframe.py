"""
Streamlit Task Tab Implementation Wireframe
Following Streamlit best practices for optimal usability
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple
import re

def show_tasks_tab_wireframe():
    """
    Main tasks tab implementation following Streamlit best practices
    This is a wireframe showing the ideal structure and components
    """
    
    # Page header with clear title and context
    st.markdown("## 📋 Tasks")
    st.caption("Manage and track your team's tasks and follow-ups")
    
    # Add task form - using st.form for better UX
    show_add_task_form()
    
    # Task overview and filters section
    show_task_overview_and_filters()
    
    # Main active tasks table
    show_active_tasks_table()
    
    # Completed tasks section (collapsible)
    show_completed_tasks_section()
    
    # Quick actions footer
    show_quick_actions()


def show_add_task_form():
    """Enhanced add task form with natural language parsing"""
    
    st.markdown("### 📝 Add New Task")
    
    with st.form("add_task_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            task_input = st.text_input(
                "Add a task...",
                placeholder="Add a task... (e.g., 'setup call on 10/11 @Nick')",
                label_visibility="collapsed",
                help="💡 Use natural language: 'meeting tomorrow @Elena' or 'review docs on Friday'"
            )
        
        with col2:
            submitted = st.form_submit_button(
                "+ Add", 
                use_container_width=True,
                type="primary"
            )
        
        if submitted and task_input.strip():
            # Parse natural language input
            title, due_date, assignee, error = parse_task_input(task_input)
            
            if error:
                st.error(error)
            elif title:
                # Add task logic here
                st.success(f"✅ Task added: {title}")
                st.rerun()
            else:
                st.warning("Please enter a valid task description")


def show_task_overview_and_filters():
    """Task overview with metrics and filtering options"""
    
    # Get task data (mock for wireframe)
    active_tasks = 4
    overdue_tasks = 1
    completed_this_week = 1
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Active Tasks", 
            active_tasks, 
            f"{overdue_tasks} overdue",
            delta_color="inverse"
        )
    
    with col2:
        st.metric(
            "Completed This Week", 
            completed_this_week, 
            "100% completion rate"
        )
    
    with col3:
        st.metric(
            "Team Productivity", 
            "85%", 
            "↑ 12% from last week"
        )
    
    with col4:
        st.metric(
            "Average Completion", 
            "2.3 days", 
            "↓ 0.5 days"
        )
    
    # Filters and search
    st.divider()
    
    col_filter, col_search, col_actions = st.columns([2, 3, 2])
    
    with col_filter:
        filter_option = st.selectbox(
            "View",
            options=[
                "All tasks",
                "Active only", 
                "Completed only",
                "Overdue only",
                "Created by me",
                "Assigned to me"
            ],
            label_visibility="collapsed"
        )
    
    with col_search:
        search_query = st.text_input(
            "Search tasks...",
            placeholder="Search by task, assignee, or notes...",
            label_visibility="collapsed"
        )
    
    with col_actions:
        if st.button("⚙️ Settings", use_container_width=True):
            st.info("Settings panel would open here")


def show_active_tasks_table():
    """Main active tasks table using st.data_editor"""
    
    st.markdown("### 📋 Active Tasks")
    
    # Mock data for wireframe
    tasks_data = [
        {
            "id": 1,
            "completed": False,
            "title": "Investor relations update",
            "owner": "Elena",
            "due_display": "🟡 Oct 18, 2025",
            "notes": "Prepare monthly portfolio update and community engagement metrics for LPs.",
            "priority": "High"
        },
        {
            "id": 2,
            "completed": False,
            "title": "Review AI model performance metrics",
            "owner": "Alexey",
            "due_display": "🟡 Oct 19, 2025",
            "notes": "Evaluate accuracy, latency, and cost metrics for production deployment.",
            "priority": "Medium"
        },
        {
            "id": 3,
            "completed": False,
            "title": "Platform automation improvements",
            "owner": "Tony",
            "due_display": "🟢 Oct 21, 2025",
            "notes": "Implement automated workflow triggers for investor updates and portfolio monitoring.",
            "priority": "Medium"
        },
        {
            "id": 4,
            "completed": False,
            "title": "Build AI agent for deal sourcing",
            "owner": "Vlad",
            "due_display": "⚪ Oct 29, 2025",
            "notes": "Develop automated workflow to connect data sources and enhance deal pipeline efficiency.",
            "priority": "Low"
        }
    ]
    
    df = pd.DataFrame(tasks_data)
    
    # Team members for owner selection
    team_members = ["Unassigned", "Marina", "Nick", "Mel", "Charles", "Alexey", "Tony", "Elena", "Vlad", "Slava"]
    
    # Column configuration for data editor
    column_config = {
        "id": None,  # Hide ID column
        "priority": None,  # Hide priority column
        "completed": st.column_config.CheckboxColumn(
            "Done",
            help="Mark task as completed",
            default=False
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
            width="medium"
        ),
        "due_display": st.column_config.TextColumn(
            "Due",
            help="Due date with color coding",
            disabled=True,
            width="medium"
        ),
        "notes": st.column_config.TextColumn(
            "Notes",
            help="Task notes and context",
            max_chars=500,
            width="large"
        ),
    }
    
    # Display data editor
    edited_df = st.data_editor(
        df,
        column_config=column_config,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        disabled=["id", "priority", "due_display"],
        key="active_tasks_editor"
    )
    
    # Handle edits
    if not edited_df.equals(df):
        handle_task_edits(edited_df, df)
        st.rerun()


def show_completed_tasks_section():
    """Completed tasks in collapsible expander"""
    
    # Mock completed tasks data
    completed_data = [
        {
            "id": 5,
            "completed": True,
            "title": "Board meeting preparation",
            "owner": "Slava",
            "due_display": "Oct 14, 2025",
            "completed_date": "Oct 15, 2025",
            "outcome": "Board materials prepared. All metrics and KPIs updated for Q4 review.",
            "notes": "Successfully completed ahead of schedule"
        }
    ]
    
    completed_df = pd.DataFrame(completed_data)
    
    with st.expander("✅ Completed Tasks (1)", expanded=False):
        if not completed_df.empty:
            # Column configuration for completed tasks
            completed_column_config = {
                "id": None,
                "completed": st.column_config.CheckboxColumn(
                    "Done",
                    help="Uncheck to reactivate task",
                    default=True
                ),
                "title": st.column_config.TextColumn(
                    "Task",
                    help="Completed task description",
                    max_chars=200
                ),
                "owner": st.column_config.SelectboxColumn(
                    "Owner",
                    help="Task assignee",
                    options=["Unassigned", "Marina", "Nick", "Mel", "Charles", "Alexey", "Tony", "Elena", "Vlad", "Slava"],
                    default="Unassigned"
                ),
                "due_display": st.column_config.TextColumn(
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
                "notes": None,  # Hide notes in completed view
            }
            
            st.data_editor(
                completed_df,
                column_config=completed_column_config,
                hide_index=True,
                use_container_width=True,
                num_rows="fixed",
                disabled=["id", "due_display", "completed_date"],
                key="completed_tasks_editor"
            )
        else:
            st.info("No completed tasks yet.")


def show_quick_actions():
    """Quick action buttons for common tasks"""
    
    st.divider()
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📝 Add Multiple Tasks", use_container_width=True):
            st.info("Multi-task form would open here")
    
    with col2:
        if st.button("📅 Set Due Date", use_container_width=True):
            st.info("Date picker would open here")
    
    with col3:
        if st.button("👥 Assign to Team", use_container_width=True):
            st.info("Team assignment dialog would open here")
    
    with col4:
        if st.button("📊 Generate Report", use_container_width=True):
            st.info("Report generation would start here")


def parse_task_input(input_text: str) -> Tuple[str, Optional[date], Optional[str], Optional[str]]:
    """
    Parse natural language task input
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
    # Check for weekday names
    elif (weekday_match := re.search(r'\b(next\s+)?(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', text, re.IGNORECASE)):
        is_next_week = bool(weekday_match.group(1))
        day_name = weekday_match.group(2).lower()
        
        weekday_map = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        target_weekday = weekday_map[day_name]
        current_weekday = today.weekday()
        
        days_ahead = target_weekday - current_weekday
        if days_ahead <= 0 or is_next_week:
            days_ahead += 7
        
        due_date = today + timedelta(days=days_ahead)
        text = text.replace(weekday_match.group(0), '').strip()
    # Check for date patterns like 10/11 or 10/11/25
    else:
        date_match = re.search(r'(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?', text)
        if date_match:
            month = int(date_match.group(1))
            day = int(date_match.group(2))
            year = int(date_match.group(3)) if date_match.group(3) else today.year
            
            if year < 100:
                year += 2000
            
            try:
                due_date = date(year, month, day)
                text = text.replace(date_match.group(0), '').strip()
            except ValueError:
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


def handle_task_edits(edited_df: pd.DataFrame, original_df: pd.DataFrame):
    """Handle changes from data editor"""
    # This would contain the actual logic for updating tasks
    st.info("Task updates would be processed here")


# CSS Styling for enhanced appearance
def apply_task_styling():
    """Apply custom CSS styling for better appearance"""
    st.markdown("""
    <style>
    /* Compact row styling */
    [data-testid="stDataFrame"] td {
        padding: 12px 16px !important;
        min-height: 40px !important;
    }
    
    /* Completed row styling */
    [data-testid="stDataFrame"] tbody tr:has(input[type="checkbox"]:checked) td {
        opacity: 0.6;
        text-decoration: line-through !important;
    }
    
    /* Enhanced form styling */
    [data-testid="stForm"] {
        padding: 16px !important;
        margin-bottom: 16px !important;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        background: var(--secondary-background-color);
    }
    
    /* Metric cards styling */
    [data-testid="metric-container"] {
        background: var(--secondary-background-color);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 16px;
    }
    
    /* Quick action buttons */
    [data-testid="stButton"] > button {
        border-radius: 8px;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)


# Main execution
if __name__ == "__main__":
    st.set_page_config(
        page_title="Tasks - DVC Portfolio Dashboard",
        page_icon="📋",
        layout="wide"
    )
    
    apply_task_styling()
    show_tasks_tab_wireframe()
