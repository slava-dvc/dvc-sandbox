"""
Streamlit Cloud entry point for DVC Portfolio Dashboard Sandbox
"""
import streamlit as st
import os
import sys

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set local development mode for mock data
os.environ['LOCAL_DEV'] = 'True'

# Set page config first
st.set_page_config(
    page_title="DVC Portfolio Dashboard",
    layout='wide',
    page_icon = "resources/favicon.png"
)

# Import and run the dashboard directly
from app.dashboard.navigation import show_navigation

# Run the main navigation
show_navigation()
