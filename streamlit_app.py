"""
Streamlit Cloud entry point for DVC Portfolio Dashboard Sandbox
"""
import streamlit as st
import os
import sys

# Add the current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Set local development mode for mock data
os.environ['LOCAL_DEV'] = 'True'

# Set page config first
st.set_page_config(
    page_title="DVC Portfolio Dashboard",
    layout='wide',
    page_icon = "resources/favicon.png"
)

# Import and run the dashboard directly
try:
    from app.dashboard.navigation import show_navigation
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please ensure the app directory is available in the root")
    st.stop()

# Run the main navigation
show_navigation()
