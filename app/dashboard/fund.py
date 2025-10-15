import pandas as pd
import streamlit as st
import plotly.express as px
from app.dashboard.formatting import format_as_dollars
from app.dashboard.data import get_investments, get_companies_v2
from app.shared.company import Company, CompanyStatus
from app.dashboard.highlights import show_highlights_for_company
from app.foundation.primitives import datetime

__all__ = ['fund_page']


def show_fund_selector(investments):
    funds = investments['Fund']
    unique_funds = funds[funds.notna()].unique()
    fund_options = list(reversed(sorted(unique_funds)))
    selected_funds = st.multiselect("Pick the fund(s)", fund_options, default=None, placeholder="Pick the fund(s)...", label_visibility='collapsed')
    return selected_funds


def show_key_metrics(investments: pd.DataFrame, companies: list[Company]):
    fund_metrics = {
        "Deployed Capital": format_as_dollars(investments['Amount Invested'].sum()),
        "Total Deals": len(investments),
        "Initial Investments": len(investments) - investments['Is it follow-on?'].sum(),
        "Follow ons": investments['Is it follow-on?'].sum(),
        "MOIC": 'TBD',
        "Exits": sum(1 for c in companies if c.status == CompanyStatus.EXIT),
        "Write offs": sum(1 for c in companies if c.status == CompanyStatus.WRITE_OFF),
        "Markup": investments['Markup?'].sum(),
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
        st.metric("Markup", fund_metrics["Markup"])


def show_counted_pie(companies: list[Company], title: str, column: str):
    st.subheader(title)

    # Extract values from Company objects
    values = []
    for company in companies:
        value = company.ourData.get(column) if company.ourData else None

        # Handle list values (take first element)
        if isinstance(value, list) and len(value) == 1:
            value = value[0]

        if value:
            values.append(value)

    if not values:
        st.info(f"No data available for {title}")
        return

    # Create DataFrame for plotting
    df = pd.DataFrame({column: values})
    value_counts = df[column].value_counts().reset_index()
    value_counts.columns = [column, 'Count']

    fig = px.pie(
        value_counts, values='Count', names=column, title=None,
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)


def show_company_card(company: Company):
    """Display a company card with basic info and highlights."""
    company_name = company.name
    company_website = company.website
    company_stage = company.ourData.get('currentStage') if company.ourData else None

    with st.container(border=True):
        logo_column, info_column, signals_column, button_column = st.columns([1, 6, 4, 1], gap='small', vertical_alignment='center')

        with logo_column:
            linkedin_url = company.linkedInData.get('logo') if isinstance(company.linkedInData, dict) else None
            fallback_url = f'https://placehold.co/128x128?text={company_name}'
            st.image(linkedin_url if linkedin_url else fallback_url, width=128)

        with info_column:
            header = []
            if company_website and isinstance(company_website, str):
                header.append(f"**[{company_name}]({company_website})**")
            else:
                header.append(f"**{company_name}**")

            if isinstance(company_stage, str):
                header.append(company_stage or "—")
            else:
                header.append("—")

            st.markdown("&nbsp; | &nbsp;".join(header))

            # Show valuation info
            c1, c2 = st.columns(2, gap='small')

            performanceOutlook = company.ourData.get('performanceOutlook')
            unrealizedPaperGain = company.ourData.get('unrealizedPaperGain', 0)
            amountInvested = company.ourData.get('amountInvested', 0)
            currentPaperValue = company.ourData.get('currentPaperValue', 0)
            revaluation = company.ourData.get('revaluation', 0)

            c1.markdown(f"Total invested: **{format_as_dollars(amountInvested)}**")
            c1.write(performanceOutlook)
            c2.markdown(f"Current paper value: **{format_as_dollars(currentPaperValue)}**")
            c2.markdown(f"Unrealized paper gain: **{format_as_dollars(unrealizedPaperGain)}**")
            c2.markdown(f"Revaluation: **{revaluation:0.2f}**")

        with signals_column:
            highlights_cnt = show_highlights_for_company(company)
            if not highlights_cnt:
                st.info("No signals for this company.")

        with button_column:
            st.link_button("View", url=f'/company_page?company_id={company.id}', width=192)


def show_companies(companies: list[Company]):
    st.subheader("Portfolio Companies")

    # Get unique values for filters
    unique_stages = list(set(
        company.ourData.get('currentStage')
        for company in companies
        if company.ourData and company.ourData.get('currentStage') and isinstance(company.ourData.get('currentStage'), str)
    ))
    unique_statuses = list(set(str(company.status) for company in companies if company.status))
    unique_expected_performance = list(set(
        company.ourData.get('performanceOutlook')
        for company in companies
        if company.ourData and company.ourData.get('performanceOutlook')
    ))

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
        sort_options = ["Default", "Name (A to Z)", "Name (Z to A)"]
        selected_sort = st.selectbox("Sort by", sort_options, index=0)

    # Apply filters
    filtered_companies = companies.copy()

    if search_query:
        filtered_companies = [c for c in filtered_companies
                            if search_query.lower() in c.name.lower()]

    if selected_stages:
        filtered_companies = [c for c in filtered_companies
                            if c.ourData and c.ourData.get('currentStage') in selected_stages]

    if selected_statuses:
        filtered_companies = [c for c in filtered_companies
                            if str(c.status) in selected_statuses]

    if selected_expected_performance:
        filtered_companies = [c for c in filtered_companies
                            if c.ourData and c.ourData.get('performanceOutlook') in selected_expected_performance]

    # Apply sorting
    if selected_sort == "Name (A to Z)":
        filtered_companies.sort(key=lambda c: c.name.lower())
    elif selected_sort == "Name (Z to A)":
        filtered_companies.sort(key=lambda c: c.name.lower(), reverse=True)
    else:  # Default
        # Default sorting: highlights count, last update, status priority
        def get_default_sort_key(company):
            # Highlights count (higher = better)
            highlights_count = 0
            if company.spectrData and 'new_highlights' in company.spectrData:
                highlights = company.spectrData['new_highlights']
                highlights_count = len(highlights) if isinstance(highlights, list) else 0

            # Last update (more recent = better)
            last_update = company.updatedAt or company.createdAt
            if last_update is None:
                last_update = datetime.datetime.min

            # Status priority
            status_map = {
                CompanyStatus.INVESTED: 0,
                CompanyStatus.OFFERED_TO_INVEST: 2,
                CompanyStatus.EXIT: -2,
                CompanyStatus.WRITE_OFF: -1,
            }
            status_priority = status_map.get(company.status, 1)

            return (highlights_count, last_update, status_priority)

        filtered_companies.sort(key=get_default_sort_key, reverse=True)

    # Display company cards
    for company in filtered_companies:
        show_company_card(company)

    st.write(f"Total companies: {len(filtered_companies)}")


def fund_page():
    """Fund page - disabled in test mode"""
    st.title("📊 Funds")
    
    st.info("🚧 **Fund page is not working in test mode**")
    st.write("The fund analytics require additional data columns that aren't available in the mock data.")
    
    st.markdown("---")
    
    st.subheader("🎯 Try these pages instead:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📋 Tasks**")
        st.write("Manage and track tasks across all companies")
        if st.button("Go to Tasks", type="primary"):
            st.switch_page("all_tasks_page")
    
    with col2:
        st.markdown("**🏢 Companies**")
        st.write("View detailed company information and metrics")
        if st.button("Go to Companies"):
            st.switch_page("company_page")
    
    with col3:
        st.markdown("**📈 Pipeline**")
        st.write("Track companies through investment pipeline")
        if st.button("Go to Pipeline"):
            st.switch_page("pipeline_page")
    
    st.markdown("---")
    
    st.write("**💡 Note:** In production mode with real data, this page would show:")
    st.write("• Fund performance metrics")
    st.write("• Investment analytics and charts") 
    st.write("• Portfolio company tracking")
    st.write("• Financial reporting dashboards")
