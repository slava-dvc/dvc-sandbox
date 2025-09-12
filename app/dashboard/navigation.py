import streamlit as st
import json
from uuid import uuid4
from google.cloud import storage, pubsub
from google.auth import default
from infrastructure.queues.company_creation import company_create_from_docs_topic_name
from app.shared.company import CompanyStatus
from app.foundation.primitives import datetime
from .data import mongo_database
from .fund import fund_page
from .company import company_page
from .jobs import jobs_page
from .pipeline import pipeline_page

__all__ = ['show_navigation']


@st.cache_resource()
def get_storage_client():
    return storage.Client()


@st.cache_resource()
def get_bucket(name):
    return get_storage_client().get_bucket(name)


@st.cache_resource()
def get_publisher_client():
    return pubsub.PublisherClient()


def validate_company_form(name, email, pitch_deck_url, pitch_deck_file):
    """Validate company form inputs"""
    if not name.strip():
        return "Company Name is required"
    if not email.strip():
        return "Company Email is required"
    if not pitch_deck_url and not pitch_deck_file:
        return "Pitch Deck is required"
    if pitch_deck_url and pitch_deck_file:
        return "Please upload either a PDF file or a link to a PDF file"
    return None


def upload_pdf_to_gcs(file, bucket_name="dvc-pdfs"):
    """Upload PDF file to GCS bucket and return the path"""
    bucket = get_bucket(bucket_name)
    path = f'inbound/{str(uuid4())}.pdf'
    bucket.blob(path).upload_from_file(file)
    return path


def build_company_sources(pitch_deck_file, pitch_deck_url):
    """Build sources array for company creation"""
    sources = []
    if pitch_deck_file:
        path = upload_pdf_to_gcs(pitch_deck_file)
        sources.append({
            'type': 'pdf',
            'bucket': 'dvc-pdfs',
            'key': path
        })
    if pitch_deck_url:
        sources.append({
            'type': 'url',
            'url': pitch_deck_url.strip()
        })
    return sources


def create_company_in_db(name, email, website, sources):
    """Create company in MongoDB with PROCESSING status"""
    db = mongo_database()
    companies_collection = db.get_collection('companies')
    
    company_doc = {
        "name": name.strip(),
        "website": website.strip() if website else None,
        "status": CompanyStatus.PROCESSING,
        "ourData": {
            "email": email.strip()
        },
        "createdAt": datetime.now(),
        "sources": sources  # Store sources for processing
    }
    
    result = companies_collection.insert_one(company_doc)
    return str(result.inserted_id)


def publish_company_to_queue(company_data):
    """Publish full company data to Pub/Sub queue"""
    publisher = get_publisher_client()
    _, project_id = default()
    topic_path = publisher.topic_path(project_id, company_create_from_docs_topic_name)
    
    message_data = json.dumps(company_data).encode('utf-8')
    
    future = publisher.publish(topic_path, message_data)
    return future.result()


@st.dialog("New company")
def add_new_company():
    with st.form("new_company_form", clear_on_submit=True, border=False):
        company_name = st.text_input("Company Name", placeholder="Enter company name...")
        company_email = st.text_input("Company Email", placeholder="contact@company.com")
        website = st.text_input("Website", placeholder="https://company.com")

        st.subheader("Pitch Deck")
        pitch_deck_file = st.file_uploader(
            "Upload PDF",
            type=['pdf'],
            help="Upload a PDF file containing the company's pitch deck"
        )
        pitch_deck_url = st.text_input(
            "From URL",
            placeholder="https://docsend.com/... or https://drive.google.com/... or direct PDF URL",
            help="Link to PDF file, DocSend presentation, or Google Drive document"
        )

        submitted = st.form_submit_button("Submit", type="primary")

        if submitted:
            # Validate form
            error = validate_company_form(company_name, company_email, pitch_deck_url, pitch_deck_file)
            if error:
                st.error(error)
                return

            # Build sources
            sources = build_company_sources(pitch_deck_file, pitch_deck_url)
            
            # Create company in database first
            company_id = create_company_in_db(company_name, company_email, website, sources)
            
            # Build full company data for Pub/Sub
            company_data = {
                "id": company_id,
                "name": company_name.strip(),
                "email": company_email.strip(),
                "website": website.strip() if website else None,
                "sources": sources
            }
            
            # Publish to queue for processing
            message_id = publish_company_to_queue(company_data)
            st.success("Company submitted successfully! It will appear in pipeline shortly.")



def show_navigation():
    """
    Display common navigation for the dashboard

    Args:
        current_page: Current page identifier ('fund', 'jobs', etc.)
    """
    # User info section at top of sidebar
    if st.user.is_logged_in:
        # st.sidebar.markdown("---")
        st.sidebar.markdown("**👤 Logged in as:**")
        st.sidebar.markdown(f"{st.user.email}")
        if st.sidebar.button("🚪 Logout", key="logout_btn", width=192):
            st.logout()
        # st.sidebar.markdown("---")

    pages = [
        st.Page(fund_page, title="Funds"),
        st.Page(company_page, title="Companies"),
        st.Page(pipeline_page, title="Pipeline"),
        st.Page(jobs_page, title="Jobs"),
    ]
    pg = st.navigation(pages, )

    st.sidebar.markdown("**Actions:**")
    st.sidebar.button('➕ Add Company', on_click=add_new_company, width=192)
    pg.run()
