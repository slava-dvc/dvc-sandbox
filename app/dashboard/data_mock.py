"""
Mock data layer for local development - matches production data structure
"""
import pandas as pd
import typing
from datetime import datetime, timedelta, timezone, date
from bson import ObjectId
from app.shared.company import Company
from app.shared.task import Task

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
    },
    {
        "_id": ObjectId("68e69a2dc32b590896149742"),
        "name": "CloudScale AI",
        "status": "New Company",
        "website": "https://cloudscaleai.com",
        "shortDescription": "Enterprise-grade AI infrastructure platform that enables companies to deploy and scale machine learning models at unprecedented speed and efficiency.",
        "mainIndustry": "AI Infrastructure, Cloud Computing, Machine Learning",
        "summary": "CloudScale AI is revolutionizing enterprise AI deployment with its cutting-edge infrastructure platform. The company has developed proprietary technology that reduces AI model deployment time from weeks to hours, while maintaining enterprise-grade security and scalability. With partnerships with AWS and Microsoft Azure, and 150+ enterprise customers processing 10M+ predictions daily, CloudScale AI is positioned to capture significant market share in the rapidly growing AI infrastructure market.",
        "problem": "Enterprise AI deployment is slow, expensive, and complex. Companies take 6-12 months to deploy AI models, with 70% of AI projects failing due to infrastructure challenges. Current solutions lack enterprise-grade security and scalability.",
        "solution": "CloudScale AI provides a unified platform for AI model deployment, scaling, and management. Features include automated model optimization, real-time scaling, enterprise security compliance, and seamless integration with existing cloud infrastructure. The platform reduces deployment time by 95% and operational costs by 60%.",
        "marketOpportunity": "The AI infrastructure market is valued at $15.8 billion and growing at 28% annually. Enterprise AI adoption is accelerating with 85% of companies planning to increase AI investments in 2024.",
        "introductionSource": "David Kim",
        "source": "David Kim",
        "blurb": "Enterprise-grade AI infrastructure platform that enables companies to deploy and scale machine learning models at unprecedented speed and efficiency.",
        "createdAt": datetime.now(timezone.utc) - timedelta(hours=6),
        "bulletPoints": [
            "Page #1: 95% reduction in AI deployment time (weeks to hours)",
            "Page #2: 150+ enterprise customers with 10M+ daily predictions"
        ],
        "signals": "Strong technical signals: AWS and Microsoft Azure partnerships confirmed.",
        "fundingStage": "Series A",
        "team": [
            {"name": "David Kim", "role": "Founder & CEO"},
            {"name": "Dr. Sarah Patel", "role": "Co-founder & CTO"},
            {"name": "Michael Torres", "role": "VP of Engineering"}
        ],
        "metrics": {
            "enterpriseCustomers": "150+",
            "dailyPredictions": "10M+",
            "deploymentTimeReduction": "95%",
            "costReduction": "60%"
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
        "status": "Active",
        "Fund": "DVC Fund I"
    },
    {
        "id": "inv_002", 
        "company_name": "TechFlow",
        "investment_amount": "$1.2M",
        "investment_date": "2024-02-20",
        "stage": "Seed",
        "status": "Active",
        "Fund": "DVC Fund I"
    },
    {
        "id": "inv_003",
        "company_name": "HealthSync", 
        "investment_amount": "$2.5M",
        "investment_date": "2024-03-10",
        "stage": "Series A",
        "status": "Active",
        "Fund": "DVC Fund I"
    },
    {
        "id": "inv_004",
        "company_name": "CloudScale AI",
        "investment_amount": "$3.8M",
        "investment_date": "2024-10-14",
        "stage": "Series A",
        "status": "Active",
        "Fund": "DVC Fund I"
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


# ============================================================================
# MOCK TASK DATA
# ============================================================================

def get_mock_tasks_for_company(company_id: str) -> typing.List[dict]:
    """Return mock tasks for a specific company with updated Task model fields"""
    # Mock tasks for Generous company (68e69a2dc32b590896149739)
    if company_id == "68e69a2dc32b590896149739":
        return [
            {
                "id": "task_001",
                "company_id": company_id,
                "text": "Draft IC memo for investment committee",
                "due_date": date.today() + timedelta(days=5),
                "assignee": "Marina",
                "status": "active",
                "outcome": None,
                "notes": "Focus on AI differentiation and market opportunity. Include competitive analysis with Shopify and Salesforce partnerships.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=2),
                "created_by": "Nick",
                "completed_at": None
            },
            {
                "id": "task_002", 
                "company_id": company_id,
                "text": "Review pitch deck and financials",
                "due_date": date.today(),
                "assignee": "Marina",
                "status": "active",
                "outcome": None,
                "notes": "Pay special attention to the $160B market sizing and 800+ waitlist validation.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=1),
                "created_by": "Nick",
                "completed_at": None
            },
            {
                "id": "task_003",
                "company_id": company_id,
                "text": "Schedule follow-up call with founders",
                "due_date": date.today() + timedelta(days=1),
                "assignee": "Nick",
                "status": "active",
                "outcome": None,
                "notes": "Discuss technical roadmap and partnership expansion plans.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=1),
                "created_by": "Marina",
                "completed_at": None
            },
            {
                "id": "task_004",
                "company_id": company_id,
                "text": "Get technical architecture documentation",
                "due_date": date.today() - timedelta(days=1),
                "assignee": "Vlad",
                "status": "active",
                "outcome": None,
                "notes": "Need to understand scalability for 400+ gift card brands integration.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=3),
                "created_by": "Nick",
                "completed_at": None
            },
            {
                "id": "task_005",
                "company_id": company_id,
                "text": "Check references from previous investors",
                "due_date": date.today() - timedelta(days=2),
                "assignee": "Nick",
                "status": "completed",
                "outcome": "All references positive. Team execution is strong.",
                "notes": "Spoke with 3 previous investors, all had positive feedback about founder execution and market timing.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=5),
                "created_by": "Marina",
                "completed_at": datetime.now(timezone.utc) - timedelta(days=1)
            }
        ]
    
    # Mock tasks for TechFlow company (68e69a2dc32b590896149740)
    elif company_id == "68e69a2dc32b590896149740":
        return [
            {
                "id": "task_009",
                "company_id": company_id,
                "text": "Analyze competitive landscape",
                "due_date": date.today() + timedelta(days=3),
                "assignee": "Nick",
                "status": "active",
                "outcome": None,
                "notes": "Focus on Zapier, Microsoft Power Automate, and Asana. Document key differentiators.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=2),
                "created_by": "Marina",
                "completed_at": None
            },
            {
                "id": "task_010",
                "company_id": company_id,
                "text": "Review technical architecture",
                "due_date": date.today() + timedelta(days=8),
                "assignee": "Alexey",
                "status": "active",
                "outcome": None,
                "notes": "Assess scalability for 100+ integrations and 2,500+ users. Check API rate limits.",
                "created_at": datetime.now(timezone.utc) - timedelta(hours=6),
                "created_by": "Nick",
                "completed_at": None
            },
            {
                "id": "task_011",
                "company_id": company_id,
                "text": "Validate MRR growth metrics",
                "due_date": date.today() + timedelta(days=1),
                "assignee": "Mel",
                "status": "active",
                "outcome": None,
                "notes": "Verify the $50K MRR claim and analyze churn rates.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=1),
                "created_by": "Nick",
                "completed_at": None
            },
            {
                "id": "task_012",
                "company_id": company_id,
                "text": "Schedule demo with founders",
                "due_date": date.today() - timedelta(days=1),
                "assignee": "Charles",
                "status": "completed",
                "outcome": "Demo completed successfully. Product shows strong potential.",
                "notes": "Demo went well. Team is impressive and product has clear market fit.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=3),
                "created_by": "Marina",
                "completed_at": datetime.now(timezone.utc) - timedelta(hours=2)
            }
        ]
    
    # Mock tasks for HealthSync company (68e69a2dc32b590896149741)
    elif company_id == "68e69a2dc32b590896149741":
        return [
            {
                "id": "task_013",
                "company_id": company_id,
                "text": "Due diligence on HIPAA compliance",
                "due_date": date.today() + timedelta(days=14),
                "assignee": "Marina",
                "status": "active",
                "outcome": None,
                "notes": "Focus on data encryption standards and patient consent management. Review with legal team by end of week.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=3),
                "created_by": "Nick",
                "completed_at": None
            },
            {
                "id": "task_014",
                "company_id": company_id,
                "text": "Verify health system partnerships",
                "due_date": date.today() + timedelta(days=7),
                "assignee": "Mel",
                "status": "active",
                "outcome": None,
                "notes": "Confirm the 15+ health systems claim. Get partnership agreements and integration details.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=2),
                "created_by": "Marina",
                "completed_at": None
            },
            {
                "id": "task_015",
                "company_id": company_id,
                "text": "Review FDA fast-track designation",
                "due_date": date.today() + timedelta(days=2),
                "assignee": "Charles",
                "status": "active",
                "outcome": None,
                "notes": "Verify FDA fast-track status and understand regulatory timeline implications.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=1),
                "created_by": "Nick",
                "completed_at": None
            },
            {
                "id": "task_016",
                "company_id": company_id,
                "text": "Technical assessment of data sync platform",
                "due_date": date.today() + timedelta(days=10),
                "assignee": "Vlad",
                "status": "active",
                "outcome": None,
                "notes": "Evaluate scalability for 100K+ patient records monthly. Check real-time sync capabilities.",
                "created_at": datetime.now(timezone.utc) - timedelta(hours=18),
                "created_by": "Marina",
                "completed_at": None
            }
        ]
    
    # Mock tasks for AI Startup company (68e69a2dc32b590896149742)
    elif company_id == "68e69a2dc32b590896149742":
        return [
            {
                "id": "task_020",
                "company_id": company_id,
                "text": "Review AI model performance metrics",
                "due_date": date.today() + timedelta(days=4),
                "assignee": "Alexey",
                "status": "active",
                "outcome": None,
                "notes": "Evaluate accuracy, latency, and cost metrics for production deployment.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=2),
                "created_by": "Marina",
                "completed_at": None
            },
            {
                "id": "task_021",
                "company_id": company_id,
                "text": "Platform automation improvements",
                "due_date": date.today() + timedelta(days=6),
                "assignee": "Tony",
                "status": "active",
                "outcome": None,
                "notes": "Implement automated workflow triggers for investor updates and portfolio monitoring.",
                "created_at": datetime.now(timezone.utc) - timedelta(hours=12),
                "created_by": "Marina",
                "completed_at": None
            },
            {
                "id": "task_022",
                "company_id": company_id,
                "text": "Investor relations update",
                "due_date": date.today() + timedelta(days=3),
                "assignee": "Elena",
                "status": "active",
                "outcome": None,
                "notes": "Prepare monthly portfolio update and community engagement metrics for LPs.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=1),
                "created_by": "Nick",
                "completed_at": None
            },
            {
                "id": "task_023",
                "company_id": company_id,
                "text": "Build AI agent for deal sourcing",
                "due_date": date.today() + timedelta(days=14),
                "assignee": "Vlad",
                "status": "active",
                "outcome": None,
                "notes": "Develop automated workflow to connect data sources and enhance deal pipeline efficiency.",
                "created_at": datetime.now(timezone.utc) - timedelta(hours=24),
                "created_by": "Marina",
                "completed_at": None
            },
            {
                "id": "task_024",
                "company_id": company_id,
                "text": "Board meeting preparation",
                "due_date": date.today() - timedelta(days=1),
                "assignee": "Slava",
                "status": "completed",
                "outcome": "Board materials prepared. All metrics and KPIs updated for Q4 review.",
                "notes": "Completed financial review and prepared strategic recommendations for board discussion.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=5),
                "created_by": "Marina",
                "completed_at": datetime.now(timezone.utc) - timedelta(hours=4)
            }
        ]
    
    # Mock tasks for FinTech company (68e69a2dc32b590896149743)
    elif company_id == "68e69a2dc32b590896149743":
        return [
            {
                "id": "task_025",
                "company_id": company_id,
                "text": "Regulatory compliance review",
                "due_date": date.today() + timedelta(days=10),
                "assignee": "Mel",
                "status": "active",
                "outcome": None,
                "notes": "Review SEC compliance and banking regulations for fintech operations.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=3),
                "created_by": "Charles",
                "completed_at": None
            },
            {
                "id": "task_026",
                "company_id": company_id,
                "text": "Technical security audit",
                "due_date": date.today() + timedelta(days=7),
                "assignee": "Alexey",
                "status": "active",
                "outcome": None,
                "notes": "Conduct penetration testing and security review for payment processing systems.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=2),
                "created_by": "Vlad",
                "completed_at": None
            },
            {
                "id": "task_027",
                "company_id": company_id,
                "text": "Community event planning",
                "due_date": date.today() + timedelta(days=5),
                "assignee": "Elena",
                "status": "active",
                "outcome": None,
                "notes": "Plan fintech startup showcase event for portfolio companies and potential LPs.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=1),
                "created_by": "Marina",
                "completed_at": None
            },
            {
                "id": "task_028",
                "company_id": company_id,
                "text": "Product roadmap review",
                "due_date": date.today() + timedelta(days=2),
                "assignee": "Tony",
                "status": "active",
                "outcome": None,
                "notes": "Review product analytics and user feedback to prioritize next quarter features.",
                "created_at": datetime.now(timezone.utc) - timedelta(hours=18),
                "created_by": "Alexey",
                "completed_at": None
            },
            {
                "id": "task_029",
                "company_id": company_id,
                "text": "Due diligence call with founders",
                "due_date": date.today() - timedelta(days=2),
                "assignee": "Nick",
                "status": "completed",
                "outcome": "Call completed. Strong technical team with clear go-to-market strategy.",
                "notes": "Founders demonstrated deep understanding of compliance requirements and market opportunity.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=4),
                "created_by": "Marina",
                "completed_at": datetime.now(timezone.utc) - timedelta(days=2)
            }
        ]
    
    # Mock tasks for SaaS company (68e69a2dc32b590896149744)
    elif company_id == "68e69a2dc32b590896149744":
        return [
            {
                "id": "task_030",
                "company_id": company_id,
                "text": "Customer success metrics analysis",
                "due_date": date.today() + timedelta(days=6),
                "assignee": "Marina",
                "status": "active",
                "outcome": None,
                "notes": "Analyze churn rates, NPS scores, and expansion revenue trends.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=2),
                "created_by": "Nick",
                "completed_at": None
            },
            {
                "id": "task_031",
                "company_id": company_id,
                "text": "Platform scalability assessment",
                "due_date": date.today() + timedelta(days=12),
                "assignee": "Vlad",
                "status": "active",
                "outcome": None,
                "notes": "Evaluate infrastructure capacity for 10x user growth and enterprise features.",
                "created_at": datetime.now(timezone.utc) - timedelta(hours=24),
                "created_by": "Alexey",
                "completed_at": None
            },
            {
                "id": "task_032",
                "company_id": company_id,
                "text": "Enterprise sales strategy review",
                "due_date": date.today() + timedelta(days=8),
                "assignee": "Charles",
                "status": "active",
                "outcome": None,
                "notes": "Review enterprise sales process and pricing strategy for large customers.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=1),
                "created_by": "Mel",
                "completed_at": None
            },
            {
                "id": "task_033",
                "company_id": company_id,
                "text": "Product analytics dashboard",
                "due_date": date.today() + timedelta(days=4),
                "assignee": "Tony",
                "status": "active",
                "outcome": None,
                "notes": "Build real-time dashboard for tracking product usage and feature adoption.",
                "created_at": datetime.now(timezone.utc) - timedelta(hours=12),
                "created_by": "Vlad",
                "completed_at": None
            },
            {
                "id": "task_034",
                "company_id": company_id,
                "text": "LP quarterly report",
                "due_date": date.today() - timedelta(days=3),
                "assignee": "Elena",
                "status": "completed",
                "outcome": "Report completed and sent to all LPs. Strong portfolio performance highlighted.",
                "notes": "Included portfolio company updates, financial metrics, and market analysis.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=7),
                "created_by": "Marina",
                "completed_at": datetime.now(timezone.utc) - timedelta(days=3)
            }
        ]
    
    # No tasks for other companies
    return []
