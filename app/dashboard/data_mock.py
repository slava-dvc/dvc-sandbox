"""
Mock data layer for local development - matches production data structure
"""
import pandas as pd
import typing
from datetime import datetime, timedelta, timezone, date
from bson import ObjectId
from app.shared.company import Company
from app.shared.task import Task

# Demo AI Portfolio Companies for Early-Stage Due Diligence
MOCK_COMPANIES = [
    {
        "_id": ObjectId("68e69a2dc32b590896149739"),
        "name": "VectorAI",
        "status": "Diligence",
        "website": "https://vectorai.io",
        "shortDescription": "Enterprise vector database for AI applications",
        "mainIndustry": "AI Infrastructure, Vector Databases, Machine Learning",
        "summary": "VectorAI is building the next generation of vector databases specifically optimized for AI applications. The platform enables real-time similarity search and retrieval-augmented generation (RAG) at enterprise scale. With 150+ enterprise customers and processing 10M+ queries daily, VectorAI addresses the critical infrastructure gap in the AI stack.",
        "problem": "Existing vector databases can't handle enterprise-scale AI workloads. Current solutions lack real-time performance, cost-effective scaling, and enterprise security features needed for production AI applications.",
        "solution": "VectorAI provides a purpose-built vector database with sub-millisecond query latency, automatic scaling, and enterprise-grade security. Features include real-time indexing, hybrid search (vector + keyword), and seamless integration with AI frameworks.",
        "marketOpportunity": "The vector database market is projected to reach $4.2B by 2027, growing at 45% annually. Enterprise AI adoption is driving demand for specialized infrastructure.",
        "introductionSource": "Sarah Chen",
        "source": "Sarah Chen",
        "blurb": "Enterprise vector database for AI applications",
        "createdAt": datetime.now(timezone.utc) - timedelta(days=3),
        "bulletPoints": [
            "Page #1: 10M+ daily queries with sub-millisecond latency",
            "Page #3: 150+ enterprise customers including Fortune 500"
        ],
        "signals": "Strong technical signals: AWS partnership confirmed, $2M ARR",
        "fundingStage": "Pre-seed",
        "team": [
            {"name": "Dr. Sarah Patel", "role": "Founder & CEO"},
            {"name": "Marcus Rodriguez", "role": "Co-founder & CTO"},
            {"name": "Lisa Wang", "role": "VP of Engineering"}
        ],
        "partnerships": ["AWS", "Microsoft Azure"],
        "metrics": {
            "enterpriseCustomers": "150+",
            "dailyQueries": "10M+",
            "arr": "$2M"
        }
    },
    {
        "_id": ObjectId("68e69a2dc32b590896149740"),
        "name": "CopilotMD",
        "status": "Diligence", 
        "website": "https://copilotmd.ai",
        "shortDescription": "AI-powered clinical decision support for physicians",
        "mainIndustry": "Healthcare AI, Clinical Decision Support, Medical Technology",
        "summary": "CopilotMD is revolutionizing healthcare with AI-powered clinical decision support that helps physicians make faster, more accurate diagnoses. The platform integrates with existing EHR systems and provides real-time recommendations based on patient data and clinical guidelines. With FDA breakthrough device designation and pilot programs at 5 major health systems, CopilotMD is positioned to transform clinical workflows.",
        "problem": "Physicians face information overload and time constraints, leading to diagnostic errors and delayed treatments. 40% of diagnostic errors could be prevented with better decision support tools.",
        "solution": "CopilotMD provides AI-powered clinical decision support that analyzes patient data, medical history, and symptoms to provide evidence-based recommendations. Features include real-time alerts, drug interaction checking, and automated documentation.",
        "marketOpportunity": "The clinical decision support market is valued at $1.8B and growing at 15% annually. Healthcare AI adoption is accelerating post-COVID.",
        "introductionSource": "Dr. Michael Thompson",
        "source": "Dr. Michael Thompson",
        "blurb": "AI-powered clinical decision support for physicians",
        "createdAt": datetime.now(timezone.utc) - timedelta(days=5),
        "bulletPoints": [
            "Page #1: FDA breakthrough device designation secured",
            "Page #2: Pilot programs at 5 major health systems"
        ],
        "signals": "Strong regulatory signals: FDA fast-track designation, HIPAA compliant",
        "fundingStage": "Seed",
        "team": [
            {"name": "Dr. Michael Thompson", "role": "Founder & CEO"},
            {"name": "Dr. Lisa Park", "role": "Co-founder & CTO"},
            {"name": "James Wilson", "role": "VP of Clinical Affairs"}
        ],
        "metrics": {
            "healthSystems": "5 pilot programs",
            "fdaStatus": "Breakthrough device",
            "accuracyRate": "94%"
        }
    },
    {
        "_id": ObjectId("68e69a2dc32b590896149741"),
        "name": "DataWeave",
        "status": "Contacted",
        "website": "https://dataweave.ai",
        "shortDescription": "Automated data transformation and quality for ML teams",
        "mainIndustry": "AI Data Pipeline, Machine Learning, Data Engineering",
        "summary": "DataWeave is solving the critical data quality problem in AI/ML workflows. The platform automatically cleans, transforms, and validates data for machine learning pipelines, reducing data preparation time from weeks to hours. With 200+ ML teams using the platform and processing 50TB+ of data monthly, DataWeave is becoming essential infrastructure for AI companies.",
        "problem": "ML teams spend 80% of their time on data preparation and quality issues. Poor data quality leads to model failures and unreliable AI systems. Current ETL tools are not designed for ML workflows.",
        "solution": "DataWeave provides automated data transformation and quality validation specifically for ML pipelines. Features include intelligent schema detection, automated data cleaning, and real-time quality monitoring.",
        "marketOpportunity": "The data preparation market is valued at $8.2B and growing at 20% annually. ML adoption is driving demand for specialized data tools.",
        "introductionSource": "David Kim",
        "source": "David Kim",
        "blurb": "Automated data transformation and quality for ML teams",
        "createdAt": datetime.now(timezone.utc) - timedelta(days=4),
        "bulletPoints": [
            "Page #1: 80% reduction in data preparation time",
            "Page #3: 200+ ML teams processing 50TB+ monthly"
        ],
        "signals": "Strong product-market fit: 95% customer retention rate",
        "fundingStage": "Pre-seed",
        "team": [
            {"name": "David Kim", "role": "Founder & CEO"},
            {"name": "Dr. Sarah Patel", "role": "Co-founder & CTO"},
            {"name": "Michael Torres", "role": "VP of Data Science"}
        ],
        "metrics": {
            "mlTeams": "200+",
            "dataProcessed": "50TB+ monthly",
            "retentionRate": "95%"
        }
    },
    {
        "_id": ObjectId("68e69a2dc32b590896149742"),
        "name": "SynthLabs",
        "status": "Diligence",
        "website": "https://synthlabs.ai",
        "shortDescription": "Generate privacy-compliant synthetic datasets for AI training",
        "mainIndustry": "Synthetic Data, Privacy Tech, AI Training Data",
        "summary": "SynthLabs is solving the critical data privacy challenge in AI development by generating high-quality synthetic datasets that preserve statistical properties while protecting privacy. The platform enables AI companies to train models without accessing real personal data. With 50+ enterprise customers and generating 100M+ synthetic records monthly, SynthLabs is becoming essential for privacy-compliant AI development.",
        "problem": "AI companies face increasing privacy regulations and data scarcity. GDPR, CCPA, and other privacy laws restrict access to personal data, while high-quality training data remains expensive and limited.",
        "solution": "SynthLabs generates privacy-compliant synthetic datasets using advanced generative models. Features include statistical fidelity validation, privacy guarantees, and domain-specific data generation for healthcare, finance, and other regulated industries.",
        "marketOpportunity": "The synthetic data market is valued at $2.1B and growing at 35% annually. Privacy regulations are driving adoption of synthetic data solutions.",
        "introductionSource": "Alice Yagolnitser",
        "source": "Alice Yagolnitser",
        "blurb": "Generate privacy-compliant synthetic datasets for AI training",
        "createdAt": datetime.now(timezone.utc) - timedelta(hours=8),
        "bulletPoints": [
            "Page #1: 100M+ synthetic records generated monthly",
            "Page #2: 50+ enterprise customers across regulated industries"
        ],
        "signals": "Strong compliance signals: SOC 2 Type II certified, GDPR compliant",
        "fundingStage": "Seed",
        "team": [
            {"name": "Dr. Rachel Chen", "role": "Founder & CEO"},
            {"name": "Alex Kumar", "role": "Co-founder & CTO"},
            {"name": "Maria Santos", "role": "VP of Privacy Engineering"}
        ],
        "metrics": {
            "enterpriseCustomers": "50+",
            "syntheticRecords": "100M+ monthly",
            "privacyCompliance": "SOC 2, GDPR"
        }
    },
    {
        "_id": ObjectId("68e69a2dc32b590896149743"),
        "name": "AgentOS",
        "status": "New Company",
        "website": "https://agentos.ai",
        "shortDescription": "Operating system for deploying and managing AI agents",
        "mainIndustry": "AI Agents, Multi-Agent Systems, AI Orchestration",
        "summary": "AgentOS is building the infrastructure layer for the AI agent economy. The platform enables companies to deploy, orchestrate, and manage multiple AI agents at scale. With early traction from 25+ companies and managing 500+ active agents, AgentOS is positioned to become the standard platform for AI agent deployment.",
        "problem": "AI agents are becoming powerful but lack infrastructure for deployment at scale. Companies struggle with agent coordination, resource management, and monitoring in production environments.",
        "solution": "AgentOS provides a unified platform for AI agent deployment and management. Features include multi-agent orchestration, resource optimization, monitoring and debugging, and seamless integration with existing AI models.",
        "marketOpportunity": "The AI agent market is projected to reach $12.8B by 2028, growing at 40% annually. Enterprise adoption of AI agents is accelerating.",
        "introductionSource": "Sarah Chen",
        "source": "Sarah Chen",
        "blurb": "Operating system for deploying and managing AI agents",
        "createdAt": datetime.now(timezone.utc) - timedelta(hours=12),
        "bulletPoints": [
            "Page #1: 500+ active agents managed across 25+ companies",
            "Page #3: 90% reduction in agent deployment complexity"
        ],
        "signals": "Early traction: Strong developer adoption, open source community",
        "fundingStage": "Pre-seed",
        "team": [
            {"name": "Jordan Lee", "role": "Founder & CEO"},
            {"name": "Dr. Priya Sharma", "role": "Co-founder & CTO"},
            {"name": "Tom Wilson", "role": "VP of Engineering"}
        ],
        "metrics": {
            "companies": "25+",
            "activeAgents": "500+",
            "developerAdoption": "1K+ GitHub stars"
        }
    }
]

# Mock investments data for AI portfolio companies
MOCK_INVESTMENTS = [
    {
        "id": "inv_001",
        "company_name": "VectorAI",
        "investment_amount": "$750K",
        "investment_date": "2024-01-15",
        "stage": "Pre-seed",
        "status": "Under Review",
        "Fund": "DVC Fund I",
        "Amount Invested": 750000
    },
    {
        "id": "inv_002", 
        "company_name": "CopilotMD",
        "investment_amount": "$1.5M",
        "investment_date": "2024-02-20",
        "stage": "Seed",
        "status": "Under Review",
        "Fund": "DVC Fund I",
        "Amount Invested": 1500000
    },
    {
        "id": "inv_003",
        "company_name": "DataWeave", 
        "investment_amount": "$650K",
        "investment_date": "2024-03-10",
        "stage": "Pre-seed",
        "status": "Under Review",
        "Fund": "DVC Fund I",
        "Amount Invested": 650000
    },
    {
        "id": "inv_004",
        "company_name": "SynthLabs",
        "investment_amount": "$2.2M",
        "investment_date": "2024-10-14",
        "stage": "Seed",
        "status": "Under Review",
        "Fund": "DVC Fund I",
        "Amount Invested": 2200000
    },
    {
        "id": "inv_005",
        "company_name": "AgentOS",
        "investment_amount": "$800K",
        "investment_date": "2024-10-16",
        "stage": "Pre-seed",
        "status": "Under Review",
        "Fund": "DVC Fund I",
        "Amount Invested": 800000
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
    """Return mock tasks for AI portfolio companies focused on due diligence workflows"""
    # Mock tasks for VectorAI company (68e69a2dc32b590896149739)
    if company_id == "68e69a2dc32b590896149739":
        return [
            {
                "id": "task_001",
                "company_id": company_id,
                "text": "Review technical architecture for scalability concerns",
                "due_date": date.today() + timedelta(days=2),
                "assignee": "Alexey",
                "status": "active",
                "outcome": None,
                "notes": "Focus on 10M+ daily queries performance and enterprise scalability. Check vector indexing algorithms.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=2),
                "created_by": "Nick",
                "completed_at": None
            },
            {
                "id": "task_002", 
                "company_id": company_id,
                "text": "Schedule founder call to discuss enterprise GTM",
                "due_date": date.today(),
                "assignee": "Nick",
                "status": "active",
                "outcome": None,
                "notes": "Discuss AWS/Azure partnerships and enterprise sales strategy. Validate $2M ARR claim.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=1),
                "created_by": "Marina",
                "completed_at": None
            },
            {
                "id": "task_003",
                "company_id": company_id,
                "text": "Research competitive landscape - Pinecone, Weaviate comparison",
                "due_date": date.today() + timedelta(days=1),
                "assignee": "Marina",
                "status": "active",
                "outcome": None,
                "notes": "Compare technical differentiation and market positioning against established players.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=1),
                "created_by": "Nick",
                "completed_at": None
            },
            {
                "id": "task_004",
                "company_id": company_id,
                "text": "Validate $4.2B TAM claim with market research",
                "due_date": date.today() - timedelta(days=1),
                "assignee": "Charles",
                "status": "active",
                "outcome": None,
                "notes": "Research vector database market sizing and growth projections. Check analyst reports.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=3),
                "created_by": "Nick",
                "completed_at": None
            },
            {
                "id": "task_005",
                "company_id": company_id,
                "text": "Reference check with AWS partnership contacts",
                "due_date": date.today() - timedelta(days=2),
                "assignee": "Nick",
                "status": "completed",
                "outcome": "AWS partnership confirmed. Strong technical team with clear differentiation in vector search performance.",
                "notes": "Spoke with AWS partner team. Partnership is legitimate and VectorAI has strong technical capabilities.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=5),
                "created_by": "Marina",
                "completed_at": datetime.now(timezone.utc) - timedelta(days=1)
            }
        ]
    
    # Mock tasks for CopilotMD company (68e69a2dc32b590896149740)
    elif company_id == "68e69a2dc32b590896149740":
        return [
            {
                "id": "task_009",
                "company_id": company_id,
                "text": "Verify regulatory pathway for clinical AI tool",
                "due_date": date.today() + timedelta(days=1),
                "assignee": "Mel",
                "status": "active",
                "outcome": None,
                "notes": "Confirm FDA breakthrough device designation and understand regulatory timeline for market approval.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=2),
                "created_by": "Nick",
                "completed_at": None
            },
            {
                "id": "task_010",
                "company_id": company_id,
                "text": "Reference check with founder's previous startup investors",
                "due_date": date.today() + timedelta(days=3),
                "assignee": "Nick",
                "status": "active",
                "outcome": None,
                "notes": "Dr. Thompson has previous healthcare startup experience. Check references from prior investors.",
                "created_at": datetime.now(timezone.utc) - timedelta(hours=6),
                "created_by": "Marina",
                "completed_at": None
            },
            {
                "id": "task_011",
                "company_id": company_id,
                "text": "Interview 3 potential physician users",
                "due_date": date.today() + timedelta(days=4),
                "assignee": "Charles",
                "status": "active",
                "outcome": None,
                "notes": "Validate product-market fit with actual physicians. Test clinical decision support accuracy.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=1),
                "created_by": "Nick",
                "completed_at": None
            },
            {
                "id": "task_012",
                "company_id": company_id,
                "text": "Assess FDA approval timeline and costs",
                "due_date": date.today() - timedelta(days=1),
                "assignee": "Marina",
                "status": "completed",
                "outcome": "FDA pathway confirmed. 12-18 month timeline with $500K-1M in regulatory costs. Breakthrough device status accelerates review process.",
                "notes": "Confirmed with regulatory consultants. Breakthrough designation provides significant advantage in approval timeline.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=3),
                "created_by": "Mel",
                "completed_at": datetime.now(timezone.utc) - timedelta(hours=2)
            }
        ]
    
    # Mock tasks for DataWeave company (68e69a2dc32b590896149741)
    elif company_id == "68e69a2dc32b590896149741":
        return [
            {
                "id": "task_013",
                "company_id": company_id,
                "text": "Technical demo review - focus on data quality metrics",
                "due_date": date.today() + timedelta(days=2),
                "assignee": "Alexey",
                "status": "active",
                "outcome": None,
                "notes": "Evaluate ML data pipeline automation and quality validation algorithms. Test with sample datasets.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=3),
                "created_by": "Nick",
                "completed_at": None
            },
            {
                "id": "task_014",
                "company_id": company_id,
                "text": "Competitive analysis vs Fivetran, Airbyte",
                "due_date": date.today() + timedelta(days=3),
                "assignee": "Marina",
                "status": "active",
                "outcome": None,
                "notes": "Compare technical differentiation in ML-specific data transformation vs general ETL tools.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=2),
                "created_by": "Nick",
                "completed_at": None
            },
            {
                "id": "task_015",
                "company_id": company_id,
                "text": "Validate customer acquisition costs with founders",
                "due_date": date.today() + timedelta(days=1),
                "assignee": "Nick",
                "status": "active",
                "outcome": None,
                "notes": "Understand go-to-market strategy and customer acquisition metrics for ML teams.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=1),
                "created_by": "Marina",
                "completed_at": None
            },
            {
                "id": "task_016",
                "company_id": company_id,
                "text": "Prepare IC memo for pipeline review",
                "due_date": date.today() - timedelta(days=1),
                "assignee": "Nick",
                "status": "completed",
                "outcome": "IC memo completed. Strong recommendation to proceed to next stage. Key strengths: clear product-market fit, strong technical team, growing market demand for ML data tools.",
                "notes": "Memo highlights 95% customer retention and 50TB+ monthly data processing as key validation metrics.",
                "created_at": datetime.now(timezone.utc) - timedelta(hours=18),
                "created_by": "Marina",
                "completed_at": datetime.now(timezone.utc) - timedelta(hours=4)
            }
        ]
    
    # Mock tasks for SynthLabs company (68e69a2dc32b590896149742)
    elif company_id == "68e69a2dc32b590896149742":
        return [
            {
                "id": "task_020",
                "company_id": company_id,
                "text": "Verify SOC 2 Type II certification and GDPR compliance",
                "due_date": date.today() + timedelta(days=4),
                "assignee": "Mel",
                "status": "active",
                "outcome": None,
                "notes": "Review privacy compliance documentation and audit reports for enterprise customers.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=2),
                "created_by": "Marina",
                "completed_at": None
            },
            {
                "id": "task_021",
                "company_id": company_id,
                "text": "Validate synthetic data quality with ML experts",
                "due_date": date.today() + timedelta(days=6),
                "assignee": "Alexey",
                "status": "active",
                "outcome": None,
                "notes": "Test synthetic data generation quality across different domains (healthcare, finance, retail).",
                "created_at": datetime.now(timezone.utc) - timedelta(hours=12),
                "created_by": "Nick",
                "completed_at": None
            },
            {
                "id": "task_022",
                "company_id": company_id,
                "text": "Interview 3 enterprise customers",
                "due_date": date.today() + timedelta(days=3),
                "assignee": "Charles",
                "status": "active",
                "outcome": None,
                "notes": "Validate customer satisfaction and use cases. Focus on regulated industries.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=1),
                "created_by": "Marina",
                "completed_at": None
            },
            {
                "id": "task_023",
                "company_id": company_id,
                "text": "Assess IP portfolio and competitive moats",
                "due_date": date.today() + timedelta(days=7),
                "assignee": "Marina",
                "status": "active",
                "outcome": None,
                "notes": "Review patents, trade secrets, and technical differentiation in synthetic data generation.",
                "created_at": datetime.now(timezone.utc) - timedelta(hours=24),
                "created_by": "Nick",
                "completed_at": None
            },
            {
                "id": "task_024",
                "company_id": company_id,
                "text": "Prepare investment committee materials",
                "due_date": date.today() - timedelta(days=1),
                "assignee": "Nick",
                "status": "completed",
                "outcome": "IC materials completed. Strong recommendation for investment. Key highlights: clear market need, strong technical team, regulatory compliance, growing enterprise adoption.",
                "notes": "Materials emphasize privacy regulation tailwinds and enterprise demand for synthetic data solutions.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=5),
                "created_by": "Marina",
                "completed_at": datetime.now(timezone.utc) - timedelta(hours=4)
            }
        ]
    
    # Mock tasks for AgentOS company (68e69a2dc32b590896149743)
    elif company_id == "68e69a2dc32b590896149743":
        return [
            {
                "id": "task_025",
                "company_id": company_id,
                "text": "Evaluate multi-agent orchestration architecture",
                "due_date": date.today() + timedelta(days=5),
                "assignee": "Alexey",
                "status": "active",
                "outcome": None,
                "notes": "Review technical architecture for managing 500+ agents. Focus on resource optimization and fault tolerance.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=3),
                "created_by": "Nick",
                "completed_at": None
            },
            {
                "id": "task_026",
                "company_id": company_id,
                "text": "Validate developer adoption metrics",
                "due_date": date.today() + timedelta(days=3),
                "assignee": "Marina",
                "status": "active",
                "outcome": None,
                "notes": "Verify 1K+ GitHub stars and developer community growth. Check open source engagement.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=2),
                "created_by": "Nick",
                "completed_at": None
            },
            {
                "id": "task_027",
                "company_id": company_id,
                "text": "Interview early enterprise customers",
                "due_date": date.today() + timedelta(days=4),
                "assignee": "Charles",
                "status": "active",
                "outcome": None,
                "notes": "Validate use cases and ROI from 25+ companies using the platform for agent deployment.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=1),
                "created_by": "Marina",
                "completed_at": None
            },
            {
                "id": "task_028",
                "company_id": company_id,
                "text": "Assess technical vision and team capability",
                "due_date": date.today() + timedelta(days=2),
                "assignee": "Alexey",
                "status": "active",
                "outcome": None,
                "notes": "Evaluate founding team's technical depth and vision for AI agent infrastructure market.",
                "created_at": datetime.now(timezone.utc) - timedelta(hours=18),
                "created_by": "Nick",
                "completed_at": None
            },
            {
                "id": "task_029",
                "company_id": company_id,
                "text": "Schedule technical deep-dive with founders",
                "due_date": date.today() - timedelta(days=2),
                "assignee": "Nick",
                "status": "completed",
                "outcome": "Technical deep-dive completed. Strong founding team with clear vision for agent infrastructure. Platform shows early traction with solid technical foundation.",
                "notes": "Founders demonstrated deep technical knowledge and clear understanding of market opportunity.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=4),
                "created_by": "Marina",
                "completed_at": datetime.now(timezone.utc) - timedelta(days=2)
            }
        ]
    
    # No additional companies - only 5 AI startups for focused demo
    # Remove the SaaS company tasks as we only need 5 companies
    
    # No tasks for other companies
    return []
