import sys
import pandas as pd
import streamlit as st
import plotly.express as px

from pathlib import Path
from app.integrations import airtable
from app.dashboard.data import get_investments, get_companies, get_investments_config, get_companies_config, \
    replace_ids_with_values, get_portfolio, get_updates
from app.dashboard.formatting import format_as_dollars, get_preview

from app.dashboard.fund import show_fund_page
from app.dashboard.company import show_company_page

st.set_page_config(
    page_title="DVC Portfolio Dashboard", page_icon=":bar_chart:",
    layout='wide'
)

EMAIL_ALLOW_LIST = {
    'galilei.mail@gmail.com',
    'neverproof@gmail.com',
}

def login_screen():
    st.header("This app is private.")
    st.subheader("Please log in.")
    st.button("Log in with Google", on_click=st.login)


def is_email_allowed():
    email = st.user.email
    return email in EMAIL_ALLOW_LIST or email.endswith('davidovs.com')


def handle_not_authorized():
    st.navigation.hidden = True
    st.error("You are not authorized to access this app.")
    st.write("Sorry, your email address is not authorized to access this dashboard.")
    st.write("Please contact the administrator if you believe this is an error.")
    st.button("Log out", on_click=st.logout)



if not st.user.is_logged_in:
    login_screen()
elif not is_email_allowed():
    handle_not_authorized()
else:

    with st.spinner("Loading investments..."):
        investments = get_investments()
    with st.spinner("Loading companies..."):
        companies = get_companies()
        companies = companies[companies['Initial Fund Invested From'].notna()]
    with st.spinner("Loading updates..."):
        updates = get_updates()
    with st.spinner("Load dependencies..."):
        investments = replace_ids_with_values(get_investments_config(), investments)
        companies = replace_ids_with_values(get_companies_config(), companies)

    company_id = st.query_params.get('company_id')

    if company_id:
        show_company_page(investments, companies,updates, company_id)
    else:
        show_fund_page(investments, companies, updates)