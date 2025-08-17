import pandas as pd

import streamlit as st
from dataclasses import fields
from app.foundation.primitives import datetime
from app.dashboard.formatting import format_as_dollars, format_as_percent, is_valid_number, get_preview
from app.dashboard.company_summary import CompanySummary, show_highlights, TractionMetric
from app.dashboard.data import get_investments, get_companies, get_portfolio, get_updates, get_ask_to_task, get_people

__all__ = ['company_page']


def show_company_basic_details(company: pd.Series, company_summary: CompanySummary):
    logo_column, name_column = st.columns([1, 5], vertical_alignment="center", width=512 )
    with logo_column:
        fallback_url = f'https://placehold.co/128x128?text={company_summary.name}'
        st.image(fallback_url)
        #
        # if company_summary.logo_url:
        #     try:
        #         st.image(company_summary.logo_url, width=64)
        #     except Exception:
        #         st.write("📊")
        # else:
        #     st.write("📊")
    with name_column:
        st.header(company_summary.name)
        st.write(company_summary.status)
    if company_summary.website and isinstance(company_summary.website, str):
        st.write(company_summary.website)
    else:
        st.caption("No URL provided.")
    if isinstance(company_summary.blurb, str):
        st.markdown(company_summary.blurb.replace('$', '\$'))
    else:
        st.caption("No blurb provided.")


def show_company_investment_details(company: pd.Series, investments: pd.DataFrame, portfolio: pd.DataFrame):
    col1, col2, col3, col4 = st.columns(4)
    company_id = company.name
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


def show_asks(company: pd.Series):
    company_id = company.name
    asks = get_ask_to_task()
    filtered_index = asks['Companies'].apply(lambda x: company_id in x if isinstance(x, list) else False)
    filtered_asks = asks[filtered_index & (asks['Status'] != 'Done')]
    if len(filtered_asks) == 0:
        st.info("No active asks for this company.")
    else:
        columns = ['ASK', 'Status', 'Type', 'Days Ago']
        st.dataframe(filtered_asks[columns], hide_index=True, use_container_width=True)


def show_last_updates_and_news(company_summary: CompanySummary, updates):
    rows = []
    relevant_updates = updates['Company Name'].apply(lambda x: company_summary.company_id in x if isinstance(x, list) else False)
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
    for company_news_item in company_summary.news:
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


def show_team(company: pd.Series):
    company_id = company.name
    people = get_people()
    filtered_index = people['Founder of Company'].apply(lambda x: company_id in x if isinstance(x, list) else False)
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


def show_signals(company_summary: CompanySummary):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Runway", company_summary.runway)
        st.metric("Revenue", format_as_dollars(company_summary.revenue))
    with c2:
        st.metric("Burnrate", company_summary.burnrate)
        st.metric("Customers Cnt", company_summary.customers_cnt)
    with c3:
        highlights_cnt = show_highlights(company_summary)
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


def show_traction_graph_with_combo(company_summary: CompanySummary, selected=None):
    traction_metrics = company_summary.traction_metrics
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


def company_page():
    with st.spinner("Loading investments..."):
        investments = get_investments()

    with st.spinner("Loading companies..."):
        companies = get_companies()
        companies = companies[companies['investingFund'].notna()]

    with st.spinner("Loading updates..."):
        updates = get_updates()

    with st.spinner("Loading portfolio..."):
        portfolio = get_portfolio()

    def reset_company_id():
        st.query_params.pop('company_id', None)

    company_id =st.query_params.get('company_id', None)
    companies_in_portfolio = companies.sort_values(by='name')
    selected_company_id = st.selectbox(
        "Pick the company",
        options=companies_in_portfolio.index,
        index=companies_in_portfolio.index.get_loc(company_id) if company_id in companies_in_portfolio.index else None,
        placeholder="Select company...",
        format_func=lambda x: companies_in_portfolio.loc[x]['name'],
        label_visibility='hidden'
    )

    if selected_company_id:
        st.query_params.update({'company_id': selected_company_id})
        selected_company = companies_in_portfolio.loc[selected_company_id]
        company_summary = CompanySummary.from_dict(selected_company, selected_company_id)
        show_company_basic_details(selected_company, company_summary)
        st.divider()
        show_company_investment_details(selected_company, investments, portfolio)
        st.divider()
        st.subheader("Asks")
        show_asks(selected_company)
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            show_traction_graph_with_combo(company_summary, 'web_visits')
        with c2:
            show_traction_graph_with_combo(company_summary, 'employee_count')
        st.divider()
        st.subheader("Signals")
        show_signals(company_summary)
        st.divider()
        st.subheader("Last Updates and News")
        show_last_updates_and_news(company_summary, updates)
        st.divider()
        st.subheader("Team")
        show_team(selected_company)
    else:
        st.warning("Please select a company.")
