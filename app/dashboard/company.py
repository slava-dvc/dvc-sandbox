import pandas as pd

import streamlit as st
from dataclasses import fields

from app.shared.company import Company, CompanyStatus
from app.foundation.primitives import datetime
from app.dashboard.formatting import format_as_dollars, format_as_percent, is_valid_number, get_preview
from app.dashboard.company_summary import show_highlights, TractionMetric, TractionMetrics, NewsItem, HIGHLIGHTS_DICT
from app.dashboard.data import get_investments, get_portfolio, get_updates, get_ask_to_task, get_people, get_companies_v2

__all__ = ['company_page']


def get_company_traction_metrics(company: Company) -> TractionMetrics:
    """Extract traction metrics from Company object."""
    if not company.spectrData or not company.spectrData.get('traction_metrics'):
        return TractionMetrics()
    return TractionMetrics.from_dict(company.spectrData['traction_metrics'])

def get_company_news(company: Company) -> list[NewsItem]:
    """Extract news items from Company object."""
    if not company.spectrData or not company.spectrData.get('news'):
        return []
    return [NewsItem.from_dict(news_item) for news_item in company.spectrData['news']]


def get_company_highlights(company: Company) -> list[str]:
    """Extract highlights from Company object."""
    if not company.spectrData:
        return []
    return company.spectrData.get('new_highlights', [])


def get_company_financial_data(company: Company) -> dict:
    """Extract financial data from Company object."""
    our_data = company.ourData or {}
    return {
        'runway': our_data.get('runway'),
        'revenue': our_data.get('revenue'),
        'burnrate': our_data.get('burnRate'),
        'customers_cnt': our_data.get('customerCount'),
        'expected_performance': our_data.get('performanceOutlook')
    }

def show_overview_row(key: str, value: str | None):
    """Helper function to display a key-value pair in two columns with proper formatting."""
    col1, col2 = st.columns([3, 7])
    with col1:
        st.markdown(f"**{key}**")
    with col2:
        if value and isinstance(value, str) and value.strip():
            st.markdown(value.replace('$', '\$'))
        else:
            st.markdown("—")

def show_traction_content(company: Company):
    """Display detailed traction information from ourData.traction."""
    traction = company.ourData.get('traction') if company.ourData else None
    
    if traction and isinstance(traction, str) and traction.strip():
        st.markdown(traction.replace('$', '\$'))
    else:
        st.info("No traction information available for this company.")

def show_overview(company: Company):
    """Display company overview information in a structured format."""
    
    # Main Industry
    main_industry = company.ourData.get('mainIndustry') if company.ourData else None
    industry_value = ', '.join(main_industry) if main_industry and isinstance(main_industry, list) else None
    show_overview_row("Main Industry", industry_value)

    # Summary - prefer ourData.summary over blurb
    summary = company.ourData.get('summary') if company.ourData else None
    if not summary:
        summary = company.blurb
    show_overview_row("Summary", summary)
    
    # Problem
    problem = company.ourData.get('problem') if company.ourData else None
    show_overview_row("Problem", problem)
    
    # Solution
    solution = company.spectrData.get('description') if company.spectrData else None
    show_overview_row("Solution", solution)
    
    # Why we're excited (skip for now)
    show_overview_row("Why we're excited", "Not implemented yet.")
    
    # Market Size
    market_size = company.ourData.get('marketSize') if company.ourData else None
    show_overview_row("Market Size", market_size)

    show_overview_row("Concerns", "Not implemented yet.")

    # Target Market
    target_market = company.ourData.get('targetMarket') if company.ourData else None
    show_overview_row("Target Market", target_market)


def show_company_basic_details(company: Company):
    logo_column, name_column, pitch_deck_column = st.columns([1, 5, 1], vertical_alignment="center")

    with logo_column:
        fallback_url = f'https://placehold.co/128x128?text={company.name}'
        st.image(fallback_url, width=128)

    with name_column:
        st.header(company.name)
        st.write(company.status.value if company.status else "Unknown")
        if company.website and isinstance(company.website, str):
            st.write(company.website)
        else:
            st.caption("No URL provided.")
        if company.blurb and isinstance(company.blurb, str):
            st.markdown(company.blurb.replace('$', '\$'))
        else:
            st.caption("No blurb provided.")

    with pitch_deck_column:
        pitch_deck_url = company.ourData.get('linkToDeck') if company.ourData else None
        if pitch_deck_url and isinstance(pitch_deck_url, str):
            st.link_button("Pitchdeck", pitch_deck_url)
        
        if st.button("Update Data"):
            st.info("Update Data functionality is not implemented yet.")


def show_company_investment_details(company: Company, investments: pd.DataFrame, portfolio: pd.DataFrame):
    col1, col2, col3, col4 = st.columns(4)
    company_id = company.airtableId
    company_investments = investments[investments['Company'].apply(lambda x: company_id in x if isinstance(x, list) else False)]
    portfolio_index = portfolio['Companies'].apply(lambda x: company_id in x if isinstance(x, list) else False)
    company_in_portfolio = None
    if sum(portfolio_index) == 1:
        company_in_portfolio = portfolio[portfolio_index].iloc[0]
    last_valuation = None
    initial_ownership = None
    current_ownership = None
    total_nav = None
    moic = None
    initial_investment = None
    total_investment=company_investments['Amount Invested'].sum()
    if company_in_portfolio is not None:
        last_valuation = company_in_portfolio['Last Valuation/cap']
        initial_investment = company_in_portfolio['Initial Investment']
        entry_valuation = company_in_portfolio['Entry Valuation /cap']
        initial_ownership = initial_investment / entry_valuation
        next_round_size = company_in_portfolio['Next round size?']
        dilution_estimate = 1 - (0 if next_round_size is None else next_round_size) / last_valuation
        follow_on_investment = company_in_portfolio['Follow on size'] or 0
        current_ownership = initial_ownership*dilution_estimate + follow_on_investment / last_valuation
        if current_ownership is None:
            current_ownership = initial_ownership
        total_nav = current_ownership * last_valuation
        moic = float(total_nav) / float(total_investment) if is_valid_number(total_investment) and total_investment > 0 else None

    with col1:
        st.metric("Invested", format_as_dollars(initial_investment))
        st.metric("Last Valuation", format_as_dollars(last_valuation))
    with col2:
        st.metric("InitialStake", format_as_percent(initial_ownership))
        st.metric("Total Inv", format_as_dollars(total_investment))

    with col3:
        st.metric("Current Stake", format_as_percent(current_ownership))
        st.metric("Total NAV", format_as_dollars(total_nav))

    with col4:
        st.metric("Initial Reval", "TBD")
        st.metric("MOIC", f"{moic:0.2f}" if is_valid_number(moic) else "—")


def show_asks(company: Company):
    company_id = company.airtableId
    with st.spinner("Loading..."):
        asks = get_ask_to_task()

    filtered_index = asks['Companies'].apply(lambda x: company_id in x if isinstance(x, list) else False)
    filtered_asks = asks[filtered_index & (asks['Status'] != 'Done')]
    if len(filtered_asks) == 0:
        st.info("No active asks for this company.")
    else:
        columns = ['ASK', 'Status', 'Type', 'Days Ago']
        st.dataframe(filtered_asks[columns], hide_index=True, use_container_width=True)


def show_last_updates_and_news(company: Company, updates):
    rows = []
    relevant_updates = updates['Company Name'].apply(lambda x: company.airtableId in x if isinstance(x, list) else False)
    company_updates = updates[relevant_updates].copy()
    company_updates.rename(columns={'Please provide any comments/questions': "Comment"}, inplace=True)
    for company_update in company_updates.itertuples():
        rows.append({
            'type': 'update',
            'publisher': 'Team',
            'url': None,
            'date': datetime.any_to_datetime(company_update.Created),
            'title': company_update.Comment,
        })
    news_after = datetime.now() - datetime.timedelta(days=90)
    company_news = get_company_news(company)
    for company_news_item in company_news:
        if company_news_item.date < news_after:
            continue
        rows.append({
            'type': 'news',
            'url': company_news_item.url,
            'date': company_news_item.date,
            'title': company_news_item.title,
            'publisher': company_news_item.publisher,
        })
    rows = sorted(rows, key=lambda x: x['date'], reverse=True)
    if len(rows) == 0:
        st.info("No news or updates for this company.")

    for row in rows:
        with st.container(border=True):
            text_column, date_column, button_column = st.columns([6, 1, 1], vertical_alignment='center')
            with text_column:
                title = row['title']
                if not isinstance(title, str):
                    title = "—"
                st.markdown(f"**{row['publisher']}**: {title.replace('$', '\$')}".format(row=row))
            with date_column:
                st.write(row['date'].strftime('%d %b %Y'))
            if row['type'] == 'news':
                with button_column:
                    st.link_button("Read more", row['url'])
        pass


def show_team(company: Company):
    with st.spinner("Loading..."):
        people = get_people()
    filtered_index = people['Founder of Company'].apply(lambda x: company.airtableId in x if isinstance(x, list) else False)
    founders = people[filtered_index]
    if len(founders) == 0:
        st.info("No founders for this company.")

    for founder in founders.itertuples():
        image_column, col1, col2, col3 = st.columns([1, 2, 3, 1], gap='small', vertical_alignment='center')
        photo_url = get_preview(founder.Photo)
        if photo_url:
            image_column.image(photo_url)

        col1.subheader(founder.Name)
        col1.write(founder.Email)
        col2.write(founder.Bio)
        col3.link_button("Contact", founder.LinkedIn)


def show_signals(company: Company):
    c1, c2, c3 = st.columns(3)
    financial_data = get_company_financial_data(company)
    traction_metrics = get_company_traction_metrics(company)
    highlights = get_company_highlights(company)
    
    with c1:
        st.metric("Runway", financial_data['runway'])
        st.metric("Revenue", format_as_dollars(financial_data['revenue']))
    with c2:
        st.metric("Burnrate", financial_data['burnrate'])
        st.metric("Customers Cnt", financial_data['customers_cnt'])
    with c3:
        # Create a mock object with required attributes for show_highlights
        mock_summary = type('MockSummary', (), {
            'new_highlights': highlights,
            'traction_metrics': traction_metrics
        })()
        highlights_cnt = show_highlights(mock_summary)
        if not highlights_cnt:
            st.info("No signals for this company.")


def show_traction_graph(traction_metric: TractionMetric, label=None):
    now = datetime.now()
    thirty_days = datetime.timedelta(days=30)
    first_day = datetime.as_local(datetime.datetime(now.year, now.month, 1))
    points = [
        ('latest', first_day),
        ('1mo', first_day - thirty_days),
        ('2mo', first_day - 2 * thirty_days),
        ('3mo', first_day - 3 * thirty_days),
        ('4mo', first_day - 4 * thirty_days),
        ('5mo', first_day - 5 * thirty_days),
        ('6mo', first_day - 6 * thirty_days),
    ]
    values = []
    for key, date in points:
        if key == 'latest':
            if isinstance(traction_metric.latest, (float, int)):
                values.append((date, traction_metric.latest))
        else:
            traction_value = traction_metric.previous.get(key)
            value = traction_value.value
            if isinstance(value, (float, int)):
                values.append((date, value))
    
    if not values:
        st.info("No data available for this metric.")
        return

    values.sort(key=lambda x: x[0])
    df = pd.DataFrame(values, columns=['date', 'value'])

    st.line_chart(
        df.set_index('date')['value'],
        use_container_width=True,
        y_label = label,
        x_label = "Date",
    )


def show_traction_graph_with_combo(company: Company, selected=None):
    traction_metrics = get_company_traction_metrics(company)
    traction_metrics_fields = fields(traction_metrics)
    # Dictionary mapping internal field names to human-readable display names
    metric_display_names = {
        "popularity_rank": "Popularity Ranking",
        "web_visits": "Website Traffic",
        "employee_count": "Employee Count",
        "linkedin_followers": "LinkedIn Followers",
        "twitter_followers": "Twitter Followers",
        "instagram_followers": "Instagram Followers",
        "itunes_reviews": "App Store Reviews",
        "googleplay_reviews": "Google Play Reviews",
        "app_downloads": "App Downloads",
        "g2_reviews": "G2 Reviews",
        "trustpilot_reviews": "Trustpilot Reviews",
        "chrome_extensions_reviews": "Chrome Extension Reviews",
        "chrome_extensions_users": "Chrome Extension Users"
    }
    
    # Get available metrics that have data
    available_metrics = list(sorted([f.name for f in traction_metrics_fields if getattr(traction_metrics, f.name)]))
    
    if not available_metrics:
        st.info("No traction metrics available for this company.")
        return

    # Create options for dropdown with human-readable names
    options = {
        name: metric_display_names.get(name, name.replace('_', ' ').title())
        for name in available_metrics
    }
    with st.container(border=True):
        index = 0
        if selected and selected in available_metrics:
            index = available_metrics.index(selected)
        metric_display = st.selectbox(
            label="Select Metric",
            options=list(options.keys()),
            format_func=lambda x: options[x],
            label_visibility='hidden',
            index=index,
            key=f"company_combo_{selected}"
        )

        if metric_display:
            traction_metric = getattr(traction_metrics, metric_display)
            show_traction_graph(traction_metric, label=options[metric_display])
        else:
            st.warning("Please select a metric.")


def get_selected_company():
    active_companies_query = {
        'status': {'$in': [s for s in CompanyStatus if s not in {CompanyStatus.PASSED}]}
    }
    companies = {
        c.airtableId: c.name for c in
        get_companies_v2(query=active_companies_query, projection=['name', 'airtableId'])
    }
    ids = sorted(companies.keys(), key=lambda x: companies[x])
    company_id = st.query_params.get('company_id', None)
    selected_company_id = st.selectbox(
        "Pick the company",
        options=ids,
        index=ids.index(company_id) if company_id and company_id in ids else None,
        placeholder="Select company...",
        format_func=lambda x: companies.get(x),
        label_visibility='hidden'
    )
    return selected_company_id


def company_page():
    selected_company_id = get_selected_company()
    if not selected_company_id:
        st.info("Please select a company.")
        return

    st.query_params.update({'company_id': selected_company_id})
    companies = get_companies_v2(query={'airtableId': selected_company_id})
    if len(companies) != 1:
        st.warning("Company not found.")
        return

    company = companies[0]
    show_company_basic_details(company)
    st.divider()

    names = ["Overview", "Team", "Financial", "Traction", "Signals", "investments", "Asks", "Updates"]
    tabs = st.tabs(names)

    with tabs[0]:
        show_overview(company)

    with tabs[1]:
        show_team(company)

    with tabs[2]:
        st.text("TBD")

    with tabs[3]:
        show_traction_content(company)


    with tabs[4]:
        show_signals(company)

        c1, c2 = st.columns(2)
        with c1:
            show_traction_graph_with_combo(company, 'web_visits')
        with c2:
            show_traction_graph_with_combo(company, 'employee_count')

    with tabs[5]:
        with st.spinner("Loading ..."):
            investments = get_investments()

        with st.spinner("Loading ..."):
            portfolio = get_portfolio()
        show_company_investment_details(company, investments, portfolio)

    with tabs[6]:
        show_asks(company)

    with tabs[7]:
        with st.spinner("Loading ..."):
            updates = get_updates()
        show_last_updates_and_news(company, updates)
