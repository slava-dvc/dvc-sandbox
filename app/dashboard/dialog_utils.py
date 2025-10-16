import streamlit as st
from datetime import datetime, timezone
from typing import Optional
from app.shared.task import Task
from app.dashboard.data import update_task
from app.dashboard.task_state_controller import save_result, cancel_result, get_user_id, clear_task_dialog_state

@st.dialog("Add Task Results", width="medium", dismissible=False)
def show_task_results_dialog(task: Task):
    """
    Dialog that shows previous results and allows adding new ones
    """
    from app.dashboard.task_result_history import format_result_history_for_display, get_result_count
    
    # Get formatted history for pre-fill
    previous_results = format_result_history_for_display(task)
    
    # Show previous results count if any
    result_count = get_result_count(task)
    if result_count > 0:
        st.info(f"📋 This task has {result_count} previous result(s). You can edit/append below.")
    
    with st.form(key=f"task_results_{task.id}", clear_on_submit=True):
        results = st.text_area(
            task.text,
            value=previous_results,  # PRE-FILL with history
            placeholder="Describe the outcome, findings, or results from completing this task...",
            help="Previous results are shown above. Edit or add new results.",
            height=200  # Taller for history
        )
        
        # Two explicit buttons - user must choose
        col1, col2 = st.columns(2)
        
        with col1:
            cancel = st.form_submit_button(
                "Cancel",
                use_container_width=True
            )
        
        with col2:
            save = st.form_submit_button(
                "Save Results",
                type="primary",
                use_container_width=True
            )
        
        # Handle Save
        if save:
            if not results or len(results.strip()) < 10:
                st.error("Outcome is required (minimum 10 characters)")
            else:
                try:
                    # Save with cumulative history
                    save_result(task.id, results, task)
                    
                    # Clean up session state using scoped keys
                    user_id = get_user_id()
                    clear_task_dialog_state(task.id, user_id)
                    
                    # Clean up legacy session state
                    if f"reactivated_task_outcome_{task.id}" in st.session_state:
                        del st.session_state[f"reactivated_task_outcome_{task.id}"]
                    
                    st.success("✅ Results saved!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        # Handle Cancel - revert task immediately
        if cancel:
            try:
                # Use controller to cancel result
                cancel_result(task.id)
                
                # Clean up session state using scoped keys
                user_id = get_user_id()
                clear_task_dialog_state(task.id, user_id)
                
                # Clean up legacy session state
                if f"reactivated_task_outcome_{task.id}" in st.session_state:
                    del st.session_state[f"reactivated_task_outcome_{task.id}"]
                
                st.info("ℹ️ Task reverted to active")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")
