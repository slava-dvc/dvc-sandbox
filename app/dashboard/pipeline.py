from bson import ObjectId
import streamlit as st
import itertools
from app.shared import Company, CompanyStatus
from app.dashboard.data import get_companies_v2
from app.dashboard.formatting import format_relative_time, safe_markdown
from app.dashboard.company import get_company_traction_metrics, get_company_highlights
from app.dashboard.highlights import show_highlights_for_company
from .data import mongo_database, airtable_api_client, AIRTABLE_BASE_ID


_PIPELINE_STATUES = {
    "New Company": [
        CompanyStatus.NEW_COMPANY,
        CompanyStatus.PROCESSING
    ],
    "In Progress": [
        CompanyStatus.CONTACTED,
        CompanyStatus.MEETING,
        CompanyStatus.CHECKIN,
    ],
    "Diligence": [
        CompanyStatus.DILIGENCE,
    ],
    "Offered to Invest": [
        CompanyStatus.OFFERED_TO_INVEST,
        CompanyStatus.SUBMITTED_AL
    ],
    "Going to Pass": [
        CompanyStatus.GOING_TO_PASS,
    ]
}

_AVAILABLE_STATUES = list(itertools.chain.from_iterable(_PIPELINE_STATUES.values())) + [
    CompanyStatus.INVESTED,
    CompanyStatus.RADAR,
    CompanyStatus.PASSED
]

# Status values for dropdown display
_AVAILABLE_STATUS_VALUES = [status.value for status in _AVAILABLE_STATUES]


@st.dialog("Company details", width="large")
def company_details(company):
    st.header(company.name)
    st.write(
        "This is a placeholder for the company details"
    )


def _update_company_status(company: Company, status_value):
    # In local development mode, we don't have MongoDB/Airtable
    # For now, just update the company object in memory
    # Convert status value back to CompanyStatus enum
    company.status = CompanyStatus(status_value)
    
    # Store the updated company in session state for persistence
    if 'updated_companies' not in st.session_state:
        st.session_state.updated_companies = {}
    st.session_state.updated_companies[company.id] = company
    
    st.success(f"Updated {company.name} status to {status_value}")
    
    # TODO: In production, update MongoDB and Airtable
    # mongo_database().companies.update_one(
    #     {'_id': ObjectId(company.id)},
    #     {'$set': {'status': str(status)}}
    # )
    # if company.airtableId:
    #     # Update Airtable
    #     api = airtable_api_client()
    #     table = api.table(AIRTABLE_BASE_ID, 'tblJL5aEsZFa0x6zY')  # Companies table
    #     table.update(company.airtableId, {'Status': str(status)})


def _render_company_card(company: Company):
    company_id = company.id
    company_name = company.name
    company_website = company.website
    company_stage = company.ourData.get('currentStage')
    source = company.ourData.get('source')
    introduced_by = company.ourData.get('introducedBy')
    if introduced_by:
        if isinstance(introduced_by, list):
            introduced_by = ' and '.join([str(person) for person in introduced_by])
        else:
            introduced_by = str(introduced_by)
        source = ' by '.join([source, introduced_by])

    logo_column, info_column, signals_column, button_column = st.columns([1, 7, 4, 1], gap='small', vertical_alignment='center')

    with logo_column:
        linedIn_url = company.linkedInData.get('logo') if isinstance(company.linkedInData, dict) else None
        fallback_url = f'https://placehold.co/128x128?text={company.name}'
        st.image(linedIn_url if linedIn_url else fallback_url, width=128)

    with info_column:
        header = []
        if company_website and isinstance(company_website, str):
            header.append(f"**[{company_name}]({company_website})**")
        else:
            header.append(f"**{company_name}**")
        header.append(company_stage or "Unknown")
        header.append(f"🕐 {format_relative_time(company.createdAt)}")

        st.markdown("&nbsp; | &nbsp;".join(header))
        st.text(source if source else "No source provided")
    # Find the index of the current status in the available statuses
    current_status_index = 0
    if company.status:
        try:
            current_status_index = _AVAILABLE_STATUS_VALUES.index(company.status.value)
        except ValueError:
            current_status_index = 0
    
    new_status = st.selectbox(
        label="Status",
        options=_AVAILABLE_STATUS_VALUES,
        key=f"status_{company.id}",
        index=current_status_index,
        label_visibility="collapsed",
        width=256
    )
    with signals_column:
        highlights_cnt = show_highlights_for_company(company)
        if not highlights_cnt:
            st.info("No signals for this company.")

    with button_column:
        def update_company_id(company_id):
            st.query_params.update({'company_id': company.id})

        st.link_button("View", url=f'/company_page?company_id={company.id}', width=192)

    if isinstance(company.blurb, str) and company.blurb:
        blurb = safe_markdown(company.blurb)
        if len(blurb) > 1024:
            blurb = blurb[:1024] + "..."
        st.markdown(blurb)
    else:
        st.caption("No blurb provided.")

    if new_status != company.status.value:
        with st.spinner("Updating..."):
            _update_company_status(company, new_status)

        st.rerun()


def show_pipeline_tab(statuses):
    query = {
        'status': {
            '$in': [s.value for s in statuses]
        }
    }
    companies = get_companies_v2(query, [('createdAt', -1)])

    # Apply any status updates from session state
    if 'updated_companies' in st.session_state:
        updated_companies = st.session_state.updated_companies
        for i, company in enumerate(companies):
            if company.id in updated_companies:
                companies[i] = updated_companies[company.id]

    if not companies:
        st.info("No companies found for this stage yet.")
        return

    # Render a compact card for each company
    for company in companies:
        with st.container(border=True):
            _render_company_card(company)

@st.fragment()
def pipeline_page():
    tabs = st.tabs(_PIPELINE_STATUES)
    for tab, (tab_name, statuses) in zip(tabs, _PIPELINE_STATUES.items()):
        with tab:
            show_pipeline_tab(statuses)
