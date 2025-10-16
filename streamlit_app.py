"""
Streamlit Cloud entry point for DVC Portfolio Dashboard Sandbox
"""
import streamlit as st
import os
import sys

# Add the synapse directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
synapse_dir = os.path.join(current_dir, 'synapse')
sys.path.insert(0, synapse_dir)

# Set local development mode for mock data
os.environ['LOCAL_DEV'] = 'True'

# Set page config first
st.set_page_config(
    page_title="DVC Portfolio Dashboard",
    layout='wide',
    page_icon = "synapse/resources/favicon.png"
)

# Import and run the dashboard directly
try:
    from app.dashboard.navigation import show_navigation
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please ensure you're running from the synapse directory")
    st.stop()

# Run the main navigation
show_navigation()
