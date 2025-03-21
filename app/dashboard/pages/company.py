import pandas as pd
import requests
import streamlit as st
from app.dashboard.data import get_companies, get_ask_to_task, get_updates, get_people

st.set_page_config(
    page_title="Portfolio company",
    layout="wide"
)

company_id = st.query_params.get('id')
companies = get_companies()
companies_in_portfolio = companies[~companies['Initial Fund Invested From'].isna()].sort_values(by='Company')

selected_company_id = st.selectbox(
    "Pick the company",
    options=companies_in_portfolio.index,
    index=companies_in_portfolio.index.get_loc(company_id) if company_id in companies_in_portfolio.index else None,
    placeholder="Select...",
    format_func=lambda x: companies_in_portfolio.loc[x]['Company']
)


def show_company_basic_details(company: pd.Series):
    st.header(company['Company'])
    if company['URL'] and isinstance(company['URL'], str):
        st.write(company['URL'])
    else:
        st.caption("No URL provided.")
    st.write(company['Blurb'])


def show_company_investment_details(company: pd.Series):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Invested", "TBD")
        st.metric("Last Valuation", "TBD")

    with col2:
        st.metric("InitialStake", "TBD")
        st.metric("Total Inv", "TBD")

    with col3:
        st.metric("Current Stake", "TBD")
        st.metric("Total NAV", "TBD")

    with col4:
        st.metric("Initial Reval", "TBD")
        st.metric("MOIC", "TBD")


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


def show_last_updates_and_news(company: pd.Series):
    company_id = company.name
    updates = get_updates()
    filtered_index = updates['Company Name'].apply(lambda x: company_id in x if isinstance(x, list) else False)
    filtered_updates = updates[filtered_index]
    if len(filtered_updates) == 0:
        st.info("No updates for this company.")
    else:
        columns = ['Please provide any comments/questions', 'Created']
        filtered_updates['Created'] = pd.to_datetime(filtered_updates['Created']).dt.strftime('%d %b %Y')
        st.dataframe(filtered_updates[columns], hide_index=True, use_container_width=True)


def show_team(company: pd.Series):
    company_id = company.name
    people = get_people()
    filtered_index = people['Founder of Company'].apply(lambda x: company_id in x if isinstance(x, list) else False)
    founders = people[filtered_index]
    if len(founders) == 0:
        st.info("No founders for this company.")

    for founder in founders.itertuples():
        photo_url = founder.Photo[0]['url'] if isinstance(founder.Photo, list) and len(founder.Photo) > 0 else None
        image_column, col1, col2, col3 = st.columns([2, 2, 5, 1], gap='medium', vertical_alignment='center')
        if photo_url:
            requests.get(photo_url)
            image_column.image(photo_url)

        col1.subheader(founder.Name)
        col1.write(founder.Email)
        col2.write(founder.Bio)
        col3.link_button("Contact", founder.LinkedIn)


if selected_company_id:
    selected_company = companies_in_portfolio.loc[selected_company_id]
    show_company_basic_details(selected_company)
    st.markdown("---")
    show_company_investment_details(selected_company)
    st.markdown("---")
    st.subheader("Asks")
    show_asks(selected_company)
    st.markdown("---")
    st.subheader("Last Updates and News")
    show_last_updates_and_news(selected_company)
    st.markdown("---")
    st.subheader("Team")
    show_team(selected_company)
else:
    st.warning("Please select a company.")
