# Only import what's needed for Streamlit
try:
    from .jobs import jobs_page
except ImportError:
    # Create minimal fallback if jobs module has issues
    def jobs_page():
        import streamlit as st
        st.write("Jobs page temporarily unavailable")