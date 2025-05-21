import pandas as pd
import requests
import streamlit as st
import numpy as np
from app.foundation.primitives import datetime
from app.dashboard.data import get_companies, get_ask_to_task, get_updates, get_people, get_investments, get_portfolio
from app.dashboard.formatting import format_as_dollars, format_as_percent, is_valid_number, get_preview
from app.dashboard.company_summary import CompanySummary, show_highlights

__all__ = ['show_company_page']


def show_company_basic_details(company: pd.Series, company_summary: CompanySummary):
    logo_column, name_column = st.columns([1, 8])
    with logo_column:
        if company_summary.logo_url:
            try:
                st.image(company_summary.logo_url, width=64)
            except Exception:
                st.write("📊")
        else:
            st.write("📊")
    with name_column:
        st.header( f"{company_summary.name} ({company_summary.status})")
    if company_summary.website and isinstance(company_summary.website, str):
        st.write(company_summary.website)
    else:
        st.caption("No URL provided.")
    if isinstance(company_summary.blurb, str):
        st.write(company_summary.blurb)
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
    last_valuation = np.nan
    initial_ownership = np.nan
    current_ownership = np.nan
    total_nav = np.nan
    moic = np.nan
    initial_investment = np.nan
    total_investment=company_investments['Amount Invested'].sum()
    if company_in_portfolio is not None:
        last_valuation = company_in_portfolio['Last Valuation/cap']
        initial_investment = company_in_portfolio['Initial Investment']
        entry_valuation = company_in_portfolio['Entry Valuation /cap']
        initial_ownership = initial_investment / entry_valuation
        next_round_size = company_in_portfolio['Next round size?']
        dilution_estimate = 1 - (0 if np.isnan(next_round_size) else next_round_size) / last_valuation
        follow_on_investment = company_in_portfolio['Follow on size'] or 0
        current_ownership = initial_ownership*dilution_estimate + follow_on_investment / last_valuation
        if np.isnan(current_ownership):
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
        st.metric("MOIC", f"{moic:0.2f}" if is_valid_number(moic) else "N/A")


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
                    title = "N/A"
                st.markdown(f"**{row['publisher']}**: {title}".format(row=row))
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
    highlights_cnt = show_highlights(company_summary)
    if not highlights_cnt:
        st.info("No signals for this company.")

def show_company_page(investments, companies, updates, company_id):
    with st.spinner("Loading portfolio..."):
        portfolio = get_portfolio()

    def reset_company_id():
        st.query_params.pop('company_id', None)

    col1, col2 = st.columns([1, 8], vertical_alignment='bottom')
    with col1:
        st.button("← To Main ", on_click=reset_company_id)

    companies_in_portfolio = companies.sort_values(by='Company')
    with col2:
        selected_company_id = st.selectbox(
            "Pick the company",
            options=companies_in_portfolio.index,
            index=companies_in_portfolio.index.get_loc(company_id) if company_id in companies_in_portfolio.index else None,
            placeholder="Select company...",
            format_func=lambda x: companies_in_portfolio.loc[x]['Company'],
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
