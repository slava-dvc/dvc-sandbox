import typing
import requests
import streamlit as st
import os
import pandas as pd
from pyairtable import Api
from pymongo import MongoClient

AIRTABLE_BASE_ID = 'appRfyOgGDu7UKmeD'


@st.cache_resource
def airtable_api_client() -> Api:
    return Api(os.environ['AIRTABLE_API_KEY'])

@st.cache_resource
def mongodb_client():
    return MongoClient(os.environ['MONGODB_URI'])

@st.cache_resource()
def mongo_database():
    return mongodb_client().get_default_database('fund')

@st.cache_data(show_spinner=False)
def fetch_airtable_as_rows(table_name: str, **options) -> typing.List[dict]:
    api = airtable_api_client()
    return api.table( AIRTABLE_BASE_ID, table_name).all(**options)


def fetch_airtable_as_df(table_name: str, **options) -> pd.DataFrame:
    rows = fetch_airtable_as_rows(table_name, **options)
    return pd.DataFrame([r['fields'] | {'id': r.get('id')} for r in rows]).set_index('id')


def get_investments(**options):
    return fetch_airtable_as_df('tblrsrZTHW8famwpw', **options)


def get_companies(**options):
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
        for company in companies_collection.find()
    ]
    return pd.DataFrame(rows).set_index('id')

    for air_row in air_table_rows:
        airtable_id = air_row['id']
        airfields = air_row['fields']
        if not airfields.get('Initial Fund Invested From'):
            continue
        row = {
            k:v for k, v in air_row['fields'].items()
            if k in all_fields
        } | {'id': airtable_id}
        mongo_row = mongo_index.get(airtable_id)
        if mongo_row:
            row = row | {
                'spectrId': mongo_row.get('spectrId'),
                'spectrUpdatedAt': mongo_row.get('spectrUpdatedAt'),
            }
            spectrData = mongo_row.get('spectrData')
            if spectrData:
                row = row | {
                    k: v for k, v in spectrData.items()
                    if k in all_fields
                }

        rows.append(row)
    return pd.DataFrame(rows).set_index('id')


def get_ask_to_task(**options):
    return fetch_airtable_as_df('tblos3pGBciCaxXp0', **options)


def get_people(**options):
    return fetch_airtable_as_df('tbl5cyHdQ9ijkbz7K', **options)


def get_updates(**options):
    return fetch_airtable_as_df('tblBA51bFtn6dZmRX', **options)


def get_portfolio(**options):
    return fetch_airtable_as_df('tblxeUBhlLFnoG6QC', **options)


@st.cache_data(show_spinner=False)
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


@st.cache_data(show_spinner=False)
def fetch_tables_config() -> dict:
    url = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables"
    headers = {
        'Authorization': f"Bearer {os.environ['AIRTABLE_API_KEY']}"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return {table['id']: table for table in response.json()['tables']}
