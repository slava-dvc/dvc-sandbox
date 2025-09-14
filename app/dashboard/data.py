import typing
import requests
import streamlit as st
import os
import pandas as pd
from bson import ObjectId
from pyairtable import Api
from pymongo import MongoClient
from app.shared.company import Company
from app.foundation.primitives import datetime
from app.foundation.server import AppConfig
from google.cloud import firestore


AIRTABLE_BASE_ID = 'appRfyOgGDu7UKmeD'


@st.cache_resource
def app_config() -> AppConfig:
    config = AppConfig()
    if not config.db_loaded:
        config.load_db(firestore.Client())
    return config

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
def get_companies_v2(query: dict = None, sort: typing.List[typing.Tuple[str, int]] = None, projection=None) -> typing.List[Company]:
    db = mongo_database()
    companies_collection = db.get_collection('companies')
    companies = companies_collection.find(query or {}, sort=sort, projection=projection).to_list()
    return [
        Company.model_validate(company) for company in companies
    ]


def update_company(company_id: str, fields: dict):
    db = mongo_database()
    companies_collection = db.get_collection('companies')
    companies_collection.update_one(
        {'_id': ObjectId(company_id)},
        {'$set': fields}
    )


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


### This peace of junk is may be required to get Notable Co-Investors in Position

def get_investments_config():
    return get_table_config('tblrsrZTHW8famwpw')


def get_table_config(table_id: str) -> dict:
    tables_config = fetch_tables_config()
    return tables_config.get(table_id, {})


def fetch_linked_table_names(linked_table_id):
    table_config = get_table_config(linked_table_id)
    primaryFieldId = table_config.get('primaryFieldId')
    field = None
    for f in table_config.get('fields', []):
        if f.get('id') == primaryFieldId:
            field = f
            break
    primary_field_name = field.get('name')
    linked_table = {
        row['id']:row['fields'].get(primary_field_name)
        for row in fetch_airtable_as_rows(linked_table_id, fields=[primary_field_name])
    }
    return linked_table

def convert_filed(field_definition: dict, column: pd.Series, linked_table: dict) -> pd.Series:
    options = {opt['id']: opt['name'] for opt in field_definition.get('options', {}).get('choices', [])}
    filed_type = field_definition.get('type')

    def _text(value):
        if isinstance(value, (list, tuple)):
            value = ", ".join([str(v) for v in value])
        if not value:
            return None
        return str(value)

    def _multiple_record_links(value):
        return [linked_table.get(i, None) for i in value] if isinstance(value, list) else []

    def _multiple_selects(value):
        return [options.get(i, None) for i in value] if isinstance(value, list) else []

    def _single_select(value):
        if not value:
            return value
        if isinstance(value, list) and len(value) == 1:
            value = value[0]
        return options.get(value, value)

    field_serializers = {
        # 'checkbox': _boolean_serializer,
        # 'currency': _number_serializer,
        'date': _text,
        'email': _text,
        'multilineText': _text,
        # 'multipleLookupValues': _multiple_selects_serializer,
        'multipleRecordLinks': _multiple_record_links,
        'multipleSelects': _multiple_selects,
        # 'number': _number_serializer,
        'richText': _text,
        'singleLineText': _text,
        'singleSelect': _single_select,
        # 'url': _url_serializer,
    }
    if filed_type in field_serializers:
        return column.apply(field_serializers[filed_type])
    return column


def replace_ids_with_values(table_config: dict, df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace IDs with corresponding values for fields in a given dataframe.

    Args:
        table_id (str): The ID of the Airtable to fetch field configuration from.
        df (pd.DataFrame): The dataframe containing rows with IDs to be replaced.

    Returns:
        pd.DataFrame: The updated dataframe with IDs replaced by their respective values.

    Example:
        df = replace_ids_with_values('tblJL5aEsZFa0x6zY', companies)
    """
    # Fetch table configuration and field definitions

    field_definitions = table_config.get('fields', [])
    linked_tables = {}
    result = df.copy()
    for field in field_definitions:
        field_name = field['name']
        # Skip fields not present in the dataframe
        if field_name not in df.columns:
            continue

        linked_table = {}
        if field.get('type') == 'multipleRecordLinks':
            linked_table_id = field.get('options', {}).get('linkedTableId')
            if linked_table_id in linked_tables:
                linked_table = linked_tables[linked_table_id]
            else:
                linked_table = fetch_linked_table_names(linked_table_id)
                linked_tables[linked_table_id] = linked_table
        result[field_name] = convert_filed(field, result[field_name], linked_table)
    return result


@st.cache_data(show_spinner=False)
def fetch_tables_config() -> dict:
    url = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables"
    headers = {
        'Authorization': f"Bearer {os.environ['AIRTABLE_API_KEY']}"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return {table['id']: table for table in response.json()['tables']}
