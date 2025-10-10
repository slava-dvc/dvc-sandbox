"""
🎨 SYNAPSE SANDBOX - Exact Original UI Match
============================================

A prototype that EXACTLY matches the original Synapse dashboard UI
based on the screenshots provided.

Features:
- Exact same navigation structure (Funds, Companies, Pipeline, Jobs)
- Same tabbed interface (New Company, In Progress, Diligence, etc.)
- Same company card layout with logos, descriptions, status dropdowns
- Same visual design and components
- Task management integrated seamlessly
"""

import streamlit as st
import pandas as pd
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

# =============================================================================
# MOCK DATA MODELS
# =============================================================================

class CompanyStatus(str, Enum):
    NEW_COMPANY = "New Company"
    IN_PROGRESS = "In Progress"
    DILIGENCE = "Diligence"
    OFFERED_TO_INVEST = "Offered to Invest"
    GOING_TO_PASS = "Going to Pass"
    INVESTED = "Invested"

class TaskStatus(str, Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    BLOCKED = "Blocked"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

class TaskCategory(str, Enum):
    FOLLOW_UP = "Follow-up"
    DUE_DILIGENCE = "Due Diligence"
    DOCUMENT_REVIEW = "Document Review"
    MEETING = "Meeting"
    FINANCIAL_REVIEW = "Financial Review"
    LEGAL = "Legal"
    TECHNICAL_REVIEW = "Technical Review"
    OTHER = "Other"

@dataclass
class Task:
    id: str
    title: str
    description: str
    company_id: str
    assignee: str
    deadline: datetime
    status: TaskStatus
    priority: TaskPriority
    category: TaskCategory
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

@dataclass
class Company:
    id: str
    name: str
    description: str
    status: CompanyStatus
    stage: str
    introduction_by: str
    signals: List[str]
    bullet_points: List[str]
    created_at: datetime
    updated_at: datetime

# =============================================================================
# MOCK DATA GENERATORS
# =============================================================================

def generate_mock_companies() -> List[Company]:
    """Generate companies that match the original data structure."""
    companies = [
        Company(
            id="company_1",
            name="Generous",
            description="An AI-powered gifting platform that offers personalized gift recommendations and transaction handling to reduce consumer anxiety and financial losses for retailers.",
            status=CompanyStatus.NEW_COMPANY,
            stage="Pre-seed/seed (Early)",
            introduction_by="Alice Yagolnitser",
            signals=["No signals for this company."],
            bullet_points=[
                "Page #2: 71% of consumers say gifting causes anxiety",
                "Page #3: AI-powered gifting, connected"
            ],
            created_at=datetime.now() - timedelta(days=1),
            updated_at=datetime.now() - timedelta(days=1)
        ),
        Company(
            id="company_2",
            name="Generous",
            description="An AI-powered platform that connects gifters, merchants, and recipients to provide personalized gift suggestions and streamline the gifting process.",
            status=CompanyStatus.NEW_COMPANY,
            stage="Unknown",
            introduction_by="Alice Yagolnitser",
            signals=["No signals for this company."],
            bullet_points=[],
            created_at=datetime.now() - timedelta(days=1),
            updated_at=datetime.now() - timedelta(days=1)
        ),
        Company(
            id="company_3",
            name="Slava's Company1",
            description="Immersive phygital playgrounds integrate learning with play to attract visitors, and innovation consulting services help companies develop effective strategies and products.",
            status=CompanyStatus.NEW_COMPANY,
            stage="Unknown",
            introduction_by="Slava Rudenko",
            signals=["No signals for this company."],
            bullet_points=[],
            created_at=datetime.now() - timedelta(days=2),
            updated_at=datetime.now() - timedelta(days=2)
        ),
        Company(
            id="company_4",
            name="TechFlow Solutions",
            description="Blockchain-based supply chain transparency platform enabling enterprise clients to track products from source to consumer with immutable records.",
            status=CompanyStatus.DILIGENCE,
            stage="Series A",
            introduction_by="Sarah Johnson",
            signals=["Strong technical team", "Partnership with Walmart"],
            bullet_points=[
                "Page #1: $1.2M ARR with 23 enterprise customers",
                "Page #2: 85% year-over-year growth"
            ],
            created_at=datetime.now() - timedelta(days=5),
            updated_at=datetime.now() - timedelta(days=1)
        ),
        Company(
            id="company_5",
            name="DataViz Pro",
            description="Advanced data visualization and analytics platform for business intelligence, helping enterprises make data-driven decisions with interactive dashboards.",
            status=CompanyStatus.INVESTED,
            stage="Series B",
            introduction_by="Michael Brown",
            signals=["Market leader", "95% customer retention"],
            bullet_points=[
                "Page #1: $8.5M ARR with 127 customers",
                "Page #2: Expanding to European markets"
            ],
            created_at=datetime.now() - timedelta(days=30),
            updated_at=datetime.now() - timedelta(hours=6)
        )
    ]
    return companies

def generate_mock_tasks() -> Dict[str, List[Task]]:
    """Generate tasks for companies."""
    return {
        "company_1": [
            Task(
                id="task_1",
                title="Schedule initial meeting with founders",
                description="Set up a call to understand their product roadmap and market approach.",
                company_id="company_1",
                assignee="John Doe",
                deadline=datetime.now() + timedelta(days=3),
                status=TaskStatus.NOT_STARTED,
                priority=TaskPriority.HIGH,
                category=TaskCategory.MEETING,
                created_at=datetime.now() - timedelta(days=1),
                updated_at=datetime.now() - timedelta(days=1)
            )
        ],
        "company_4": [
            Task(
                id="task_2",
                title="Technical due diligence review",
                description="Review blockchain architecture and security practices with engineering team.",
                company_id="company_4",
                assignee="Sarah Johnson",
                deadline=datetime.now() + timedelta(days=5),
                status=TaskStatus.IN_PROGRESS,
                priority=TaskPriority.HIGH,
                category=TaskCategory.TECHNICAL_REVIEW,
                created_at=datetime.now() - timedelta(days=3),
                updated_at=datetime.now() - timedelta(hours=1)
            ),
            Task(
                id="task_3",
                title="Financial model review",
                description="Analyze revenue projections and unit economics.",
                company_id="company_4",
                assignee="Jane Smith",
                deadline=datetime.now() + timedelta(days=7),
                status=TaskStatus.NOT_STARTED,
                priority=TaskPriority.MEDIUM,
                category=TaskCategory.FINANCIAL_REVIEW,
                created_at=datetime.now() - timedelta(days=2),
                updated_at=datetime.now() - timedelta(days=2)
            )
        ],
        "company_5": [
            Task(
                id="task_4",
                title="Portfolio company check-in",
                description="Monthly check-in with DataViz Pro leadership team on progress and challenges.",
                company_id="company_5",
                assignee="Michael Brown",
                deadline=datetime.now() + timedelta(days=14),
                status=TaskStatus.NOT_STARTED,
                priority=TaskPriority.MEDIUM,
                category=TaskCategory.MEETING,
                created_at=datetime.now() - timedelta(days=7),
                updated_at=datetime.now() - timedelta(days=7)
            )
        ]
    }

# =============================================================================
# SESSION STATE MANAGEMENT
# =============================================================================

def get_session_data():
    """Initialize session data if not exists."""
    if 'companies' not in st.session_state:
        st.session_state.companies = generate_mock_companies()
    if 'tasks' not in st.session_state:
        st.session_state.tasks = generate_mock_tasks()
    return st.session_state.companies, st.session_state.tasks

# =============================================================================
# UI COMPONENTS (matching exact original design)
# =============================================================================

def show_sidebar_navigation():
    """Sidebar navigation matching original exactly."""
    st.sidebar.markdown("# DVC Portfolio Dashboard")
    st.sidebar.markdown("*Sandbox Prototype*")
    
    st.sidebar.markdown("---")
    
    # Navigation links matching original
    st.sidebar.markdown("**Navigation**")
    
    # Create navigation buttons
    nav_options = ["Funds", "Companies", "Pipeline", "Jobs"]
    
    # Use session state to track current page
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Pipeline"
    
    for option in nav_options:
        if st.sidebar.button(option, key=f"nav_{option}", use_container_width=True):
            st.session_state.current_page = option
    
    st.sidebar.markdown("---")
    
    # Actions section
    st.sidebar.markdown("**Actions:**")
    if st.sidebar.button("+ Add Company", use_container_width=True):
        st.session_state.show_add_company = True
    
    st.sidebar.markdown("---")
    
    # Prototype info
    st.sidebar.info(
        "🎨 **Prototype Mode**\n\n"
        "This is a sandbox with mock data.\n"
        "Perfect for demonstrating features!\n\n"
        "Data resets when you refresh the page."
    )

def show_company_card(company: Company):
    """Show company card matching original design exactly."""
    # Company card container
    with st.container(border=True):
        # Top row: Logo and company name
        col1, col2 = st.columns([1, 6])
        
        with col1:
            # Company logo placeholder (gray square)
            st.markdown(f"""
                <div style="
                    width: 60px; 
                    height: 60px; 
                    background-color: #f0f0f0; 
                    border-radius: 8px; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    font-weight: bold; 
                    color: #666;
                    font-size: 12px;
                ">
                    {company.name[:8]}
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"### [{company.name}](https://{company.name.lower().replace(' ', '')}.com)")
            
            # Status and timeline
            st.markdown(f"**{company.stage}** | {format_relative_time(company.created_at)}")
            
            # Introduction
            st.markdown(f"Introduction by {company.introduction_by}")
        
        st.markdown("---")
        
        # Status dropdown and signals
        col1, col2 = st.columns([2, 3])
        
        with col1:
            # Status dropdown (matching original)
            status_options = [s.value for s in CompanyStatus]
            current_status = company.status.value
            new_status = st.selectbox(
                "Status",
                status_options,
                index=status_options.index(current_status),
                key=f"status_{company.id}",
                label_visibility="collapsed"
            )
            
            if new_status != current_status:
                company.status = CompanyStatus(new_status)
                company.updated_at = datetime.now()
                st.rerun()
        
        with col2:
            # Signals section
            if company.signals:
                for signal in company.signals:
                    st.markdown(f"🔵 {signal}")
            else:
                st.markdown("🔵 No signals for this company.")
        
        # Action button
        if st.button("View", key=f"view_{company.id}"):
            st.session_state.selected_company = company.id
            st.session_state.show_company_details = True
            st.rerun()
        
        # Company description
        st.markdown(f"*{company.description}*")
        
        # Bullet points
        if company.bullet_points:
            for point in company.bullet_points:
                st.markdown(f"• {point}")

def format_relative_time(dt: datetime) -> str:
    """Format relative time like 'Yesterday', '2 days ago', etc."""
    now = datetime.now()
    diff = now - dt
    
    if diff.days == 0:
        return "Today"
    elif diff.days == 1:
        return "Yesterday"
    else:
        return f"{diff.days} days ago"

def show_pipeline_page():
    """Pipeline page matching original design exactly."""
    companies, tasks = get_session_data()
    
    # Main tabs matching original
    tabs = st.tabs(["New Company", "In Progress", "Diligence", "Offered to Invest", "Going to Pass"])
    
    # Filter companies by status
    status_mapping = {
        "New Company": CompanyStatus.NEW_COMPANY,
        "In Progress": CompanyStatus.IN_PROGRESS,
        "Diligence": CompanyStatus.DILIGENCE,
        "Offered to Invest": CompanyStatus.OFFERED_TO_INVEST,
        "Going to Pass": CompanyStatus.GOING_TO_PASS
    }
    
    for tab, tab_name in zip(tabs, status_mapping.keys()):
        with tab:
            # Get companies for this tab
            filtered_companies = [c for c in companies if c.status == status_mapping[tab_name]]
            
            if filtered_companies:
                for company in filtered_companies:
                    show_company_card(company)
                    st.markdown("")  # Add spacing between cards
            else:
                st.info(f"No companies in {tab_name} status.")

def show_companies_page():
    """Companies page."""
    companies, tasks = get_session_data()
    
    st.header("Companies")
    
    # Show all companies in a list
    for company in companies:
        show_company_card(company)
        st.markdown("")

def show_funds_page():
    """Funds page."""
    st.header("Funds")
    st.info("Fund information would be displayed here in the full version.")

def show_jobs_page():
    """Jobs page."""
    st.header("Jobs")
    st.info("Job board would be displayed here in the full version.")

def show_company_details(company: Company):
    """Show detailed company view with task management."""
    st.header(f"🏢 {company.name}")
    
    # Back button
    if st.button("← Back to Pipeline"):
        st.session_state.show_company_details = False
        st.rerun()
    
    st.divider()
    
    # Company info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"**Stage:** {company.stage}")
        st.markdown(f"**Status:** {company.status.value}")
    
    with col2:
        st.markdown(f"**Introduction by:** {company.introduction_by}")
        st.markdown(f"**Created:** {company.created_at.strftime('%m/%d/%Y')}")
    
    with col3:
        st.markdown(f"**Last Updated:** {company.updated_at.strftime('%m/%d/%Y')}")
    
    st.divider()
    
    # Description
    st.markdown("**Description:**")
    st.write(company.description)
    
    # Signals
    if company.signals:
        st.markdown("**Signals:**")
        for signal in company.signals:
            st.write(f"• {signal}")
    
    # Bullet points
    if company.bullet_points:
        st.markdown("**Key Points:**")
        for point in company.bullet_points:
            st.write(f"• {point}")
    
    st.divider()
    
    # Tasks section
    show_tasks_section(company)

def show_tasks_section(company: Company):
    """Show tasks section for company details."""
    st.subheader("📋 Tasks")
    
    # Get tasks for this company
    tasks = st.session_state.tasks.get(company.id, [])
    
    # Add new task form
    with st.expander("➕ Add New Task", expanded=False):
        with st.form("add_task_form"):
            task_title = st.text_input("Task Title*", placeholder="e.g., Schedule meeting with founders")
            task_description = st.text_area("Description", placeholder="Additional details...")
            
            col1, col2 = st.columns(2)
            with col1:
                task_assignee = st.selectbox("Assignee", ["John Doe", "Jane Smith", "Sarah Johnson", "Michael Brown", "Emily Davis"])
                task_priority = st.selectbox("Priority", [p.value for p in TaskPriority])
            with col2:
                task_deadline = st.date_input("Deadline", value=datetime.now() + timedelta(days=7))
                task_category = st.selectbox("Category", [c.value for c in TaskCategory])
            
            submitted = st.form_submit_button("Add Task", type="primary")
            
            if submitted and task_title:
                new_task = Task(
                    id=str(uuid.uuid4()),
                    title=task_title,
                    description=task_description,
                    company_id=company.id,
                    assignee=task_assignee,
                    deadline=datetime.combine(task_deadline, datetime.min.time()),
                    status=TaskStatus.NOT_STARTED,
                    priority=TaskPriority(task_priority),
                    category=TaskCategory(task_category),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                if company.id not in st.session_state.tasks:
                    st.session_state.tasks[company.id] = []
                st.session_state.tasks[company.id].append(new_task)
                
                st.success(f"✅ Task '{task_title}' added successfully!")
                st.rerun()
    
    # Display tasks
    if not tasks:
        st.info("📝 No tasks yet. Add your first task above!")
        return
    
    # Task filters
    col1, col2 = st.columns(2)
    
    with col1:
        status_filter = st.multiselect(
            "Filter by Status",
            options=[s.value for s in TaskStatus],
            default=[TaskStatus.NOT_STARTED.value, TaskStatus.IN_PROGRESS.value]
        )
    
    with col2:
        priority_filter = st.multiselect(
            "Filter by Priority",
            options=[p.value for p in TaskPriority],
            default=[p.value for p in TaskPriority]
        )
    
    # Filter tasks
    filtered_tasks = [
        task for task in tasks
        if task.status.value in status_filter and task.priority.value in priority_filter
    ]
    
    # Display tasks
    for task in filtered_tasks:
        is_overdue = task.deadline < datetime.now() and task.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]
        
        # Priority and status emojis
        priority_emojis = {TaskPriority.LOW: "🟢", TaskPriority.MEDIUM: "🟡", TaskPriority.HIGH: "🔴", TaskPriority.URGENT: "🚨"}
        status_emojis = {TaskStatus.NOT_STARTED: "⭕", TaskStatus.IN_PROGRESS: "🔄", TaskStatus.BLOCKED: "🚫", TaskStatus.COMPLETED: "✅", TaskStatus.CANCELLED: "❌"}
        
        with st.container(border=True):
            col1, col2, col3 = st.columns([4, 2, 1])
            
            with col1:
                priority_emoji = priority_emojis.get(task.priority, "⚪")
                status_emoji = status_emojis.get(task.status, "⭕")
                overdue_text = " 🕐 OVERDUE" if is_overdue else ""
                
                st.markdown(f"**{priority_emoji} {task.title} {status_emoji}{overdue_text}**")
                if task.description:
                    st.write(task.description)
            
            with col2:
                st.write(f"**Assignee:** {task.assignee}")
                st.write(f"**Due:** {task.deadline.strftime('%m/%d/%Y')}")
                st.write(f"**Category:** {task.category.value}")
            
            with col3:
                if task.status != TaskStatus.COMPLETED:
                    if st.button("✅ Complete", key=f"complete_{task.id}"):
                        task.status = TaskStatus.COMPLETED
                        task.completed_at = datetime.now()
                        task.updated_at = datetime.now()
                        st.rerun()

def show_add_company_form():
    """Show add company form."""
    st.header("Add New Company")
    
    if st.button("← Back"):
        st.session_state.show_add_company = False
        st.rerun()
    
    with st.form("add_company_form"):
        name = st.text_input("Company Name*")
        description = st.text_area("Description*")
        stage = st.selectbox("Stage", ["Pre-seed", "Seed", "Series A", "Series B", "Series C+"])
        introduction_by = st.text_input("Introduction by*")
        
        submitted = st.form_submit_button("Add Company", type="primary")
        
        if submitted and name and description and introduction_by:
            new_company = Company(
                id=str(uuid.uuid4()),
                name=name,
                description=description,
                status=CompanyStatus.NEW_COMPANY,
                stage=stage,
                introduction_by=introduction_by,
                signals=["No signals for this company."],
                bullet_points=[],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            st.session_state.companies.append(new_company)
            st.session_state.show_add_company = False
            
            st.success(f"✅ Company '{name}' added successfully!")
            st.rerun()

# =============================================================================
# MAIN APP
# =============================================================================

def main():
    """Main application matching original design exactly."""
    st.set_page_config(
        page_title="DVC Portfolio Dashboard",
        layout='wide',
        page_icon="🎨"
    )
    
    # Initialize session state
    if 'show_company_details' not in st.session_state:
        st.session_state.show_company_details = False
    if 'show_add_company' not in st.session_state:
        st.session_state.show_add_company = False
    
    # Initialize data
    get_session_data()
    
    # Sidebar navigation
    show_sidebar_navigation()
    
    # Main content area
    if st.session_state.show_add_company:
        show_add_company_form()
    elif st.session_state.show_company_details:
        # Show company details
        selected_company_id = st.session_state.get('selected_company')
        if selected_company_id:
            companies, _ = get_session_data()
            selected_company = next((c for c in companies if c.id == selected_company_id), None)
            if selected_company:
                show_company_details(selected_company)
            else:
                st.error("Company not found")
                st.session_state.show_company_details = False
                st.rerun()
    else:
        # Show main pages based on navigation
        if st.session_state.current_page == "Pipeline":
            show_pipeline_page()
        elif st.session_state.current_page == "Companies":
            show_companies_page()
        elif st.session_state.current_page == "Funds":
            show_funds_page()
        elif st.session_state.current_page == "Jobs":
            show_jobs_page()

if __name__ == "__main__":
    main()

