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
    """Return realistic mock tasks for AI portfolio companies demonstrating VC due diligence workflows"""
    
    # VectorAI - Enterprise vector database (Diligence stage, strong AWS partnership)
    if company_id == "68e69a2dc32b590896149739":
        return [
            {
                "id": "vectorai_001",
                "company_id": company_id,
                "text": "Verify AWS partnership and technical integration",
                "due_date": date.today() - timedelta(days=2),
                "assignee": "Nick",
                "status": "completed",
                "outcome": "AWS partnership confirmed legitimate. VectorAI has deep technical integration with AWS services. Partnership team validated their 10M+ daily query performance claims.",
                "notes": "Spoke with AWS partner team and technical architects. Partnership is strategic, not just reseller agreement.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=6),
                "created_by": "Marina",
                "completed_at": datetime.now(timezone.utc) - timedelta(days=2),
                "completed_by": "Nick"
            },
            {
                "id": "vectorai_002",
                "company_id": company_id,
                "text": "Technical architecture deep-dive with CTO",
                "due_date": date.today() - timedelta(days=1),
                "assignee": "Alexey",
                "status": "completed",
                "outcome": "Architecture review completed. Strong technical foundation with proprietary vector indexing algorithms. Can handle enterprise-scale workloads with sub-millisecond latency. Team has deep ML expertise.",
                "notes": "CTO Marcus Rodriguez has PhD from Stanford, previously at Google. Architecture is sound and scalable.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=4),
                "created_by": "Nick",
                "completed_at": datetime.now(timezone.utc) - timedelta(hours=6),
                "completed_by": "Alexey"
            },
            {
                "id": "vectorai_003",
                "company_id": company_id,
                "text": "Review Q4 revenue projections and enterprise pipeline",
                "due_date": date.today() - timedelta(days=3),  # Overdue
                "assignee": "Marina",
                "status": "active",
                "outcome": None,
                "notes": "Founder promised Q4 numbers by Monday. Critical for IC decision - need to validate $2M ARR claims and growth trajectory.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=5),
                "created_by": "Nick",
                "completed_at": None
            },
            {
                "id": "vectorai_004",
                "company_id": company_id,
                "text": "Customer reference calls with Fortune 500 users",
                "due_date": date.today(),
                "assignee": "Charles",
                "status": "active",
                "outcome": None,
                "notes": "Scheduled calls with 3 enterprise customers: Goldman Sachs, Pfizer, and Toyota. Focus on performance, support quality, and ROI.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=2),
                "created_by": "Marina",
                "completed_at": None
            },
            {
                "id": "vectorai_005",
                "company_id": company_id,
                "text": "Market analysis: Vector DB competitive landscape",
                "due_date": date.today() + timedelta(days=1),
                "assignee": "Mel",
                "status": "active",
                "outcome": None,
                "notes": "Compare vs Pinecone, Weaviate, Qdrant. Need to understand differentiation and market positioning.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=3),
                "created_by": "Alexey",
                "completed_at": None
            },
            {
                "id": "vectorai_006",
                "company_id": company_id,
                "text": "Schedule demo with potential Fortune 500 customer",
                "due_date": date.today() + timedelta(days=2),
                "assignee": "Nick",
                "status": "active",
                "outcome": None,
                "notes": "VectorAI founder will demo to our portfolio company that's evaluating vector databases. Good validation opportunity.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=1),
                "created_by": "Marina",
                "completed_at": None
            },
            {
                "id": "vectorai_007",
                "company_id": company_id,
                "text": "Legal review: IP ownership and patent landscape",
                "due_date": date.today() - timedelta(days=1),
                "assignee": "Elena",
                "status": "completed",
                "outcome": "IP review completed. VectorAI owns core vector indexing patents. No major IP conflicts identified. Strong defensive patent portfolio.",
                "notes": "Legal team confirmed clean IP ownership. Patents filed for core algorithms provide good moat.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=4),
                "created_by": "Charles",
                "completed_at": datetime.now(timezone.utc) - timedelta(hours=12),
                "completed_by": "Elena"
            },
            {
                "id": "vectorai_008",
                "company_id": company_id,
                "text": "Founder background check and references",
                "due_date": date.today() - timedelta(days=2),
                "assignee": "Marina",
                "status": "completed",
                "outcome": "Background checks completed. Dr. Sarah Patel has strong track record at Microsoft and Google. Former colleagues confirm technical leadership and execution ability. No red flags.",
                "notes": "References from Microsoft Azure team and Google Cloud were excellent. Founder is well-respected in the ML community.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=5),
                "created_by": "Nick",
                "completed_at": datetime.now(timezone.utc) - timedelta(days=2),
                "completed_by": "Marina"
            },
            {
                "id": "vectorai_009",
                "company_id": company_id,
                "text": "Financial model review and unit economics",
                "due_date": date.today() + timedelta(days=3),
                "assignee": "Alexey",
                "status": "active",
                "outcome": None,
                "notes": "Need to validate pricing model and customer acquisition costs. Enterprise deals are $50K-500K ARR range.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=2),
                "created_by": "Marina",
                "completed_at": None
            },
            {
                "id": "vectorai_010",
                "company_id": company_id,
                "text": "Prepare IC memo and investment recommendation",
                "due_date": date.today() + timedelta(days=5),
                "assignee": "Nick",
                "status": "active",
                "outcome": None,
                "notes": "Strong technical team, proven product-market fit, AWS partnership, clear path to $100M ARR. Recommend proceeding to term sheet.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=1),
                "created_by": "Marina",
                "completed_at": None
            }
        ]
    
    # CopilotMD - Healthcare AI (Seed stage, FDA pathway)
    elif company_id == "68e69a2dc32b590896149740":
        return [
            {
                "id": "copilotmd_001",
                "company_id": company_id,
                "text": "FDA regulatory pathway assessment and timeline",
                "due_date": date.today() - timedelta(days=1),
                "assignee": "Marina",
                "status": "completed",
                "outcome": "FDA pathway confirmed via breakthrough device designation. 12-18 month approval timeline with $500K-1M regulatory costs. Significant competitive advantage with fast-track status.",
                "notes": "Consulted with former FDA commissioner and regulatory consultants. Breakthrough designation is major validation.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=4),
                "created_by": "Mel",
                "completed_at": datetime.now(timezone.utc) - timedelta(hours=3),
                "completed_by": "Marina"
            },
            {
                "id": "copilotmd_002",
                "company_id": company_id,
                "text": "Medical advisor reference calls and clinical validation",
                "due_date": date.today() - timedelta(days=2),
                "assignee": "Charles",
                "status": "completed",
                "outcome": "Clinical validation completed. 94% diagnostic accuracy vs 78% baseline. Medical advisors from Johns Hopkins and Mayo Clinic confirm clinical utility. Strong physician adoption in pilot programs.",
                "notes": "Advisors are impressed with clinical outcomes. Early adoption by top-tier health systems is promising.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=5),
                "created_by": "Marina",
                "completed_at": datetime.now(timezone.utc) - timedelta(days=2),
                "completed_by": "Charles"
            },
            {
                "id": "copilotmd_003",
                "company_id": company_id,
                "text": "Healthcare compliance and HIPAA security review",
                "due_date": date.today() - timedelta(days=1),
                "assignee": "Elena",
                "status": "completed",
                "outcome": "HIPAA compliance audit completed. SOC 2 Type II certified. Security architecture reviewed and approved. No compliance concerns identified.",
                "notes": "Security team validated data protection measures. Enterprise-grade security infrastructure in place.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=3),
                "created_by": "Charles",
                "completed_at": datetime.now(timezone.utc) - timedelta(hours=8),
                "completed_by": "Elena"
            },
            {
                "id": "copilotmd_004",
                "company_id": company_id,
                "text": "Health system pilot program evaluation",
                "due_date": date.today(),
                "assignee": "Nick",
                "status": "active",
                "outcome": None,
                "notes": "5 major health systems in pilot programs. Need to validate expansion plans and conversion rates to paid contracts.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=2),
                "created_by": "Marina",
                "completed_at": None
            },
            {
                "id": "copilotmd_005",
                "company_id": company_id,
                "text": "Connect with medical advisors for board consideration",
                "due_date": date.today() + timedelta(days=1),
                "assignee": "Charles",
                "status": "active",
                "outcome": None,
                "notes": "Dr. Michael Thompson (founder) has strong medical network. Need to identify potential board members with healthcare expertise.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=3),
                "created_by": "Nick",
                "completed_at": None
            },
            {
                "id": "copilotmd_006",
                "company_id": company_id,
                "text": "Competitive analysis: Epic, Cerner integration challenges",
                "due_date": date.today() + timedelta(days=2),
                "assignee": "Mel",
                "status": "active",
                "outcome": None,
                "notes": "Need to understand EHR integration complexity and competitive positioning vs existing clinical decision support tools.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=2),
                "created_by": "Alexey",
                "completed_at": None
            },
            {
                "id": "copilotmd_007",
                "company_id": company_id,
                "text": "Review updated financial model and unit economics",
                "due_date": date.today() + timedelta(days=3),
                "assignee": "Alexey",
                "status": "active",
                "outcome": None,
                "notes": "Healthcare sales cycles are long (12-18 months). Need to validate pricing model and customer acquisition costs.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=1),
                "created_by": "Marina",
                "completed_at": None
            },
            {
                "id": "copilotmd_008",
                "company_id": company_id,
                "text": "Founder technical deep-dive and AI model review",
                "due_date": date.today() - timedelta(days=2),
                "assignee": "Alexey",
                "status": "completed",
                "outcome": "Technical review completed. AI model trained on 2M+ clinical cases with 94% accuracy. Strong ML team with medical and technical expertise. Model interpretability is excellent.",
                "notes": "Dr. Lisa Park (CTO) has impressive ML background. Model architecture is sound and clinically validated.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=4),
                "created_by": "Nick",
                "completed_at": datetime.now(timezone.utc) - timedelta(days=2),
                "completed_by": "Alexey"
            },
            {
                "id": "copilotmd_009",
                "company_id": company_id,
                "text": "Prepare IC memo for healthcare AI investment",
                "due_date": date.today() + timedelta(days=4),
                "assignee": "Nick",
                "status": "active",
                "outcome": None,
                "notes": "Strong regulatory pathway, clinical validation, and healthcare expertise. Recommend proceeding with seed investment.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=1),
                "created_by": "Marina",
                "completed_at": None
            }
        ]
    
    # DataWeave - ML data pipeline (Pre-seed, strong product-market fit)
    elif company_id == "68e69a2dc32b590896149741":
        return [
            {
                "id": "dataweave_001",
                "company_id": company_id,
                "text": "Initial screening call with CEO David Kim",
                "due_date": date.today() - timedelta(days=5),
                "assignee": "Nick",
                "status": "completed",
                "outcome": "Strong initial call. David has clear vision for solving ML data quality problems. 200+ ML teams using platform with 95% retention rate. Clear product-market fit demonstrated.",
                "notes": "CEO is technical founder with strong product sense. Problem is real and painful for ML teams.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=7),
                "created_by": "Marina",
                "completed_at": datetime.now(timezone.utc) - timedelta(days=5),
                "completed_by": "Nick"
            },
            {
                "id": "dataweave_002",
                "company_id": company_id,
                "text": "Technical architecture review and scalability assessment",
                "due_date": date.today() - timedelta(days=3),
                "assignee": "Alexey",
                "status": "completed",
                "outcome": "Architecture review completed. Platform handles 50TB+ monthly data processing with 80% reduction in prep time. Scalable microservices architecture with strong data pipeline optimization.",
                "notes": "CTO Dr. Sarah Patel has impressive background at Palantir. Architecture is enterprise-ready and scalable.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=6),
                "created_by": "Nick",
                "completed_at": datetime.now(timezone.utc) - timedelta(days=3),
                "completed_by": "Alexey"
            },
            {
                "id": "dataweave_003",
                "company_id": company_id,
                "text": "Customer reference calls with ML teams",
                "due_date": date.today() - timedelta(days=2),
                "assignee": "Charles",
                "status": "completed",
                "outcome": "Customer references excellent. 95% retention rate validated. Customers report 80% time savings on data prep. Strong NPS scores and expansion revenue from existing customers.",
                "notes": "Spoke with ML teams at Uber, Airbnb, and Stripe. All confirmed significant productivity improvements.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=4),
                "created_by": "Marina",
                "completed_at": datetime.now(timezone.utc) - timedelta(days=2),
                "completed_by": "Charles"
            },
            {
                "id": "dataweave_004",
                "company_id": company_id,
                "text": "Market size analysis and competitive positioning",
                "due_date": date.today() - timedelta(days=1),
                "assignee": "Mel",
                "status": "completed",
                "outcome": "Market analysis completed. $8.2B data preparation market growing 20% annually. Clear differentiation vs traditional ETL tools. Positioned as ML-native data platform with strong competitive moat.",
                "notes": "Traditional ETL tools (Informatica, Talend) don't understand ML workflows. DataWeave has first-mover advantage.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=3),
                "created_by": "Alexey",
                "completed_at": datetime.now(timezone.utc) - timedelta(hours=4),
                "completed_by": "Mel"
            },
            {
                "id": "dataweave_005",
                "company_id": company_id,
                "text": "Schedule follow-up call with founders",
                "due_date": date.today() + timedelta(days=1),
                "assignee": "Nick",
                "status": "active",
                "outcome": None,
                "notes": "Need to discuss funding round details, use of proceeds, and board composition. Strong candidate for pre-seed investment.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=1),
                "created_by": "Marina",
                "completed_at": None
            },
            {
                "id": "dataweave_006",
                "company_id": company_id,
                "text": "Review financial model and unit economics",
                "due_date": date.today() + timedelta(days=2),
                "assignee": "Alexey",
                "status": "active",
                "outcome": None,
                "notes": "Need to validate pricing model. Enterprise deals range from $25K-200K ARR. Strong expansion revenue from existing customers.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=2),
                "created_by": "Marina",
                "completed_at": None
            },
            {
                "id": "dataweave_007",
                "company_id": company_id,
                "text": "Check references from previous investors",
                "due_date": date.today() + timedelta(days=1),
                "assignee": "Marina",
                "status": "active",
                "outcome": None,
                "notes": "Need to speak with seed investors and understand their perspective on the team and market opportunity.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=2),
                "created_by": "Nick",
                "completed_at": None
            },
            {
                "id": "dataweave_008",
                "company_id": company_id,
                "text": "Prepare IC memo for pipeline review",
                "due_date": date.today() - timedelta(hours=4),
                "assignee": "Nick",
                "status": "completed",
                "outcome": "IC memo completed. Strong recommendation to proceed to next stage. Key strengths: clear product-market fit, strong technical team, growing market demand for ML data tools, excellent customer retention.",
                "notes": "Memo highlights 95% customer retention and 50TB+ monthly data processing as key validation metrics.",
                "created_at": datetime.now(timezone.utc) - timedelta(hours=18),
                "created_by": "Marina",
                "completed_at": datetime.now(timezone.utc) - timedelta(hours=4),
                "completed_by": "Nick"
            },
            {
                "id": "dataweave_009",
                "company_id": company_id,
                "text": "Legal review: IP ownership and data privacy",
                "due_date": date.today() + timedelta(days=3),
                "assignee": "Elena",
                "status": "active",
                "outcome": None,
                "notes": "Need to review data processing IP and ensure compliance with data privacy regulations (GDPR, CCPA).",
                "created_at": datetime.now(timezone.utc) - timedelta(days=1),
                "created_by": "Charles",
                "completed_at": None
            },
            {
                "id": "dataweave_010",
                "company_id": company_id,
                "text": "Competitive analysis: vs traditional ETL and ML platforms",
                "due_date": date.today() + timedelta(days=4),
                "assignee": "Mel",
                "status": "active",
                "outcome": None,
                "notes": "Compare vs Informatica, Talend, Databricks, Snowflake. Need to understand competitive positioning and differentiation.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=2),
                "created_by": "Alexey",
                "completed_at": None
            },
            {
                "id": "dataweave_011",
                "company_id": company_id,
                "text": "Review legal documents and term sheet preparation",
                "due_date": date.today() + timedelta(days=5),
                "assignee": "Elena",
                "status": "active",
                "outcome": None,
                "notes": "Prepare term sheet for pre-seed investment. Strong candidate with clear product-market fit and technical team.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=1),
                "created_by": "Nick",
                "completed_at": None
            }
        ]
    
    # SynthLabs - Synthetic data generation (Seed stage, privacy compliance)
    elif company_id == "68e69a2dc32b590896149742":
        return [
            {
                "id": "synthlabs_001",
                "company_id": company_id,
                "text": "Privacy compliance and regulatory review",
                "due_date": date.today() - timedelta(days=2),
                "assignee": "Elena",
                "status": "completed",
                "outcome": "Compliance review completed. SOC 2 Type II certified, GDPR compliant. Privacy guarantees validated by independent auditors. Strong regulatory positioning for synthetic data market.",
                "notes": "Privacy compliance is critical differentiator. SynthLabs has best-in-class privacy guarantees and audit trail.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=4),
                "created_by": "Charles",
                "completed_at": datetime.now(timezone.utc) - timedelta(days=2),
                "completed_by": "Elena"
            },
            {
                "id": "synthlabs_002",
                "company_id": company_id,
                "text": "Technical deep-dive: synthetic data generation algorithms",
                "due_date": date.today() - timedelta(days=1),
                "assignee": "Alexey",
                "status": "completed",
                "outcome": "Technical review completed. Advanced generative models with statistical fidelity validation. 100M+ synthetic records generated monthly with privacy guarantees. Strong ML team with privacy expertise.",
                "notes": "CTO Alex Kumar has PhD in privacy-preserving ML. Algorithms are sophisticated and clinically validated.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=3),
                "created_by": "Nick",
                "completed_at": datetime.now(timezone.utc) - timedelta(hours=6),
                "completed_by": "Alexey"
            },
            {
                "id": "synthlabs_003",
                "company_id": company_id,
                "text": "Enterprise customer validation and expansion plans",
                "due_date": date.today() - timedelta(days=1),
                "assignee": "Charles",
                "status": "completed",
                "outcome": "Customer validation completed. 50+ enterprise customers across healthcare, finance, and retail. Strong expansion revenue and multi-year contracts. Enterprise adoption accelerating due to privacy regulations.",
                "notes": "Privacy regulations (GDPR, CCPA, HIPAA) are driving enterprise demand. SynthLabs is well-positioned for this trend.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=4),
                "created_by": "Marina",
                "completed_at": datetime.now(timezone.utc) - timedelta(hours=8),
                "completed_by": "Charles"
            },
            {
                "id": "synthlabs_004",
                "company_id": company_id,
                "text": "Market analysis: privacy regulation tailwinds",
                "due_date": date.today(),
                "assignee": "Mel",
                "status": "active",
                "outcome": None,
                "notes": "Need to quantify impact of new privacy regulations on synthetic data market. $2.1B market growing 35% annually.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=2),
                "created_by": "Alexey",
                "completed_at": None
            },
            {
                "id": "synthlabs_005",
                "company_id": company_id,
                "text": "Connect with privacy experts and advisors",
                "due_date": date.today() + timedelta(days=1),
                "assignee": "Charles",
                "status": "active",
                "outcome": None,
                "notes": "Need to build advisory board with privacy and regulatory expertise. Maria Santos (VP Privacy Engineering) has strong network.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=3),
                "created_by": "Nick",
                "completed_at": None
            },
            {
                "id": "synthlabs_006",
                "company_id": company_id,
                "text": "Financial model review and unit economics",
                "due_date": date.today() + timedelta(days=2),
                "assignee": "Alexey",
                "status": "active",
                "outcome": None,
                "notes": "Enterprise deals range from $100K-1M ARR. Strong expansion revenue from existing customers. Need to validate growth assumptions.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=1),
                "created_by": "Marina",
                "completed_at": None
            },
            {
                "id": "synthlabs_007",
                "company_id": company_id,
                "text": "Competitive analysis: synthetic data landscape",
                "due_date": date.today() + timedelta(days=3),
                "assignee": "Mel",
                "status": "active",
                "outcome": None,
                "notes": "Compare vs Gretel, Mostly AI, Hazy. Need to understand competitive positioning and differentiation in privacy guarantees.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=2),
                "created_by": "Alexey",
                "completed_at": None
            },
            {
                "id": "synthlabs_008",
                "company_id": company_id,
                "text": "Prepare investment committee materials",
                "due_date": date.today() - timedelta(hours=4),
                "assignee": "Nick",
                "status": "completed",
                "outcome": "IC materials completed. Strong recommendation for investment. Key highlights: clear market need, strong technical team, regulatory compliance, growing enterprise adoption, privacy regulation tailwinds.",
                "notes": "Materials emphasize privacy regulation tailwinds and enterprise demand for synthetic data solutions.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=5),
                "created_by": "Marina",
                "completed_at": datetime.now(timezone.utc) - timedelta(hours=4),
                "completed_by": "Nick"
            },
            {
                "id": "synthlabs_009",
                "company_id": company_id,
                "text": "Founder background check and references",
                "due_date": date.today() + timedelta(days=1),
                "assignee": "Marina",
                "status": "active",
                "outcome": None,
                "notes": "Dr. Rachel Chen (CEO) has strong academic background in privacy-preserving ML. Need to validate execution track record.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=2),
                "created_by": "Nick",
                "completed_at": None
            },
            {
                "id": "synthlabs_010",
                "company_id": company_id,
                "text": "Schedule demo with portfolio company evaluating synthetic data",
                "due_date": date.today() + timedelta(days=4),
                "assignee": "Nick",
                "status": "active",
                "outcome": None,
                "notes": "Our portfolio company in healthcare is evaluating synthetic data solutions. Good validation opportunity for SynthLabs platform.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=1),
                "created_by": "Marina",
                "completed_at": None
            }
        ]
    
    # AgentOS - AI agent infrastructure (Pre-seed, early traction)
    elif company_id == "68e69a2dc32b590896149743":
        return [
            {
                "id": "agentos_001",
                "company_id": company_id,
                "text": "Initial screening call with CEO Jordan Lee",
                "due_date": date.today() - timedelta(days=4),
                "assignee": "Nick",
                "status": "completed",
                "outcome": "Strong initial call. Jordan has clear vision for AI agent infrastructure. 25+ companies using platform with 500+ active agents managed. Early traction in emerging agent economy.",
                "notes": "CEO is technical founder with strong product sense. Problem is becoming critical as AI agents scale.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=6),
                "created_by": "Marina",
                "completed_at": datetime.now(timezone.utc) - timedelta(days=4),
                "completed_by": "Nick"
            },
            {
                "id": "agentos_002",
                "company_id": company_id,
                "text": "Technical deep-dive with founders",
                "due_date": date.today() - timedelta(days=2),
                "assignee": "Nick",
                "status": "completed",
                "outcome": "Technical deep-dive completed. Strong founding team with clear vision for agent infrastructure. Platform shows early traction with solid technical foundation. 90% reduction in agent deployment complexity validated.",
                "notes": "Founders demonstrated deep technical knowledge and clear understanding of market opportunity.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=4),
                "created_by": "Marina",
                "completed_at": datetime.now(timezone.utc) - timedelta(days=2),
                "completed_by": "Nick"
            },
            {
                "id": "agentos_003",
                "company_id": company_id,
                "text": "Market analysis: AI agent economy and infrastructure needs",
                "due_date": date.today() - timedelta(days=1),
                "assignee": "Mel",
                "status": "completed",
                "outcome": "Market analysis completed. AI agent market projected to reach $12.8B by 2028, growing 40% annually. Clear infrastructure gap for agent deployment and management at scale. Early-mover advantage in emerging market.",
                "notes": "Agent economy is emerging rapidly. Infrastructure layer is critical bottleneck for enterprise adoption.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=3),
                "created_by": "Nick",
                "completed_at": datetime.now(timezone.utc) - timedelta(hours=6),
                "completed_by": "Mel"
            },
            {
                "id": "agentos_004",
                "company_id": company_id,
                "text": "Customer validation with early adopters",
                "due_date": date.today(),
                "assignee": "Charles",
                "status": "active",
                "outcome": None,
                "notes": "Need to speak with 3-4 early customers to validate platform value and deployment experience.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=2),
                "created_by": "Marina",
                "completed_at": None
            },
            {
                "id": "agentos_005",
                "company_id": company_id,
                "text": "Technical architecture review and scalability",
                "due_date": date.today() + timedelta(days=1),
                "assignee": "Alexey",
                "status": "active",
                "outcome": None,
                "notes": "Need to review architecture for handling 500+ agents across 25+ companies. Focus on multi-agent orchestration and resource optimization.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=3),
                "created_by": "Nick",
                "completed_at": None
            },
            {
                "id": "agentos_006",
                "company_id": company_id,
                "text": "Open source community engagement assessment",
                "due_date": date.today() + timedelta(days=2),
                "assignee": "Mel",
                "status": "active",
                "outcome": None,
                "notes": "1K+ GitHub stars and active developer community. Need to understand community engagement and developer adoption trends.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=1),
                "created_by": "Alexey",
                "completed_at": None
            },
            {
                "id": "agentos_007",
                "company_id": company_id,
                "text": "Competitive analysis: agent infrastructure landscape",
                "due_date": date.today() + timedelta(days=3),
                "assignee": "Mel",
                "status": "active",
                "outcome": None,
                "notes": "Compare vs LangChain, AutoGPT, CrewAI. Need to understand competitive positioning and differentiation.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=2),
                "created_by": "Nick",
                "completed_at": None
            },
            {
                "id": "agentos_008",
                "company_id": company_id,
                "text": "Founder background check and references",
                "due_date": date.today() + timedelta(days=1),
                "assignee": "Marina",
                "status": "active",
                "outcome": None,
                "notes": "Jordan Lee and Dr. Priya Sharma have strong technical backgrounds. Need to validate execution track record and team dynamics.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=2),
                "created_by": "Nick",
                "completed_at": None
            },
            {
                "id": "agentos_009",
                "company_id": company_id,
                "text": "Financial model and growth projections review",
                "due_date": date.today() + timedelta(days=4),
                "assignee": "Alexey",
                "status": "active",
                "outcome": None,
                "notes": "Early-stage company with 25+ customers. Need to validate pricing model and growth assumptions for agent infrastructure market.",
                "created_at": datetime.now(timezone.utc) - timedelta(days=1),
                "created_by": "Marina",
                "completed_at": None
            }
        ]
    
    # No tasks for other companies
    return []
