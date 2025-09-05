from dataclasses import fields

import pandas as pd
import requests
import streamlit as st
from bson import ObjectId
from fastapi.encoders import jsonable_encoder

from app.dashboard.company_summary import show_highlights, TractionMetric, TractionMetrics, NewsItem
from app.dashboard.data import (
    get_investments, get_portfolio, get_updates, get_ask_to_task, get_people,
    get_companies_v2, app_config, update_company, mongo_database,
)
from app.dashboard.formatting import (
    format_as_dollars, format_as_percent, is_valid_number, get_preview,
    safe_markdown, format_relative_time
)
from app.foundation.primitives import datetime
from app.shared.company import Comment, Company, CompanyStatus
from app.shared.user import User

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


def show_key_value_row(key: str, value: str | None):
    """Helper function to display a key-value pair in two columns with proper formatting."""
    col1, col2 = st.columns([1, 7], vertical_alignment="center")
    with col1:
        st.markdown(f"**{key}**")
    with col2:
        if value and isinstance(value, str) and value.strip():
            st.markdown(safe_markdown(value))
        else:
            st.markdown("—")


def show_financial(company: Company):
    """Display financial information in a structured format."""

    # Revenue Model Type
    revenue_model = company.ourData.get('revenueModelType') if company.ourData else None
    revenue_model_value = ', '.join(revenue_model) if revenue_model and isinstance(revenue_model, list) else None
    show_key_value_row("Revenue Model Type", revenue_model_value)

    # Revenue
    revenue = company.ourData.get('revenue') if company.ourData else None
    show_key_value_row("Revenue", format_as_dollars(revenue) if revenue else None)

    # Total Funding
    total_funding = company.spectrData.get('funding', {}).get('total_funding_usd') if company.spectrData else None
    show_key_value_row("Total Funding", format_as_dollars(total_funding) if total_funding else None)

    # Round Size - Not clear from data structure
    show_key_value_row("Round Size", "Not implemented yet.")

    # Valuation - use latest valuation
    valuation = company.ourData.get('latestValuation') if company.ourData else None
    if valuation and isinstance(valuation, list) and valuation:
        valuation_value = format_as_dollars(valuation[0])
    else:
        valuation_value = None
    show_key_value_row("Valuation", valuation_value)

    # Burnrate
    burnrate = company.ourData.get('burnRate') if company.ourData else None
    show_key_value_row("Burnrate", format_as_dollars(burnrate) if burnrate else None)

    # Last Financing Date
    last_funding_date = company.spectrData.get('funding', {}).get('last_funding_date') if company.spectrData else None
    show_key_value_row("Last Financing Date", last_funding_date)

    # Instrument - Not clear from data structure
    show_key_value_row("Instrument", "Not implemented yet.")

    # Business Model
    business_model = company.ourData.get('businessModelType') if company.ourData else None
    if business_model and isinstance(business_model, list) and business_model:
        business_model_value = business_model[0]  # Take first item as it's long text
    else:
        business_model_value = None
    show_key_value_row("Business Model", business_model_value)

    # Co-Investors - Not clear from data structure
    show_key_value_row("Co-Investors", "Not implemented yet.")


def show_traction_content(company: Company):
    """Display detailed traction information from ourData.traction."""
    traction = company.ourData.get('traction') if company.ourData else None

    if traction and isinstance(traction, str) and traction.strip():
        st.markdown(safe_markdown(traction))
    else:
        st.info("No traction information available for this company.")


def show_overview(company: Company):
    """Display company overview information in a structured format."""
    # show_key_value_row("Concerns", "Not implemented yet.")
    valid_concerns = [
        "Non repeat founder(s)",
        "The market is too small",
        "The market is too red",
        "Weird Captable",
        "Valuation is too high",
        "Strong Competitors",
        "Not a VC Story",
        "Conflict of interest",
        "Hardware",
        "Tokenomics",
        "No Unique Value",
        "No Contact",
        "Too early for us",
        "Not in our focus",
        "No moat/unique value",
        "Round is too slow, ability to raise",
        "Not the US based",
        "Focusing on EU market"
    ]
    concerns = st.multiselect(
        label="Concerns",
        options=valid_concerns,
        default=company.concerns,
        placeholder="Add concerns...",
        label_visibility='collapsed',
        width=512
    )
    if set(concerns) != set(company.concerns):
        update_company(company.id, {'concerns': list(concerns)})

    # Main Industry
    main_industry = company.ourData.get('mainIndustry') if company.ourData else None
    industry_value = ', '.join(main_industry) if main_industry and isinstance(main_industry, list) else None
    show_key_value_row("Main Industry", industry_value)

    # Summary - prefer ourData.summary over blurb
    summary = company.ourData.get('summary') if company.ourData else None
    if not summary:
        summary = company.blurb
    show_key_value_row("Summary", summary)

    # Problem
    problem = company.ourData.get('problem') if company.ourData else None
    show_key_value_row("Problem", problem)

    # Solution
    solution = company.spectrData.get('description') if company.spectrData else None
    show_key_value_row("Solution", solution)

    # Market Size
    market_size = company.ourData.get('marketSize') if company.ourData else None
    show_key_value_row("Market Size", market_size)

    # Target Market
    target_market = company.ourData.get('targetMarket') if company.ourData else None
    show_key_value_row("Target Market", target_market)


def show_company_basic_details(company: Company):
    logo_column, name_column, buttons_column = st.columns([1, 5, 1], vertical_alignment="center")

    with logo_column:
        linedIn_url = company.linkedInData.get('logo') if isinstance(company.linkedInData, dict) else None
        fallback_url = f'https://placehold.co/128x128?text={company.name}'
        st.image(linedIn_url if linedIn_url else fallback_url, width=128)

    with name_column:
        st.header(company.name)
        st.write(company.status.value if company.status else "Unknown")
        if company.website and isinstance(company.website, str):
            st.write(company.website)
        else:
            st.caption("No URL provided.")
        if company.blurb and isinstance(company.blurb, str):
            st.markdown(safe_markdown(company.blurb))
        else:
            st.caption("No blurb provided.")

    with buttons_column:
        lindy_data = {
            'callbackURL': f'https://api.dvcagent.com/api/companies/{company.id}/memorandum',
            'companyName': company.name,
            'airtableId': company.airtableId,
            'companyWebsite': company.website,
            'companyBlurb': company.blurb,
            'concerns': company.concerns,
            'comments': company.comments,
        }
        pitch_deck_url = company.ourData.get('linkToDeck') if company.ourData else None
        if pitch_deck_url and isinstance(pitch_deck_url, str):
            st.link_button("Pitchdeck", pitch_deck_url, width=192)

        memorandum_is_creating = False
        company_passed = False
        if st.button("Generate memo" if not company.memorandum else "(Re)generate memo", width=192):
            config = app_config()
            lindy_data |= {'linkedin': company.linkedInData, 'data': company.ourData, 'spectr': company.spectrData}
            response = requests.post(
                url=config.lindy.memorandum.url,
                headers={
                    'Authorization': f'Bearer {config.lindy.memorandum.api_key}',
                },
                json=jsonable_encoder(lindy_data)
            )
            response.raise_for_status()
            memorandum_is_creating = True

        if company.status == CompanyStatus.GOING_TO_PASS and st.button("Pass and archive", width=192):
            config = app_config()
            lindy_data |= {'email': company.ourData.get('email')}
            response = requests.post(
                url=config.lindy.pass_company.url,
                headers={
                    'Authorization': f'Bearer {config.lindy.pass_company.api_key}',
                },
                json=jsonable_encoder(lindy_data)
            )
            response.raise_for_status()
            mongo_database().companies.update_one(
                {'_id': ObjectId(company.id)},
                {'$set': {'status': str(CompanyStatus.PASSED)}}
            )
            company_passed=True

    if company_passed:
        st.info('Company status changed to Pass. Soon Founder(s) get email about our decision. You may close the window')

    if memorandum_is_creating:
        st.info("Memorandum creation is triggered.", icon="️⏲️")


def show_company_investment_details(company: Company):
    with st.spinner("Loading ..."):
        investments = get_investments()

    with st.spinner("Loading ..."):
        portfolio = get_portfolio()

    col1, col2, col3, col4 = st.columns(4)
    company_id = company.airtableId
    company_investments = investments[
        investments['Company'].apply(lambda x: company_id in x if isinstance(x, list) else False)]
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
    total_investment = company_investments['Amount Invested'].sum()
    if company_in_portfolio is not None:
        last_valuation = company_in_portfolio['Last Valuation/cap']
        initial_investment = company_in_portfolio['Initial Investment']
        entry_valuation = company_in_portfolio['Entry Valuation /cap']
        initial_ownership = initial_investment / entry_valuation
        next_round_size = company_in_portfolio['Next round size?']
        dilution_estimate = 1 - (0 if next_round_size is None else next_round_size) / last_valuation
        follow_on_investment = company_in_portfolio['Follow on size'] or 0
        current_ownership = initial_ownership * dilution_estimate + follow_on_investment / last_valuation
        if current_ownership is None:
            current_ownership = initial_ownership
        total_nav = current_ownership * last_valuation
        moic = float(total_nav) / float(total_investment) if is_valid_number(
            total_investment) and total_investment > 0 else None

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


def show_last_updates_and_news(company: Company):
    with st.spinner("Loading ..."):
        updates = get_updates()
    rows = []
    relevant_updates = updates['Company Name'].apply(
        lambda x: company.airtableId in x if isinstance(x, list) else False)
    company_updates = updates[relevant_updates].copy()
    company_updates.rename(columns={'Please provide any comments/questions': "Comment"}, inplace=True)
    for company_update in company_updates.itertuples():
        rows.append({
            'type': 'update',
            'publisher': 'Team update:',
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
                    title = "No text available."
                st.markdown(f"**{row['publisher']}**: {safe_markdown(title)}".format(row=row))
            with date_column:
                st.write(row['date'].strftime('%d %b %Y'))
            if row['type'] == 'news':
                with button_column:
                    st.link_button("Read more", row['url'], width=192)


def show_team(company: Company):
    with st.spinner("Loading..."):
        people = get_people()
    filtered_index = people['Founder of Company'].apply(
        lambda x: company.airtableId in x if isinstance(x, list) else False)
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
        if founder.LinkedIn and isinstance(founder.LinkedIn, str):
            col3.link_button("Contact", founder.LinkedIn)
        else:
            col3.write("No LinkedIn")


def show_signals(company: Company):
    highlights = get_company_highlights(company)
    traction_metrics = get_company_traction_metrics(company)

    if company.status == CompanyStatus.INVESTED:
        c1, c2, c3 = st.columns(3)
        financial_data = get_company_financial_data(company)

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
    else:
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
        y_label=label,
        x_label="Date",
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


def show_signlas_and_traction(company: Company):
    show_signals(company)

    c1, c2 = st.columns(2)
    with c1:
        show_traction_graph_with_combo(company, 'web_visits')
    with c2:
        show_traction_graph_with_combo(company, 'employee_count')


@st.fragment
def show_comments(company: Company):
    company = get_companies_v2({'_id': ObjectId(company.id)}, projection=['comments', 'airtableId', 'name'])[0]
    comments = company.comments or []
    comments.sort(key=lambda x: x.createdAt, reverse=True)
    if not comments:
        st.info("No comments for this company.")

    for comment in comments:
        with st.container(border=True):
            photo_column, text_column = st.columns([1, 12], vertical_alignment='center', width=512)
            if comment.user.picture:
                with photo_column:
                    st.image(comment.user.picture, width=32)

            with text_column:
                st.markdown(f"**{comment.user.name}** • {format_relative_time(comment.createdAt)} ")

            st.write(safe_markdown(comment.text))
    if not comments:
        text = st.chat_input("Add a first comment")
    else:
        text = st.chat_input("Add a new comment")
    if text:
        user = User.model_validate(dict(st.user))
        comments.append(Comment(text=text, user=user))
        update_company(
            company_id=company.id,
            fields={'comments': [c.model_dump() for c in comments]}
        )
        st.rerun(scope='fragment')


def show_memorandum(company: Company):
    st.markdown(safe_markdown(company.memorandum))


def get_company_meetings(company: Company):
    """Get meetings for a specific company from the database."""
    meetings_collection = mongo_database().meetings
    meetings = list(meetings_collection.find({"companyId": company.id}).sort("createdAt", -1))
    return meetings


def show_meetings(company: Company):
    """Display meetings for the company as a list of cards."""
    with st.spinner("Loading meetings..."):
        meetings = get_company_meetings(company)
    
    if not meetings:
        st.info("No meetings recorded for this company.")
        return
    
    for meeting in meetings:
        with st.container(border=True):
            # Header row with meeting title and date
            header_col, date_col = st.columns([3, 1], vertical_alignment="center")
            
            calendar_event = meeting.get('calendarEvent', {})
            meeting_name = calendar_event.get('name', 'Untitled Meeting')
            created_at = meeting.get('createdAt')
            
            with header_col:
                st.subheader(meeting_name)
            
            with date_col:
                if created_at:
                    st.write(format_relative_time(created_at))
            
            # Meeting details
            if calendar_event.get('start'):
                st.write(f"**Start:** {calendar_event['start']}")
            
            if calendar_event.get('attendees'):
                attendees = [attendee.get('email', 'Unknown') for attendee in calendar_event['attendees']]
                st.write(f"**Attendees:** {', '.join(attendees)}")
            
            # Recording URL
            recording_url = meeting.get('recordingUrl')
            if recording_url:
                st.link_button("Watch Recording", recording_url, use_container_width=False)
            
            # Recap as markdown
            recap = meeting.get('recap', '')
            if recap and isinstance(recap, str) and recap.strip():
                with st.expander("Meeting Recap", expanded=False):
                    st.markdown(safe_markdown(recap))
            else:
                st.info("No recap available for this meeting.")


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

    tabs_config: dict = {
        "Overview": show_overview,
        "Team": show_team,
        "Financial": show_financial,
        "Traction": show_traction_content,
        "Signals": show_signlas_and_traction,
        "Investments": show_company_investment_details,
        "Asks": show_asks,
        "Updates": show_last_updates_and_news,
        "Memorandum": show_memorandum,
        "Comments": show_comments,
        "Meetings": show_meetings,
    }

    names = ["Overview", "Team", "Financial"]
    if company.memorandum:
        names.append("Memorandum")
    if company.ourData.get('traction'):
        names.append("Traction")
    if company.spectrData:
        names.append("Signals")
    if company.status == CompanyStatus.INVESTED:
        names.extend(["Investments", "Asks", "Updates"])
    names.extend(['Comments', 'Meetings'])
    for t, n in zip(st.tabs(names), names):
        with t:
            tabs_config[n](company)

    # Show last update timestamps
    update_parts = []

    timestamps = [
        ("Created", company.createdAt),
        ("Updated", company.updatedAt),
        ("LinkedIn", company.linkedInUpdatedAt),
        ("Signals", company.spectrUpdatedAt),
        ("Google Play", company.googlePlayUpdatedAt),
        ("App Store", company.appStoreUpdatedAt),
        ("Google Jobs", company.googleJobsUpdatedAt)
    ]

    for label, timestamp in timestamps:
        if timestamp:
            formatted_time = format_relative_time(timestamp)
            if formatted_time:
                update_parts.append(f"{label} {formatted_time}")

    if update_parts:
        st.caption(" • ".join(update_parts))
