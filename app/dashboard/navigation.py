import streamlit as st
from uuid import uuid4
from google.cloud import storage
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
            if not company_name.strip():
                st.error("Company Name is required")
                return
            if not company_email.strip():
                st.error("Company Email is required")
                return
            if not pitch_deck_url and not pitch_deck_file:
                st.error("Pitch Deck is required")
                return
            if pitch_deck_url and pitch_deck_file:
                st.error("Please upload either a PDF file or a link to a PDF file")
                return

            sources = []
            if pitch_deck_file:
                bucket = get_bucket("dvc-pdfs")
                path = f'inbound/{str(uuid4())}.pdf'
                bucket.blob(path).upload_from_file(pitch_deck_file)

                sources.append(
                    {
                        'type': 'pdf',
                        'bucket': 'dvc-pdfs',
                        'key': path
                    }
                )
            if pitch_deck_url:
                sources.append(
                    {
                        'type': 'url',
                        'url': pitch_deck_url.strip()
                    }
                )

            data = {
                "companyName": company_name.strip(),
                "companyEmail": company_email.strip(),
                "website": website.strip(),
                "sources": sources
            }


            st.info("Company is submitted. It will appear in pipeline shortly")

            #
            # st.session_state.add_new_company = {
            #     "companyName": company_name.strip(),
            #     "companyEmail": company_email.strip(),
            #     "website": website.strip(),
            #     "pitchDeckFile": pitch_deck_file,
            #     "pitchDeckUrl": pitch_deck_url.strip() if pitch_deck_url else None
            # }
        # st.rerun()


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
