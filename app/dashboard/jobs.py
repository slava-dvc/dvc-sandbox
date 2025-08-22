import streamlit as st
from app.dashboard.data import get_jobs
from app.dashboard.formatting import format_relative_time, safe_markdown

__all__ = ['jobs_page']



def show_job_card(job):
    """Display a single job card with collapsible details"""
    
    # Get first apply option for the apply button
    apply_options = job.get('applyOptions', [])
    first_apply_option = apply_options[0] if apply_options else None
    
    # Job card container
    with st.container(border=True):
        # Header row with company name, title, and apply button
        col1, col2 = st.columns([7, 1], vertical_alignment='center')

        company_name = job.get('companyName', 'Unknown Company')
        title = job.get('title', 'Unknown Position')
        location = job.get('location', 'Remote/Unknown')
        created_at = job.get('createdAt')
        updated_at = job.get('updatedAt')

        with col1:
            st.markdown(f"**{company_name}** - {title}")
            st.caption(
                f"{location}, Found: {format_relative_time(created_at)}, Updated: {format_relative_time(updated_at)}")
        with col2:
            if first_apply_option:
                apply_link = first_apply_option.get('link', '#')
                st.link_button("Apply", apply_link, width=192)
            else:
                st.button("Apply", disabled=True, width=192)

        # Collapsible details
        with st.expander("View Details"):
            # Description
            description = job.get('description', 'No description available')
            st.markdown("**Description:**")
            st.markdown(safe_markdown(description))
            
            # Job highlights
            job_highlights = job.get('jobHighlights', [])
            if job_highlights:
                st.markdown("**Highlights:**")
                for highlight in job_highlights:
                    title = highlight.get('title', '')
                    items = highlight.get('items', [])
                    if title and items:
                        st.markdown(f"*{title}:*")
                        for item in items:
                            st.markdown(f" {item}")
            
            # Extensions (job type, etc.)
            extensions = job.get('extensions', [])
            if extensions:
                st.markdown("**Job Type:**")
                st.markdown(", ".join(extensions))
            
            # All apply options
            if len(apply_options) > 1:
                st.markdown("**All Apply Options:**")
                for option in apply_options:
                    title = option.get('title', 'Apply')
                    link = option.get('link', '#')
                    st.markdown(f" [{title}]({link})")


def jobs_page():
    st.title("🔍 Job Opportunities")

    with st.spinner("Loading jobs..."):
        jobs = get_jobs()
    
    if not jobs:
        st.info("No recent job opportunities found.")
        st.markdown("Jobs are updated automatically when our portfolio companies post new positions.")
        return

    st.markdown(f"{len(jobs)} Open roles across our portfolio — from early hires to exec searches. Share, apply, or refer someone great.")

    st.divider()

    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:
        # Company filter
        companies = sorted(set(job.get('companyName') or 'Unknown' for job in jobs))
        selected_companies = st.multiselect(
            "Filter by Company",
            options=companies,
            default=[]
        )

    with filter_col2:
        # Location filter
        locations = sorted(set(job.get('location') or 'Unknown' for job in jobs))
        selected_locations = st.multiselect(
            "Filter by Location",
            options=locations,
            default=[]
        )
    
    # Apply filters
    filtered_jobs = jobs
    if selected_companies:
        filtered_jobs = [job for job in filtered_jobs if (job.get('companyName') or 'Unknown') in selected_companies]
    if selected_locations:
        filtered_jobs = [job for job in filtered_jobs if (job.get('location') or 'Unknown') in selected_locations]

    
    # Display jobs
    if not filtered_jobs:
        st.warning("No jobs match the selected filters.")
    else:
        for job in filtered_jobs:
            show_job_card(job)