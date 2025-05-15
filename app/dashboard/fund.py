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


__all__ = ['show_fund_page']


def show_fund_selector(investments):
    funds = investments['Fund']
    unique_funds = funds[funds.notna()].unique()
    fund_options = list(reversed(sorted(unique_funds)))
    selected_funds = st.multiselect("Pick the fund(s)", fund_options, default=None, placeholder="Pick the fund(s)...", label_visibility='collapsed')
    return selected_funds


def show_keymetrics(investments: pd.DataFrame, companies: pd.DataFrame):
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
        company_id = company_summary.company_id
        company_name = company_summary.name
        company_website = company_summary.website
        company_stage = company_summary.stage
        initial_fund = company_summary.initial_fund
        initial_valuation = company_summary.initial_valuation
        current_valuation = company_summary.current_valuation


        company_last_update = company_summary.last_update

        with st.container(border=True):
            col1, col2, col3 = st.columns([1, 10, 1], gap='small')

            with col1:
                if company_summary.logo_url:
                    try:
                        st.image(company_summary.logo_url, width=64)
                    except Exception:
                        st.write("📊")
                else:
                    st.write("📊")

            with col2:
                header = []
                c1, c2 = st.columns(2)
                with c1:
                    if company_website and isinstance(company_website, str):
                        header.append(f"**[{company_name}]({company_website})**")
                    else:
                        header.append(f"**{company_name}**")
                    header.append(company_stage)
                    if company_last_update:
                        now = datetime.now()
                        if company_last_update < now - datetime.timedelta(days=7):
                            header.append(f"🕐 This week")
                        elif company_last_update < now - datetime.timedelta(days=30):
                            header.append(f"🕐 This month")
                        else:
                            header.append(f"🕐 {company_last_update.strftime('%d %b %Y')}")
                    else:
                        header.append("❌ No updates")
                    st.markdown("&nbsp; | &nbsp;".join(header))
                with c2:
                    # Display new highlights badge
                    new_highlights = company_summary.new_highlights
                    if isinstance(new_highlights, list) and len(new_highlights) > 0:
                        text = '⚠️ ' + ', '.join([h.replace('_', ' ').capitalize() for h in new_highlights])
                        st.badge(text, color='green')
                    
                    # Display metrics badges if available
                    if company_summary.spectr_metrics:
                        metrics = company_summary.spectr_metrics
                        
                        # Display metrics in a cleaner way
                        metrics_to_display = []
                        
                        # Check available metrics and format them
                        if 'employee_count' in metrics and metrics['employee_count']['value'] is not None:
                            emp_count = metrics['employee_count']['value']
                            emp_change = metrics['employee_count']['change']
                            if emp_change is not None:
                                badge_text, badge_color = format_metric_badge(emp_change, "1mo")
                                if badge_text:
                                    metrics_to_display.append(("Employee Count", emp_count, badge_text, badge_color))
                        
                        if 'web_visits' in metrics and metrics['web_visits']['value'] is not None:
                            web_visits = metrics['web_visits']['value']
                            web_change = metrics['web_visits']['change']
                            if web_change is not None:
                                badge_text, badge_color = format_metric_badge(web_change, "1mo")
                                if badge_text:
                                    metrics_to_display.append(("Web Visits", web_visits, badge_text, badge_color))
                        
                        if 'linkedin_followers' in metrics and metrics['linkedin_followers']['value'] is not None:
                            li_followers = metrics['linkedin_followers']['value']
                            li_change = metrics['linkedin_followers']['change']
                            if li_change is not None:
                                badge_text, badge_color = format_metric_badge(li_change, "1mo")
                                if badge_text:
                                    metrics_to_display.append(("LinkedIn", li_followers, badge_text, badge_color))
                        
                        # Display the metrics as badges that match the design
                        for i, (label, value, badge_text, badge_color) in enumerate(metrics_to_display):
                            # Format to match the badge.png design
                            st.markdown(f"""
                            <div style="margin-bottom: 5px;">
                                <div style="font-weight: 500;">{label}: {value}</div>
                                <span style="background-color: {'#ffcdd2' if badge_color == 'red' else '#c8e6c9'}; 
                                            color: {'#d32f2f' if badge_color == 'red' else '#2e7d32'}; 
                                            padding: 2px 8px; 
                                            border-radius: 16px; 
                                            font-size: 12px;">
                                    {badge_text}
                                </span>
                            </div>
                            """, unsafe_allow_html=True)

                # All information in one row using 3 smaller columns
                c1, c2, c3, c4 = st.columns(4)
                c1.markdown(f"Initial Fund: **{initial_fund}**")
                c2.markdown(f"Initial Val: **{format_as_dollars(initial_valuation, 'N/A')}**")
                c3.markdown(f"Current Val: **{format_as_dollars(current_valuation, 'N/A')}**")

            with col3:
                def update_company_id(company_id):
                    st.query_params.update({'company_id': company_id})

                # Push the button higher on the row by adding padding
                st.write("")  # Small spacer to align with company name
                st.button("View", key=f"open_company_{company_id}", on_click=update_company_id, args=[company_id], use_container_width=True)

            # # # Thinner divider
            # st.markdown("<hr style='margin: 0.25em 0.25em; border-width: 0; background-color: #e0e0e0; height: 1px'>",
            #             unsafe_allow_html=True)

    st.write(f"Total companies: {len(companies_to_display)}")


def show_fund_page(investments, companies, updates):
    selected_funds = show_fund_selector(investments)
    st.markdown("---")
    
    if selected_funds:
        investments = investments[investments['Fund'].isin(selected_funds)]
        companies = companies[companies['Initial Fund Invested From'].isin(selected_funds)]

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
    st.divider()
    show_companies(companies, updates)
