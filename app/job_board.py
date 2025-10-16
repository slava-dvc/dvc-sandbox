import streamlit as st
from app import dashboard

st.set_page_config(
    page_title="DVC Portfolio Job Board",
    layout="wide",
    page_icon="resources/favicon.png"
)

dashboard.jobs_page()
