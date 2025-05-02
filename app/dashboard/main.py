import sys
import pandas as pd
import streamlit as st
import plotly.express as px

from pathlib import Path
from app.integrations import airtable
from app.dashboard.data import get_investments, get_companies, get_investments_config, get_companies_config, replace_ids_with_values

EMAIL_ALLOW_LIST = {
    'galilei.mail@gmail.com',
    'neverproof@gmail.com',
}

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
    return email in EMAIL_ALLOW_LIST or email.endswith('davidovs.com')


def handle_not_authorized():
    st.navigation.hidden = True
    st.error("You are not authorized to access this app.")
    st.write("Sorry, your email address is not authorized to access this dashboard.")
    st.write("Please contact the administrator if you believe this is an error.")
    st.button("Log out", on_click=st.logout)


def show_fund_selector(investments):
    fund_options = list(reversed(sorted(investments['Fund'].notna().unique())))
    selected_fund = st.selectbox("Pick the fund", fund_options, index=None, placeholder="Select...")
    return selected_fund


def show_keymetrics(investments: pd.DataFrame, companies: pd.DataFrame):
    fund_metrics = {
        "Deployed Capital": investments['Amount Invested'].sum(),
        "Total Deals": len(investments),
        "Initial Investments": len(investments) - investments['Is it follow-on?'].sum(),
        "Follow ons": investments['Is it follow-on?'].sum(),
        "MOIC": 'TBD',
        "Exits": sum(list(companies.Status == 'Exit')),
        "Write offs": sum(list(companies['Status'] == 'Write-off')),
        "TVPI": 'TBD',
    }

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Deployed Capital", fund_metrics["Deployed Capital"])
        st.metric("MOIC", fund_metrics["MOIC"])

    with col2:
        st.metric("Total Deals", fund_metrics["Total Deals"])
        st.metric("Exits", fund_metrics["Exits"])

    with col3:
        st.metric("Initial Investments", fund_metrics["Initial Investments"])
        st.metric("Write offs", fund_metrics["Write offs"])

    with col4:
        st.metric("Follow ons", fund_metrics["Follow ons"])
        st.metric("TVPI", fund_metrics["TVPI"])


def show_counted_pie(df: pd.DataFrame, title: str, column):
    st.subheader(title)

    # Count values for the specified column
    value_counts = df[column].value_counts().reset_index()
    value_counts.columns = [column, 'Count']
    # st.dataframe(value_counts)

    fig = px.pie(
        value_counts, values='Count', names=column, title=None,
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)


def show_companies(companies: pd.DataFrame):
    st.subheader("Portfolio Companies")
    search_query = st.text_input("Search Company", "", placeholder='Search company by name...', label_visibility='hidden')
    companies_to_display = companies[
        ['Company', 'URL', 'Initial Valuation', 'Current Valuation', 'Current Stage', 'Main Industry']
    ]
    companies_to_display.insert(0, 'Open', [f"/company?id={x}" for x in companies.index])
    if search_query:
        index = companies_to_display['Company'].str.lower().str.contains(search_query, na=False)
        companies_to_display = companies_to_display[index]
    st.dataframe(
        companies_to_display,
        column_config={
            'Open': st.column_config.LinkColumn("Open", display_text="Learn more"),
        },
        hide_index=True,
        use_container_width=True
    )
    st.write(f"Total companies: {len(companies_to_display)}")


def show_fund():
    all_investments = get_investments()
    all_companies = get_companies()
    selected_fund = show_fund_selector(all_investments)
    st.markdown("---")
    investments = all_investments[all_investments['Fund'] == selected_fund] if selected_fund else all_investments
    companies = all_companies[all_companies['Initial Fund Invested From'] == selected_fund] if selected_fund \
        else all_companies[~all_companies['Initial Fund Invested From'].isna()]

    investments = replace_ids_with_values(get_investments_config(), investments)
    companies = replace_ids_with_values(get_companies_config(), companies)

    show_keymetrics(investments, companies)
    st.markdown("---")
    chart_col1, chart_col2 = st.columns([1, 1])
    with chart_col1:
        show_counted_pie(
            df=companies[companies['Status'].isin(["Invested", "Exit", "Write-off"])],
            title="Stage when we invested",
            column="Stage when we invested"
        )
    with chart_col2:
        show_counted_pie(
            df=companies[companies['Status'].isin(["Invested", "Exit", "Write-off"])],
            title="Companies by industry",
            column="Main Industry"
        )
    st.markdown("---")
    show_companies(companies)


if not st.experimental_user.is_logged_in:
    login_screen()
elif not is_email_allowed():
    handle_not_authorized()
else:
    show_fund()
