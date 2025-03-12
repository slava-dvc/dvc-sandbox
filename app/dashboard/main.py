import sys
import pandas as pd
import streamlit as st
from pathlib import Path
from app.integrations import airtable
from data import get_investments


st.set_page_config(
    page_title="DVC Portfolio Management",
    layout="wide"
)


def login_screen():
    st.header("This app is private.")
    st.subheader("Please log in.")
    st.button("Log in with Google", on_click=st.login)


def is_email_allowed():
    email = st.experimental_user.email
    return email == 'galilei.mail@gmail.com' or email.endswith('davidovs.com')


def handle_not_authorized():
    st.navigation.hidden = True
    st.error("You are not authorized to access this app.")
    st.write("Sorry, your email address is not authorized to access this dashboard.")
    st.write("Please contact the administrator if you believe this is an error.")
    st.button("Log out", on_click=st.logout)


def show_fund_selector(investments):
    fund_options = ['Select...'] + list(reversed(sorted(investments['Fund'].unique())))
    selected_fund = st.selectbox("Pick the fund", fund_options)
    return selected_fund if selected_fund != 'Select...' else None


def show_keymetrics(investments: pd.DataFrame):
    fund_metrics = {
        "Deployed Capital": investments['Amount Invested'].sum(),
        "Total Deals": len(investments),
        "Initial Investments": len(investments) - investments['Is it follow-on?'].sum(),
        "Follow ons": investments['Is it follow-on?'].sum(),
        "NOEC": 'TBD',
        "Portf.": 'TBD',
        "Write offs": 'TBD',
        "TVPI": 'TBD',
    }

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Deployed Capital", fund_metrics["Deployed Capital"])
        st.metric("NOEC", fund_metrics["NOEC"])

    with col2:
        st.metric("Total Deals", fund_metrics["Total Deals"])
        st.metric("Portf.", fund_metrics["Portf."])

    with col3:
        st.metric("Initial Investments", fund_metrics["Initial Investments"])
        st.metric("Write offs", fund_metrics["Write offs"])

    with col4:
        st.metric("Follow ons", fund_metrics["Follow ons"])
        st.metric("TVPI", fund_metrics["TVPI"])

    pass


def show_fund():
    all_investments = get_investments()
    selected_fund = show_fund_selector(all_investments)
    investments = all_investments[all_investments['Fund'] == selected_fund] if selected_fund else all_investments
    show_keymetrics(investments)


if not st.experimental_user.is_logged_in:
    login_screen()
elif not is_email_allowed():
    handle_not_authorized()
else:
    show_fund()
