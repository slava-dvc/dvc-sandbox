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

# Import and run the dashboard
from app.dashboard.main import main

if __name__ == "__main__":
    main()
