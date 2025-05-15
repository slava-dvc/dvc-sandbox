import sys
import pandas as pd
import streamlit as st
import plotly.express as px
from typing import Optional, Union, List, Any
from dataclasses import dataclass
from pathlib import Path
from app.integrations import airtable
from app.dashboard.data import get_investments, get_companies, get_investments_config, get_companies_config, replace_ids_with_values
from app.dashboard.formatting import format_as_dollars, get_preview, format_metric_badge
from app.foundation.primitives import datetime
from app.dashboard.company_summary import CompanySummary
from .company_summary import show_company_summary


__all__ = ['show_fund_page']


def show_fund_selector(investments):
    funds = investments['Fund']
    unique_funds = funds[funds.notna()].unique()
    fund_options = list(reversed(sorted(unique_funds)))
    selected_funds = st.multiselect("Pick the fund(s)", fund_options, default=None, placeholder="Pick the fund(s)...", label_visibility='collapsed')
    return selected_funds


def show_key_metrics(investments: pd.DataFrame, companies: pd.DataFrame):
    fund_metrics = {
        "Deployed Capital": format_as_dollars(investments['Amount Invested'].sum()),
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


def show_company_highlights(company: pd.Series):
    pass

def show_companies(companies: pd.DataFrame, updates: pd.DataFrame):
    st.subheader("Portfolio Companies")
    search_query = st.text_input("Search Company", "", placeholder='Search company by name...', label_visibility='hidden')
    if search_query:
        index = companies['Company'].str.lower().str.contains(search_query, na=False)
        companies_to_display = companies[index]
    else:
        companies_to_display = companies

    company_id_to_last_update = {}
    for update_id, update in updates.iterrows():
        company_id = update['Company Name']
        if isinstance(company_id, list):
            company_id = company_id[0]
            created = datetime.any_to_datetime(update['Created'])
            company_id_to_last_update.setdefault(company_id, created)
            company_id_to_last_update[company_id] = max(company_id_to_last_update[company_id], created)
    summaries = [
        CompanySummary.from_dict(company, company_id, company_id_to_last_update.get(company_id))
        for company_id, company in companies_to_display.iterrows()
    ]

    for company_summary in reversed(sorted(summaries)):
        show_company_summary(company_summary)

    st.write(f"Total companies: {len(companies_to_display)}")


def show_fund_page(investments, companies, updates):
    selected_funds = show_fund_selector(investments)
    st.markdown("---")
    
    if selected_funds:
        investments = investments[investments['Fund'].isin(selected_funds)]
        companies = companies[companies['Initial Fund Invested From'].isin(selected_funds)]

    show_key_metrics(investments, companies)
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
    st.divider()
    show_companies(companies, updates)
