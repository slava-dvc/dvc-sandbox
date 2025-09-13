import pandas as pd
import streamlit as st
import plotly.express as px
from app.dashboard.formatting import format_as_dollars
from app.dashboard.data import get_investments, get_companies_v2, get_updates
from app.shared.company import Company, CompanyStatus
from app.dashboard.highlights import show_highlights_for_company

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

            # Show investment fund if available
            fund = company.ourData.get('investingFund') if company.ourData else None
            if fund:
                header.append(f"Fund: {fund}")

            st.markdown("&nbsp; | &nbsp;".join(header))

            # Show valuation info
            c1, c2 = st.columns(2, gap='small')

            # Initial valuation
            initial_val = company.ourData.get('entryValuation') if company.ourData else None
            if initial_val:
                c1.markdown(f"Entry: **{format_as_dollars(initial_val)}**")

            # Current valuation
            current_val = company.ourData.get('latestValuation')
            if current_val and isinstance(current_val, list) and current_val:
                c2.markdown(f"Latest: **{format_as_dollars(current_val[0])}**")

        with signals_column:
            highlights_cnt = show_highlights_for_company(company)
            if not highlights_cnt:
                st.info("No signals for this company.")

        with button_column:
            st.link_button("View", url=f'/company_page?company_id={company.id}', width=192)


def show_companies(companies: list[Company], updates: pd.DataFrame):
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
        sort_options = ["Default", "Current Val (High to Low)", "Current Val (Low to High)",
                       "Initial Val (High to Low)", "Initial Val (Low to High)",
                       "Name (A to Z)", "Name (Z to A)"]
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
    if selected_sort != "Default":
        if "Name" in selected_sort:
            key_func = lambda c: c.name.lower()
            reverse = "Z to A" in selected_sort
        else:
            def get_numeric_val(company, val_type):
                if val_type == "current":
                    val = company.ourData.get('latestValuation') if company.ourData else None
                    if isinstance(val, list) and val:
                        val = val[0]
                else:  # initial
                    val = company.ourData.get('entryValuation') if company.ourData else None

                if val is None:
                    return 0
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return 0

            if "Current Val" in selected_sort:
                key_func = lambda c: get_numeric_val(c, "current")
            else:  # Initial Val
                key_func = lambda c: get_numeric_val(c, "initial")

            reverse = "High to Low" in selected_sort

        filtered_companies.sort(key=key_func, reverse=reverse)

    # Display company cards
    for company in filtered_companies:
        show_company_card(company)

    st.write(f"Total companies: {len(filtered_companies)}")


def fund_page():
    with st.spinner("Loading investments..."):
        investments = get_investments()

    with st.spinner("Loading updates..."):
        updates = get_updates()

    selected_funds = show_fund_selector(investments)
    st.markdown("---")

    # Build MongoDB query for companies
    query = {
        'status': {'$in': [str(CompanyStatus.INVESTED), str(CompanyStatus.EXIT), str(CompanyStatus.WRITE_OFF)]},
        'ourData.investingFund': {'$exists': True, '$ne': None}
    }

    # Add fund filtering to query if funds are selected
    if selected_funds:
        query['ourData.investingFund'] = {'$in': selected_funds}
        investments = investments[investments['Fund'].isin(selected_funds)]

    with st.spinner("Loading companies..."):
        companies = get_companies_v2(query)

    show_key_metrics(investments, companies)
    st.markdown("---")
    chart_col1, chart_col2 = st.columns([1, 1])
    with chart_col1:
        show_counted_pie(
            companies=companies,
            title="Stage when we invested",
            column="entryStage"
        )
    with chart_col2:
        show_counted_pie(
            companies=companies,
            title="Companies by industry",
            column="mainIndustry"
        )
    st.divider()
    show_companies(companies, updates)
