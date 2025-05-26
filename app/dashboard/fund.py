import sys
import pandas as pd
import streamlit as st
import plotly.express as px
from typing import Optional, Union, List, Any
from dataclasses import dataclass
from pathlib import Path
from app.integrations import airtable
from app.dashboard.data import get_investments, get_companies, get_investments_config, get_companies_config, replace_ids_with_values
from app.dashboard.formatting import format_as_dollars, get_preview
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


def show_companies(companies: pd.DataFrame, updates: pd.DataFrame):
    # Create summaries first
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
        for company_id, company in companies.iterrows()
    ]
    
    # Get unique values for filters from summaries
    unique_stages = list(set(s.stage for s in summaries if s.stage))
    unique_statuses = list(set(s.status for s in summaries if s.status))
    unique_expected_performance = list(set(s.expected_performance for s in summaries if s.expected_performance))
    st.subheader("Portfolio Companies")

    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])

    with col1:
        search_query = st.text_input("Company Name", "", placeholder='Type name...', )

    with col2:
        # Stage filter
        selected_stages = st.multiselect("Stage", unique_stages, placeholder="Select stages...")
    
    with col3:
        # Status filter  
        selected_statuses = st.multiselect("Status", unique_statuses, placeholder="Select statuses...")
    
    with col4:
        # Expected Performance filter
        selected_expected_performance = st.multiselect("Expected Performance", unique_expected_performance, placeholder="Select performance...")
    
    with col5:
        # Sort by dropdown
        sort_options = ["Default", "Current Val (High to Low)", "Current Val (Low to High)", 
                       "Initial Val (High to Low)", "Initial Val (Low to High)",
                       "Last Update (Newest First)", "Last Update (Oldest First)"]
        selected_sort = st.selectbox("Sort by", sort_options, index=0)
    
    # Apply filters to summaries
    filtered_summaries = summaries.copy()
    
    if search_query:
        filtered_summaries = [s for s in filtered_summaries 
                            if search_query.lower() in s.name.lower()]
    
    if selected_stages:
        filtered_summaries = [s for s in filtered_summaries 
                            if s.stage in selected_stages]
    
    if selected_statuses:
        filtered_summaries = [s for s in filtered_summaries 
                            if s.status in selected_statuses]
    
    if selected_expected_performance:
        filtered_summaries = [s for s in filtered_summaries 
                            if s.expected_performance in selected_expected_performance]
    
    # Apply sorting to summaries
    if selected_sort != "Default":
        if "Last Update" in selected_sort:
            def get_update_date(summary):
                if isinstance(summary.last_update, datetime.datetime):
                    return summary.last_update
                return datetime.as_utc(datetime.datetime.min)

            key_func = get_update_date
            reverse = "Newest First" in selected_sort
        else:
            def get_numeric_val(summary, val_type):
                if val_type == "current":
                    val = summary.current_valuation
                else:  # initial
                    val = summary.initial_valuation
                
                if val is None:
                    return 0
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return 0
            
            if "Current Val" in selected_sort:
                key_func = lambda s: get_numeric_val(s, "current")
            else:  # Initial Val
                key_func = lambda s: get_numeric_val(s, "initial")
            
            reverse = "High to Low" in selected_sort
        
        filtered_summaries.sort(key=key_func, reverse=reverse)
    else:
        # Use default sorting (the __lt__ method in CompanySummary)
        filtered_summaries = list(reversed(sorted(filtered_summaries)))

    for company_summary in filtered_summaries:
        show_company_summary(company_summary)

    st.write(f"Total companies: {len(filtered_summaries)}")


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
