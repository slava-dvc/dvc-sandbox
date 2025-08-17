import os
import streamlit as st
from app.dashboard.data import get_companies_v2
from app.shared import Company, CompanyStatus
from app.dashboard.formatting import format_relative_time


_PIPELINE_STATUES = [
    CompanyStatus.NEW_COMPANY,
    CompanyStatus.IN_PROGRESS,
    CompanyStatus.DILIGENCE,
    CompanyStatus.OFFERED_TO_INVEST,
    CompanyStatus.GOING_TO_PASS
]


@st.dialog("Company details", width="large")
def company_details(company):
    st.header(company.name)
    st.write(
        "This is a placeholder for the company details"
    )


def _extract_logo_url(logo_field):
    """Return a best-effort logo URL from the provided field.
    Supports:
    - Airtable attachment arrays (with thumbnails)
    - Direct string URLs
    - Single attachment dict
    """
    if not logo_field:
        return None

    # If it's a list/tuple of attachments or URLs
    if isinstance(logo_field, (list, tuple)):
        if not logo_field:
            return None
        first = logo_field[0]
        logo_field = first

    # If it is a dict (Airtable attachment)
    if isinstance(logo_field, dict):
        thumbs = logo_field.get("thumbnails") or {}
        # Prefer large then full then small (favor larger images)
        for size in ("large", "full", "small"):
            url = (thumbs.get(size) or {}).get("url")
            if url:
                return url
        return logo_field.get("url")

    # If it's a direct URL string
    if isinstance(logo_field, str):
        return logo_field

    return None


def _render_company_card(company: Company):
    """Render a compact company card with logo, name, website, blurb."""
    st.caption(f"Company ID: {company.airtableId}")

    # logo may come from ourData.logo merged as top-level 'logo'
    logo_url = _extract_logo_url(company.ourData.get('logo'))
    fallback_url = f'https://placehold.co/128x128?text={company.name}'
    logo_column, company_fields_column = st.columns([2, 5], vertical_alignment="center", width=512 )
    statuses = [str(s) for s in  CompanyStatus]

    with logo_column:
        try:
            st.image(logo_url, width=128)
        except Exception:
            st.image(fallback_url, width=128)

    with company_fields_column:
        source = company.ourData.get('source') or "No source provided"
        st.markdown(f"### {company.name}")
        st.text(f"{source}")
        st.markdown(f"[{company.website}]({company.website})")
        new_status = st.selectbox(
            label="Company status",
            options=statuses,
            key=f"company_status_{company.airtableId}",
            label_visibility='hidden',
            index=statuses.index(str(company.status))
        )

    if isinstance(company.blurb,str):
        blurb = company.blurb.replace('$', '\$')
        if len(blurb) > 1024:
            blurb = blurb[:1024] + " ..."
        st.markdown(blurb)
    columns = st.columns([0.3, 0.4, 0.3], vertical_alignment="center")
    # with columns[0]:

    with columns[1]:
        if st.button('Details', key=f"company_details_{company.airtableId}"):
            company_details(company)
    with columns[2]:
        st.text(f"Added: {format_relative_time(company.createdAt)}")


    if new_status != str(company.status):
        st.warning('Status update is not yet supported.')

@st.fragment()
def show_pipeline_tab(status):
    companies = get_companies_v2({'status': str(status)}, [('createdAt', -1)])
    # if st.button("Show company details", key=f"show_company_details_{status}"):
    #     company_dialog(1)

    if not companies:
        st.info("No companies found for this stage yet.")
        return

    # Render a compact card for each company
    for company in companies:
        with st.container(border=True):
            _render_company_card(company)


def pipeline_page():

    tabs = st.tabs(_PIPELINE_STATUES)
    for tab, status in zip(tabs, _PIPELINE_STATUES):
        with tab:
            show_pipeline_tab(status)
