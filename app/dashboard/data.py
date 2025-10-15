import typing
import requests
import streamlit as st
import os
import pandas as pd
from datetime import date
from bson import ObjectId
from pyairtable import Api
from pymongo import MongoClient
from app.shared.company import Company
from app.shared.task import Task
from app.foundation.primitives import datetime
from app.foundation.server import AppConfig
try:
    from google.cloud import firestore
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    firestore = None
from .data_mock import get_mock_companies, get_mock_investments, get_mock_jobs, get_mock_company_by_id, get_mock_companies_by_status, get_mock_tasks_for_company

# Set local development mode for mock data (override any existing value)
os.environ['LOCAL_DEV'] = 'True'

# Check if we're in local development mode
LOCAL_DEV = os.getenv('LOCAL_DEV', 'False').lower() == 'true'


AIRTABLE_BASE_ID = 'appRfyOgGDu7UKmeD'


@st.cache_resource
def app_config() -> AppConfig:
    config = AppConfig()
    if not config.db_loaded:
        config.load_db(firestore.Client())
    return config

@st.cache_resource
def airtable_api_client() -> Api:
    if LOCAL_DEV:
        return None  # Mock API client for local development
    return Api(os.environ['AIRTABLE_API_KEY'])

@st.cache_resource
def mongodb_client():
    if LOCAL_DEV:
        return None  # Mock client for local development
    return MongoClient(os.environ['MONGODB_URI'], tz_aware=True)

@st.cache_resource()
def mongo_database():
    if LOCAL_DEV:
        return None  # Mock database for local development
    return mongodb_client().get_default_database('fund')

@st.cache_resource()
def mongo_collection(collection_name):
    if LOCAL_DEV:
        return None  # Mock collection for local development
    return mongo_database().get_collection(collection_name)

@st.cache_data(show_spinner=False, ttl=datetime.timedelta(minutes=5))
def fetch_airtable_as_rows(table_name: str, **options) -> typing.List[dict]:
    if LOCAL_DEV:
        return []  # Mock empty rows for local development
    api = airtable_api_client()
    return api.table( AIRTABLE_BASE_ID, table_name).all(**options)


def fetch_airtable_as_df(table_name: str, **options) -> pd.DataFrame:
    rows = fetch_airtable_as_rows(table_name, **options)
    return pd.DataFrame([r['fields'] | {'id': r.get('id')} for r in rows]).set_index('id')


def get_investments(**options):
    if LOCAL_DEV:
        return get_mock_investments(**options)
    return fetch_airtable_as_df('tblrsrZTHW8famwpw', **options)


def get_companies_v2(query: dict = None, sort: typing.List[typing.Tuple[str, int]] = None, projection=None) -> typing.List[Company]:
    if LOCAL_DEV:
        mock_companies = get_mock_companies(query, sort)
        return [
            Company(
                id=str(company['_id']),
                name=company.get('name', ''),
                status=company.get('status', ''),
                website=company.get('website', ''),
                blurb=company.get('blurb', ''),
                createdAt=company.get('createdAt'),
                ourData={
                    'mainIndustry': company.get('mainIndustry', ''),
                    'summary': company.get('summary', ''),
                    'problem': company.get('problem', ''),
                    'marketSize': company.get('marketOpportunity', ''),
                    'targetMarket': company.get('mainIndustry', ''),
                    'bulletPoints': company.get('bulletPoints', []),
                    'signals': company.get('signals', ''),
                    'fundingStage': company.get('fundingStage', ''),
                    'team': company.get('team', []),
                    'partnerships': company.get('partnerships', []),
                    'metrics': company.get('metrics', {})
                },
                spectrData={
                    'description': company.get('solution', '')
                }
            ) for company in mock_companies
        ]
    
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
    if LOCAL_DEV:
        return pd.DataFrame(columns=['id'])
    return fetch_airtable_as_df('tblos3pGBciCaxXp0', **options)


def get_people(**options):
    if LOCAL_DEV:
        # Return mock DataFrame with expected structure for local development
        mock_people = [
            {
                'id': 'person_001',
                'Founder of Company': ['68e69a2dc32b590896149739'],  # Generous company ID
                'Name': 'Kyle Montgomery',
                'Role': 'Co-founder & CEO'
            },
            {
                'id': 'person_002', 
                'Founder of Company': ['68e69a2dc32b590896149739'],  # Generous company ID
                'Name': 'Vlad Turcu',
                'Role': 'Co-founder & CTO'
            }
        ]
        return pd.DataFrame(mock_people).set_index('id')
    return fetch_airtable_as_df('tbl5cyHdQ9ijkbz7K', **options)


def get_updates(**options):
    if LOCAL_DEV:
        return pd.DataFrame(columns=['id'])
    return fetch_airtable_as_df('tblBA51bFtn6dZmRX', **options)


def get_portfolio(**options):
    if LOCAL_DEV:
        return pd.DataFrame(columns=['id'])
    return fetch_airtable_as_df('tblxeUBhlLFnoG6QC', **options)


@st.cache_data(show_spinner=False, ttl=datetime.timedelta(minutes=5))
def get_jobs(**options):
    """Fetch jobs from MongoDB jobs collection"""
    if LOCAL_DEV:
        return get_mock_jobs(**options)
    
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


# ============================================================================
# TASK MANAGEMENT FUNCTIONS
# ============================================================================

def get_tasks(company_id: str) -> typing.List[Task]:
    """Get all tasks for a company"""
    if LOCAL_DEV:
        # For local development, use session state with mock data fallback
        if "tasks" not in st.session_state:
            st.session_state.tasks = {}
        
        # Get tasks from session state (user-created) or mock data (initial)
        session_tasks = st.session_state.tasks.get(company_id, [])
        if not session_tasks:
            # Initialize with mock data if no tasks exist
            mock_tasks = get_mock_tasks_for_company(company_id)
            st.session_state.tasks[company_id] = mock_tasks
            session_tasks = mock_tasks
        
        return [Task(**task) if isinstance(task, dict) else task for task in session_tasks]
    
    # Production: Query MongoDB
    db = mongo_database()
    tasks_collection = db.get_collection('tasks')
    tasks_data = tasks_collection.find({'companyId': ObjectId(company_id)}).to_list()
    return [Task(**task) for task in tasks_data]


def add_task(company_id: str, text: str, due_date: date, assignee: str, created_by: str = "Unknown") -> Task:
    """Add a new task to a company"""
    # Validate that due_date is not in the past
    if due_date < date.today():
        raise ValueError(f"Cannot create task with past due date: {due_date.strftime('%m/%d/%Y')}. Please use today or a future date.")
    
    task = Task(
        company_id=company_id,
        text=text,
        due_date=due_date,
        assignee=assignee,
        created_by=created_by
    )
    
    if LOCAL_DEV:
        # Store in session state for local development
        if "tasks" not in st.session_state:
            st.session_state.tasks = {}
        
        if company_id not in st.session_state.tasks:
            st.session_state.tasks[company_id] = []
        
        st.session_state.tasks[company_id].append(task.model_dump())
        return task
    
    # Production: Save to MongoDB
    db = mongo_database()
    tasks_collection = db.get_collection('tasks')
    task_data = task.model_dump()
    task_data['companyId'] = ObjectId(company_id)
    result = tasks_collection.insert_one(task_data)
    task.id = str(result.inserted_id)
    return task


def update_task(task_id: str, **updates) -> typing.Optional[Task]:
    """Update a task by ID"""
    # Validate that due_date is not in the past if it's being updated
    if 'due_date' in updates and updates['due_date'] is not None:
        if isinstance(updates['due_date'], date) and updates['due_date'] < date.today():
            raise ValueError(f"Cannot update task with past due date: {updates['due_date'].strftime('%m/%d/%Y')}. Please use today or a future date.")
    
    if LOCAL_DEV:
        # Update in session state for local development
        if "tasks" not in st.session_state:
            return None
        
        for company_id, tasks in st.session_state.tasks.items():
            for i, task_data in enumerate(tasks):
                if isinstance(task_data, dict) and task_data.get('id') == task_id:
                    task_data.update(updates)
                    return Task(**task_data)
                elif hasattr(task_data, 'id') and task_data.id == task_id:
                    # Update the task object
                    for key, value in updates.items():
                        setattr(task_data, key, value)
                    return task_data
        return None
    
    # Production: Update in MongoDB
    db = mongo_database()
    tasks_collection = db.get_collection('tasks')
    result = tasks_collection.update_one({'_id': ObjectId(task_id)}, {'$set': updates})
    
    if result.modified_count > 0:
        updated_task = tasks_collection.find_one({'_id': ObjectId(task_id)})
        return Task(**updated_task) if updated_task else None
    
    return None


def delete_task(task_id: str) -> bool:
    """Delete a task by ID"""
    if LOCAL_DEV:
        # Delete from session state for local development
        if "tasks" not in st.session_state:
            return False
        
        for company_id, tasks in st.session_state.tasks.items():
            for i, task_data in enumerate(tasks):
                if isinstance(task_data, dict) and task_data.get('id') == task_id:
                    del st.session_state.tasks[company_id][i]
                    return True
                elif hasattr(task_data, 'id') and task_data.id == task_id:
                    del st.session_state.tasks[company_id][i]
                    return True
        return False
    
    # Production: Delete from MongoDB
    db = mongo_database()
    tasks_collection = db.get_collection('tasks')
    result = tasks_collection.delete_one({'_id': ObjectId(task_id)})
    return result.deleted_count > 0


def get_active_tasks_count(company_id: str) -> int:
    """Get count of active tasks for a company"""
    tasks = get_tasks(company_id)
    return len([task for task in tasks if task.status == "active"])
