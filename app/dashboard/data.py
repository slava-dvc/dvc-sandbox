import streamlit as st
import os
import pandas as pd
from pyairtable import Api


AIRTABLE_BASE_ID = 'appRfyOgGDu7UKmeD'


@st.cache_resource
def api_client() -> Api:
    return Api(os.environ['AIRTABLE_API_KEY'])


def fetch_table_as_df(table_name: str) -> pd.DataFrame:
    api = api_client()
    table = api.table( AIRTABLE_BASE_ID, table_name)
    return pd.DataFrame([r['fields'] for r in table.all()])


@st.cache_data
def get_investments():
    return fetch_table_as_df('tblrsrZTHW8famwpw')

@st.cache_data
def get_companies():
    return fetch_table_as_df('tblJL5aEsZFa0x6zY')