import streamlit as st
from datetime import datetime, timezone
from typing import Optional
from app.shared.task import Task
from app.dashboard.data import update_task

@st.dialog("Add Task Results")
def show_task_results_dialog(task: Task):
    """
    World-class unified dialog for adding task results.
    Follows Streamlit best practices with natural auto-sizing.
    """
    
    # Minimal CSS - only for responsive width, NO height constraints
    st.markdown("""
    <style>
    /* Responsive width only - let Streamlit handle height naturally */
    [data-testid="stDialog"] > div {
        width: min(600px, 90vw);
    }
    
    /* Let textarea auto-size naturally - no height constraints */
    [data-testid="stDialog"] textarea {
        width: 100%;
        resize: vertical;
    }
    
    @media (max-width: 768px) {
        [data-testid="stDialog"] > div {
            width: 95vw;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Clean content structure
    st.subheader("Add Task Results")
    st.markdown(f"**Task:** {task.text}")
    st.divider()
    
    # Form with natural sizing
    with st.form(key=f"task_results_{task.id}", clear_on_submit=False):
        # No height parameter - let Streamlit auto-size
        results = st.text_area(
            "Results",
            placeholder="Describe the outcome, findings, or results from completing this task...",
            label_visibility="visible",
            help="Enter detailed results or findings"
        )
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            save = st.form_submit_button(
                "💾 Save Results",
                type="primary",
                use_container_width=True
            )
        
        with col2:
            cancel = st.form_submit_button(
                "❌ Cancel",
                use_container_width=True
            )
        
        # Handle actions without blocking sleep
        if save:
            if results and results.strip():
                try:
                    update_task(
                        task.id,
                        status="completed",
                        completed_at=datetime.now(timezone.utc),
                        outcome=results.strip()
                    )
                    # Clean up session state
                    if f"reactivated_task_outcome_{task.id}" in st.session_state:
                        del st.session_state[f"reactivated_task_outcome_{task.id}"]
                    st.success("✅ Results saved!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.warning("⚠️ Please enter results before saving")
        
        if cancel:
            try:
                update_task(
                    task.id,
                    status="active",
                    completed_at=None,
                    outcome=None
                )
                if f"reactivated_task_outcome_{task.id}" in st.session_state:
                    del st.session_state[f"reactivated_task_outcome_{task.id}"]
                st.info("ℹ️ Task reverted to active")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")
