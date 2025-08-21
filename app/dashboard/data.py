import typing
import requests
import streamlit as st
import os
import pandas as pd
from pyairtable import Api
from pymongo import MongoClient
from app.shared.company import Company
from app.foundation.primitives import datetime

AIRTABLE_BASE_ID = 'appRfyOgGDu7UKmeD'


@st.cache_resource
def airtable_api_client() -> Api:
    return Api(os.environ['AIRTABLE_API_KEY'])

@st.cache_resource
def mongodb_client():
    return MongoClient(os.environ['MONGODB_URI'], tz_aware=True)

@st.cache_resource()
def mongo_database():
    return mongodb_client().get_default_database('fund')

@st.cache_data(show_spinner=False, ttl=datetime.timedelta(minutes=5))
def fetch_airtable_as_rows(table_name: str, **options) -> typing.List[dict]:
    api = airtable_api_client()
    return api.table( AIRTABLE_BASE_ID, table_name).all(**options)


def fetch_airtable_as_df(table_name: str, **options) -> pd.DataFrame:
    rows = fetch_airtable_as_rows(table_name, **options)
    return pd.DataFrame([r['fields'] | {'id': r.get('id')} for r in rows]).set_index('id')


def get_investments(**options):
    return fetch_airtable_as_df('tblrsrZTHW8famwpw', **options)

@st.cache_resource(show_spinner=False)
def get_companies(query: dict = None):
    def transform_company(company):
        data = {'id': company['airtableId']}
        data |= {
            k: v for k, v in company.items()
            if k in {'spectrId', 'spectrUpdatedAt', 'name', 'website', 'blurb', 'status'}
        }
        data |= company.get('ourData')
        spectrData = company.get('spectrData')
        if spectrData:
            data = data | {
                k: v for k, v in spectrData.items()
                if k in {'new_highlights', 'highlights', 'traction_metrics', 'news'}
            }
        return data

    db = mongo_database()
    companies_collection = db.get_collection('companies')
    rows = [
        transform_company(company)
        for company in companies_collection.find(query or {})
    ]
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).set_index('id')


def get_companies_v2(query: dict = None, sort: typing.List[typing.Tuple[str, int]] = None, projection=None) -> typing.List[Company]:
    db = mongo_database()
    companies_collection = db.get_collection('companies')
    companies = companies_collection.find(query or {}, sort=sort, projection=projection).to_list()
    return [
        Company.model_validate(company) for company in companies
    ]


def get_ask_to_task(**options):
    return fetch_airtable_as_df('tblos3pGBciCaxXp0', **options)


def get_people(**options):
    return fetch_airtable_as_df('tbl5cyHdQ9ijkbz7K', **options)


def get_updates(**options):
    return fetch_airtable_as_df('tblBA51bFtn6dZmRX', **options)


def get_portfolio(**options):
    return fetch_airtable_as_df('tblxeUBhlLFnoG6QC', **options)


@st.cache_data(show_spinner=False, ttl=datetime.timedelta(minutes=5))
def get_jobs(**options):
    """Fetch jobs from MongoDB jobs collection"""
    from app.foundation.primitives import datetime
    
    client = mongodb_client()
    db = client.get_default_database('fund')
    jobs_collection = db.get_collection('jobs')
    
    # Filter jobs updated in the last 2 weeks
    two_weeks_ago = datetime.now() - datetime.timedelta(weeks=2)
    query = {
        'updatedAt': {'$gte': two_weeks_ago}
    }
    
    jobs = list(jobs_collection.find(query).sort('updatedAt', -1))
    return jobs
