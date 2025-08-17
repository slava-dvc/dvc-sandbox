import streamlit as st
from .fund import fund_page
from .company import company_page
from .jobs import jobs_page
from .pipeline import pipeline_page
__all__ = ['show_navigation']


def show_navigation():
    """
    Display common navigation for the dashboard
    
    Args:
        current_page: Current page identifier ('fund', 'jobs', etc.)
    """
    pages = [
        st.Page(fund_page, title="Funds"),
        st.Page(company_page, title="Companies"),
        st.Page(pipeline_page, title="Pipeline"),
        st.Page(jobs_page, title="Jobs"),
    ]
    pg=st.navigation(pages, position="top")
    pg.run()
