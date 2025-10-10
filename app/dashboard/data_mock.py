"""
Mock data layer for local development - matches production data structure
"""
import pandas as pd
import typing
from datetime import datetime, timedelta, timezone
from bson import ObjectId
from app.shared.company import Company

# Mock companies data matching the structure from screenshots
MOCK_COMPANIES = [
    {
        "_id": ObjectId("68e69a2dc32b590896149739"),
        "name": "Generous",
        "status": "New Company",
        "website": "https://meetgenerous.com",
        "shortDescription": "An AI-powered gifting platform that offers personalized gift recommendations and transaction handling to reduce consumer anxiety and financial losses for retailers.",
        "mainIndustry": "AI, E-commerce, Artificial Intelligence",
        "summary": "Generous presents an exceptional opportunity to invest in the next generation of e-commerce and AI-powered consumer platforms. Founded by Kyle Montgomery and Vlad Turcu, the company has already established strategic partnerships with industry giants like Salesforce and Shopify. With over 800 people on the waitlist and access to 400+ gift card brands, Generous is positioned to capture a significant share of the $160 billion gifting market.",
        "problem": "Gifting causes significant anxiety for consumers and financial losses for retailers. 71% of consumers say gifting causes anxiety. Current gifting solutions are fragmented and don't provide personalized recommendations.",
        "solution": "Generous is an AI-powered gifting assistant and e-commerce marketplace that connects gifters, merchants, and recipients. The platform features intelligent occasion remembering, AI-powered gift recommendations, Autogift™ for automated gifting, a comprehensive dashboard for tracking, and a retail brand platform for merchants to showcase their products.",
        "marketOpportunity": "The global gifting market is valued at $160 billion and growing at 8% annually. Digital gifting represents the fastest-growing segment with 25% year-over-year growth.",
        "introductionSource": "Alice Yagolnitser",
        "source": "Alice Yagolnitser",
        "blurb": "An AI-powered gifting platform that offers personalized gift recommendations and transaction handling to reduce consumer anxiety and financial losses for retailers.",
        "createdAt": datetime.now(timezone.utc) - timedelta(days=1),
        "bulletPoints": [
            "Page #2: 71% of consumers say gifting causes anxiety.",
            "Page #3: AI-powered gifting, connected"
        ],
        "signals": "No signals for this company.",
        "fundingStage": "Pre-seed/seed (Early)",
        "team": [
            {"name": "Kyle Montgomery", "role": "Co-founder & CEO"},
            {"name": "Vlad Turcu", "role": "Co-founder & CTO"}
        ],
        "partnerships": ["Salesforce", "Shopify"],
        "metrics": {
            "waitlist": "800+",
            "giftCardBrands": "400+"
        }
    },
    {
        "_id": ObjectId("68e69a2dc32b590896149740"),
        "name": "TechFlow",
        "status": "Processing", 
        "website": "https://techflow.io",
        "shortDescription": "A comprehensive workflow automation platform that helps teams streamline their processes and increase productivity through intelligent task management.",
        "mainIndustry": "SaaS, Productivity, Workflow Automation",
        "summary": "TechFlow is revolutionizing how teams collaborate and manage their workflows. The platform integrates with over 100+ popular tools and uses AI to automatically optimize team processes. With 2,500+ active users and $50K MRR, TechFlow is experiencing rapid growth in the competitive productivity software market.",
        "problem": "Teams struggle with fragmented workflows across multiple tools, leading to decreased productivity and missed deadlines. 78% of knowledge workers report spending significant time on manual coordination tasks.",
        "solution": "TechFlow provides a unified workflow automation platform with intelligent task routing, automated notifications, and seamless integration with existing tools. Features include drag-and-drop workflow builder, AI-powered task prioritization, and real-time collaboration tools.",
        "marketOpportunity": "The workflow automation market is expected to reach $19.6 billion by 2025, with enterprise adoption growing at 35% annually.",
        "introductionSource": "Sarah Chen",
        "source": "Sarah Chen",
        "blurb": "A comprehensive workflow automation platform that helps teams streamline their processes and increase productivity through intelligent task management.",
        "createdAt": datetime.now(timezone.utc) - timedelta(days=2),
        "bulletPoints": [
            "Page #1: 78% of workers struggle with fragmented workflows.",
            "Page #4: AI-powered task optimization increases productivity by 40%"
        ],
        "signals": "Strong growth signals: 40% month-over-month user growth.",
        "fundingStage": "Seed",
        "team": [
            {"name": "Sarah Chen", "role": "Founder & CEO"},
            {"name": "Marcus Rodriguez", "role": "Co-founder & CTO"}
        ],
        "metrics": {
            "activeUsers": "2,500+",
            "mrr": "$50K",
            "integrations": "100+"
        }
    },
    {
        "_id": ObjectId("68e69a2dc32b590896149741"),
        "name": "HealthSync",
        "status": "Contacted",
        "website": "https://healthsync.app",
        "shortDescription": "A comprehensive healthcare data synchronization platform that connects patients, providers, and payers through secure, real-time data exchange.",
        "mainIndustry": "Healthcare, HealthTech, Data Synchronization",
        "summary": "HealthSync addresses the critical need for seamless healthcare data exchange between different stakeholders. The platform ensures HIPAA-compliant data sharing while reducing administrative burden for healthcare providers. With partnerships with 15 major health systems and processing 100K+ patient records monthly, HealthSync is well-positioned for growth.",
        "problem": "Healthcare data remains siloed across different systems, leading to fragmented patient care and increased administrative costs. Providers spend 40% of their time on administrative tasks rather than patient care.",
        "solution": "HealthSync provides a secure, real-time data synchronization platform that connects electronic health records (EHRs), insurance systems, and patient portals. Features include automated data validation, real-time synchronization, and comprehensive audit trails.",
        "marketOpportunity": "The healthcare data integration market is valued at $4.2 billion and growing at 12% annually, driven by increasing digitization and interoperability requirements.",
        "introductionSource": "Dr. Michael Thompson",
        "source": "Dr. Michael Thompson",
        "blurb": "A comprehensive healthcare data synchronization platform that connects patients, providers, and payers through secure, real-time data exchange.",
        "createdAt": datetime.now(timezone.utc) - timedelta(days=5),
        "bulletPoints": [
            "Page #1: 40% of provider time spent on administrative tasks.",
            "Page #2: Healthcare data silos cost $350B annually in inefficiencies"
        ],
        "signals": "Positive regulatory signals: FDA fast-track designation for core platform.",
        "fundingStage": "Series A",
        "team": [
            {"name": "Dr. Michael Thompson", "role": "Founder & CEO"},
            {"name": "Lisa Park", "role": "Co-founder & CTO"},
            {"name": "James Wilson", "role": "VP of Sales"}
        ],
        "metrics": {
            "healthSystems": "15+",
            "patientRecords": "100K+ monthly",
            "compliance": "HIPAA certified"
        }
    }
]

# Mock investments data
MOCK_INVESTMENTS = [
    {
        "id": "inv_001",
        "company_name": "Generous",
        "investment_amount": "$500K",
        "investment_date": "2024-01-15",
        "stage": "Pre-seed",
        "status": "Active"
    },
    {
        "id": "inv_002", 
        "company_name": "TechFlow",
        "investment_amount": "$1.2M",
        "investment_date": "2024-02-20",
        "stage": "Seed",
        "status": "Active"
    },
    {
        "id": "inv_003",
        "company_name": "HealthSync", 
        "investment_amount": "$2.5M",
        "investment_date": "2024-03-10",
        "stage": "Series A",
        "status": "Active"
    }
]

# Mock jobs data
MOCK_JOBS = [
    {
        "id": "job_001",
        "title": "Senior Software Engineer",
        "company": "Generous",
        "location": "San Francisco, CA",
        "type": "Full-time",
        "posted_date": datetime.now(timezone.utc) - timedelta(days=3),
        "description": "Join our team building the future of AI-powered gifting platforms."
    },
    {
        "id": "job_002",
        "title": "Product Manager",
        "company": "TechFlow", 
        "location": "Remote",
        "type": "Full-time",
        "posted_date": datetime.now(timezone.utc) - timedelta(days=1),
        "description": "Lead product strategy for our workflow automation platform."
    }
]

def get_mock_companies(query: dict = None, sort: list = None) -> list:
    """Return mock companies data matching MongoDB query structure"""
    companies = MOCK_COMPANIES.copy()
    
    if query:
        filtered_companies = []
        for company in companies:
            # Handle MongoDB-style queries
            if 'status' in query:
                query_status = query['status']
                if isinstance(query_status, dict) and '$in' in query_status:
                    # Handle $in queries like {'status': {'$in': ['New Company', 'Processing']}}
                    if company.get('status') in query_status['$in']:
                        filtered_companies.append(company)
                elif company.get('status') == query_status:
                    # Handle simple equality queries
                    filtered_companies.append(company)
            elif '_id' in query:
                # Handle _id queries for company detail page
                if str(company.get('_id')) == str(query['_id']):
                    filtered_companies.append(company)
            elif 'name' in query:
                if company.get('name', '').lower().find(query['name'].lower()) != -1:
                    filtered_companies.append(company)
            else:
                filtered_companies.append(company)
        companies = filtered_companies
    
    # Simple sorting (basic implementation)
    if sort and sort[0][0] == 'createdAt':
        reverse = sort[0][1] == -1
        companies.sort(key=lambda x: x.get('createdAt', datetime.now(timezone.utc)), reverse=reverse)
    
    return companies

def get_mock_investments(**options) -> pd.DataFrame:
    """Return mock investments as DataFrame matching Airtable structure"""
    return pd.DataFrame(MOCK_INVESTMENTS).set_index('id')

def get_mock_jobs(**options) -> pd.DataFrame:
    """Return mock jobs as DataFrame"""
    jobs_data = []
    for job in MOCK_JOBS:
        job_copy = job.copy()
        job_copy['posted_date'] = job_copy['posted_date'].isoformat()
        jobs_data.append(job_copy)
    return pd.DataFrame(jobs_data).set_index('id')

def get_mock_company_by_id(company_id: str) -> typing.Optional[Company]:
    """Return mock company by ID as Company object"""
    for company_data in MOCK_COMPANIES:
        if str(company_data['_id']) == company_id:
            return Company(
                id=str(company_data['_id']),
                name=company_data.get('name', ''),
                status=company_data.get('status', ''),
                website=company_data.get('website', ''),
                blurb=company_data.get('blurb', ''),
                createdAt=company_data.get('createdAt'),
                ourData={
                    'mainIndustry': company_data.get('mainIndustry', ''),
                    'summary': company_data.get('summary', ''),
                    'problem': company_data.get('problem', ''),
                    'marketSize': company_data.get('marketOpportunity', ''),
                    'targetMarket': company_data.get('mainIndustry', ''),
                    'bulletPoints': company_data.get('bulletPoints', []),
                    'signals': company_data.get('signals', ''),
                    'fundingStage': company_data.get('fundingStage', ''),
                    'team': company_data.get('team', []),
                    'partnerships': company_data.get('partnerships', []),
                    'metrics': company_data.get('metrics', {})
                },
                spectrData={
                    'description': company_data.get('solution', '')
                }
            )
    return None

def get_mock_companies_by_status(status: str) -> list:
    """Return mock companies filtered by status"""
    return [company for company in MOCK_COMPANIES if company.get('status') == status]
