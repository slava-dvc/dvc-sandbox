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


__all__ = ['show_fund_page']


@dataclass
class CompanySummary:
    """Represents a company with its relevant data."""
    company_id: str
    name: str
    website: Optional[str] = None
    stage: Optional[str] = None
    status: Optional[str] = None
    initial_fund: Optional[str] = None
    initial_valuation: Optional[Union[str, float, int]] = None
    current_valuation: Optional[Union[str, float, int]] = None
    logo_url: Optional[str] = None
    last_update: Optional[Any] = None
    new_highlights: Optional[List[str]] = None

    def __lt__(self, other):
        status_map = {
            "Invested": 0,
            "Exit": -2,
            "Offered To Invest": 2,
            "Write-off": -1,
        }

        def get_sorting_tuple(obj):
            highlights_count = 0 if not isinstance(obj.new_highlights, list) else len(obj.new_highlights)
            last_update = datetime.now() if not isinstance(obj.last_update, datetime.datetime) else obj.last_update
            return (
                highlights_count,
                last_update,
                status_map.get(obj.status, 0),
            )
        return get_sorting_tuple(self) < get_sorting_tuple(other)

    @classmethod
    def from_row(cls, company, company_id, last_update=None):

        stage = company['Company Stage']
        if isinstance(stage, list) and stage:
            stage = stage[0]
        else:
            stage = 'N/A'

        # Handle current valuation - if it's a list, take the first element
        current_val = company['Last Valuation/cap (from DVC Portfolio 3)']
        if isinstance(current_val, list) and current_val:
            current_val = current_val[0]
        else:
            current_val = 'N/A'
        initial_val = company['Entry Valuation /cap (from DVC Portfolio 3)']
        if isinstance(initial_val, list) and initial_val:
            initial_val = initial_val[0]
        else:
            initial_val = 'N/A'

        return cls(
            company_id=company_id,
            name=company['Company'],
            status=company['Status'],
            website=company['URL'],
            stage=stage,
            initial_fund=company['Initial Fund Invested From'],
            initial_valuation=initial_val,
            current_valuation=current_val,
            logo_url=get_preview(company['Logo']),
            last_update=last_update,
            new_highlights=company.get('new_highlights')
        )


def show_fund_selector(investments):
    funds = investments['Fund']
    unique_funds = funds[funds.notna()].unique()
    fund_options = list(reversed(sorted(unique_funds)))
    selected_fund = st.selectbox("Pick the fund", fund_options, index=None, placeholder="Pick the fund...", label_visibility='collapsed')
    return selected_fund


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
        CompanySummary.from_row(company, company_id, company_id_to_last_update.get(company_id))
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
                    new_highlights = company_summary.new_highlights
                    if isinstance(new_highlights, list) and len(new_highlights) > 0:
                        text = '⚠️ ' + ', '.join([h.replace('_', ' ').capitalize() for h in new_highlights])
                        st.badge(text, color='green')

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
    selected_fund = show_fund_selector(investments)
    st.markdown("---")
    investments = investments[investments['Fund'] == selected_fund] if selected_fund else investments
    companies = companies[companies['Initial Fund Invested From'] == selected_fund] if selected_fund else companies

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
