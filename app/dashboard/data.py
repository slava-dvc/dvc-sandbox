import typing
import requests
import streamlit as st
import os
import pandas as pd
from pyairtable import Api


AIRTABLE_BASE_ID = 'appRfyOgGDu7UKmeD'


@st.cache_resource
def api_client() -> Api:
    return Api(os.environ['AIRTABLE_API_KEY'])


@st.cache_data
def fetch_table_as_rows(table_name: str, **options) -> typing.List[dict]:
    api = api_client()
    return api.table( AIRTABLE_BASE_ID, table_name).all(**options)


def fetch_table_as_df(table_name: str, **options) -> pd.DataFrame:
    rows = fetch_table_as_rows(table_name)
    return pd.DataFrame([r['fields'] for r in rows])


def get_investments():
    return fetch_table_as_df('tblrsrZTHW8famwpw')


def get_companies():
    return fetch_table_as_df('tblJL5aEsZFa0x6zY')


def get_companies_config():
    return get_table_config('tblJL5aEsZFa0x6zY')


def get_investments_config():
    return get_table_config('tblrsrZTHW8famwpw')


@st.cache_data
def fetch_tables_config() -> dict:
    url = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables"
    headers = {
        'Authorization': f"Bearer {os.environ['AIRTABLE_API_KEY']}"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return {table['id']: table for table in response.json()['tables']}


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
        for row in fetch_table_as_rows(linked_table_id, fields=[primary_field_name])
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
