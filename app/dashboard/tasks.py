"""
Tasks UI components for the DVC Portfolio Dashboard
"""
import streamlit as st
from datetime import date, datetime
from typing import List, Optional
from app.shared.task import Task
from app.dashboard.data import get_tasks, add_task, update_task, delete_task


def show_tasks_section():
    """Main tasks section for company pages"""
    st.header("📋 Tasks")
    
    # Get company ID from URL params
    company_id = st.query_params.get("company_id")
    if not company_id:
        st.error("No company selected")
        return
    
    # Get tasks for this company
    tasks = get_tasks(company_id)
    
    # Show task summary
    active_tasks = [t for t in tasks if t.status == "active"]
    completed_tasks = [t for t in tasks if t.status == "completed"]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Active Tasks", len(active_tasks))
    with col2:
        st.metric("Completed Tasks", len(completed_tasks))
    with col3:
        st.metric("Total Tasks", len(tasks))
    
    st.markdown("---")
    
    # Add new task form
    show_add_task_form(company_id)
    
    st.markdown("---")
    
    # Show active tasks
    if active_tasks:
        st.subheader("🔄 Active Tasks")
        show_task_list(active_tasks, company_id)
    else:
        st.info("No active tasks")
    
    # Show completed tasks (collapsible)
    if completed_tasks:
        with st.expander(f"✅ Completed Tasks ({len(completed_tasks)})", expanded=False):
            show_task_list(completed_tasks, company_id, show_actions=False)


def show_add_task_form(company_id: str):
    """Form to add a new task"""
    st.subheader("➕ Add New Task")
    
    with st.form("add_task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Task Title", placeholder="Enter task title...")
            assignee = st.text_input("Assignee", placeholder="Enter assignee name...")
        
        with col2:
            due_date = st.date_input("Due Date", value=date.today())
        
        submitted = st.form_submit_button("Add Task", type="primary")
        
        if submitted:
            if title and assignee:
                try:
                    task = add_task(company_id, title, due_date, assignee)
                    st.success(f"✅ Task '{title}' added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error adding task: {str(e)}")
            else:
                st.error("Please fill in all required fields")


def show_task_list(tasks: List[Task], company_id: str, show_actions: bool = True):
    """Display a list of tasks"""
    for task in tasks:
        with st.container():
            # Task card styling
            task_color = "🟢" if task.status == "active" else "✅"
            due_date_color = get_due_date_color(task.due_date)
            
            # Create columns for task display
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                # Clickable task title
                if st.button(f"{task_color} {task.title}", key=f"task_title_{task.id}", help="Click to edit"):
                    st.session_state[f"editing_task_{task.id}"] = True
            
            with col2:
                st.write(f"**Assignee:** {task.assignee}")
            
            with col3:
                st.write(f"**Due:** {task.due_date.strftime('%Y-%m-%d')} {due_date_color}")
            
            with col4:
                if show_actions:
                    # Quick action buttons
                    if st.button("✓", key=f"complete_{task.id}", help="Mark as completed"):
                        update_task(task.id, status="completed")
                        st.success("Task completed!")
                        st.rerun()
                    
                    if st.button("🗑", key=f"delete_{task.id}", help="Delete task"):
                        if st.session_state.get(f"confirm_delete_{task.id}", False):
                            delete_task(task.id)
                            st.success("Task deleted!")
                            st.rerun()
                        else:
                            st.session_state[f"confirm_delete_{task.id}"] = True
                            st.warning("Click again to confirm deletion")
            
            # Task edit form (appears when task title is clicked)
            if st.session_state.get(f"editing_task_{task.id}", False):
                show_task_edit_form(task, company_id)
            
            st.markdown("---")


def show_task_edit_form(task: Task, company_id: str):
    """Form to edit an existing task"""
    st.markdown("**Edit Task**")
    
    with st.form(f"edit_task_form_{task.id}", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            new_title = st.text_input("Task Title", value=task.title, key=f"edit_title_{task.id}")
            new_assignee = st.text_input("Assignee", value=task.assignee, key=f"edit_assignee_{task.id}")
        
        with col2:
            new_due_date = st.date_input("Due Date", value=task.due_date, key=f"edit_due_{task.id}")
            new_status = st.selectbox("Status", ["active", "completed"], 
                                    index=0 if task.status == "active" else 1,
                                    key=f"edit_status_{task.id}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            save_clicked = st.form_submit_button("💾 Save Changes", type="primary")
        
        with col2:
            cancel_clicked = st.form_submit_button("❌ Cancel")
        
        with col3:
            delete_clicked = st.form_submit_button("🗑 Delete Task", type="secondary")
        
        if save_clicked:
            try:
                update_task(task.id, 
                          title=new_title,
                          assignee=new_assignee,
                          due_date=new_due_date,
                          status=new_status)
                st.success("✅ Task updated successfully!")
                st.session_state[f"editing_task_{task.id}"] = False
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error updating task: {str(e)}")
        
        if cancel_clicked:
            st.session_state[f"editing_task_{task.id}"] = False
            st.rerun()
        
        if delete_clicked:
            try:
                delete_task(task.id)
                st.success("✅ Task deleted successfully!")
                st.session_state[f"editing_task_{task.id}"] = False
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error deleting task: {str(e)}")


def get_due_date_color(due_date: date) -> str:
    """Get color indicator for due date"""
    today = date.today()
    days_until_due = (due_date - today).days
    
    if days_until_due < 0:
        return "🔴"  # Overdue
    elif days_until_due == 0:
        return "🟡"  # Due today
    elif days_until_due <= 3:
        return "🟠"  # Due soon
    else:
        return "🟢"  # Not urgent


def show_task_summary_card(company_id: str):
    """Compact task summary for company cards"""
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
