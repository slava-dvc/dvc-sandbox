# Company Data Pipeline Module

## Overview
The company_data module implements a scalable data fetching pipeline that aggregates company information from multiple external sources (LinkedIn, Google Play, Spectr, AirTable) using async processing patterns with Pub/Sub queues.

## Module Structure
```
app/company_data/
├── __init__.py                 # Module exports router
├── routes.py                   # FastAPI endpoints (/v1/company_data/*)
├── data_syncer.py             # Data orchestration and storage
├── job_dispatcher.py          # Pub/Sub job dispatching  
├── linkedin_fetcher.py        # LinkedIn data source
└── googleplay_fetcher.py      # Google Play data source
```

## Data Sources & Fetchers

Plugin Architecture Pattern:
- All fetchers implement DataFetcher abstract base class
- Required methods: source_id(), fetch_company_data()
- Optional: should_update() for refresh logic

Available Sources:
- LinkedIn: Uses ScrapinClient, 1-day refresh interval
- Google Play: Uses SerpApiClient, 7-day refresh interval  
- Spectr: Company enrichment via SpectrClient
- AirTable: Company database sync

## API Endpoints Pattern

Base Route: /v1/company_data

Endpoints:
```python
POST /pull                    # Bulk async processing
POST /pull/linkedin          # Direct LinkedIn sync  
POST /pull/googleplay        # Direct Google Play sync
```

Request/Response Pattern:
- Bulk endpoint accepts SyncRequest with sources and max_items
- Returns HTTP 202 (Accepted) for async processing
- Direct endpoints accept Company model payload

## Data Model Schema

Company Model (app/shared/company.py):
```python
class Company(BaseModel):
    # Core identity
    id: str
    airtableId: str  
    name: str
    website: str
    
    # LinkedIn integration
    linkedInId: str | None
    linkedInData: dict | None
    linkedInUpdatedAt: datetime | None
    
    # Google Play integration  
    googlePlayId: str | None
    googlePlayData: dict | None
    googlePlayUpdatedAt: datetime | None
    
    # Spectr integration
    spectrId: str | None
    spectrData: dict | None
    spectrUpdatedAt: datetime | None
```

## Deployment & Infrastructure

Pub/Sub Queue Architecture:
- Topics defined in infrastructure/queues/company_data.py:
  - company-data-pull-linkedin
  - company-data-pull-googleplay 
  - company-data-pull-spectr
  - company-data-pull-airtable

Scheduled Jobs (infrastructure/services/integrations.py):
```python
# Weekly LinkedIn data pull
company_data_pull_linkedin = make_scheduled_job(
    "company-data-pull-linkedin",
    "Pull Company Data (LinkedIn)", 
    "12 11 * * 7",  # Weekly Sunday 11:12
    f"{CLOUD_RUN_URI}/v1/company_data/pull",
    {"sources": ["linkedin"], "max_items": 50000}
)

# Weekly Google Play data pull  
company_data_pull_googleplay = make_scheduled_job(
    "company-data-pull-googleplay",
    "Pull Company Data (Google Play)",
    "45 14 * * 7",  # Weekly Sunday 14:45
    f"{CLOUD_RUN_URI}/v1/company_data/pull", 
    {"sources": ["googleplay"], "max_items": 50000}
)
```

Push Subscriptions:
```python
# LinkedIn topic -> /v1/company_data/pull/linkedin
create_subscription_with_push_and_dlq(
    company_data.linkedin_topic_name,
    "consume",
    f"{CLOUD_RUN_URI}/v1/company_data/pull/linkedin"
)

# Google Play topic -> /v1/company_data/pull/googleplay  
create_subscription_with_push_and_dlq(
    company_data.googleplay_topic_name,
    "consume", 
    f"{CLOUD_RUN_URI}/v1/company_data/pull/googleplay"
)
```

## Data Processing Flow

1. Scheduled Trigger: Cloud Scheduler hits bulk /pull endpoint
2. Job Dispatch: JobDispatcher queries MongoDB for companies
3. Message Publishing: Individual Company payloads sent to Pub/Sub topics
4. Async Processing: Cloud Run consumes messages via push subscriptions
5. Data Fetching: DataFetcher implementations call external APIs
6. Storage: DataSyncer updates MongoDB + archives raw data to GCS

## Storage Pattern

Dual Storage Strategy:
- MongoDB: Structured company data with update timestamps
- Cloud Storage: Raw API responses archived as compressed JSON
  - Path: {source_id}/{website_id}/{YYYY-MM-DD}.json.gz
  - Bucket: dvc-dataset-v2

## Configuration Requirements

Environment Variables:
```bash
SCRAPIN_API_KEY=xxx        # LinkedIn data access
SERPAPI_API_KEY=xxx        # Google Play search  
SPECTR_API_KEY=xxx         # Company enrichment
AIRTABLE_API_KEY=xxx       # Company data source
```

## Adding New Data Sources

To add a new data source (e.g., "crunchbase"):

1. Create Fetcher: app/company_data/crunchbase_fetcher.py
   ```python
   class CrunchbaseFetcher(DataFetcher):
       def source_id(self) -> str:
           return "crunchbase"
       
       def fetch_company_data(self, company: Company) -> FetchResult:
           # Implementation
   ```

2. Add Topic: Update infrastructure/queues/company_data.py
   ```python
   crunchbase_topic_name = "company-data-pull-crunchbase"
   ```

3. Deploy Infrastructure: Add subscription in infrastructure/services/integrations.py
   ```python
   create_subscription_with_push_and_dlq(
       company_data.crunchbase_topic_name,
       "consume",
       f"{CLOUD_RUN_URI}/v1/company_data/pull/crunchbase"
   )
   ```

4. Add Route: Update app/company_data/routes.py
   ```python
   @router.post("/pull/crunchbase")
   async def pull_crunchbase_data(company: Company):
       # Implementation
   ```

5. Update Model: Add fields to Company model
   ```python
   crunchbaseId: str | None = None
   crunchbaseData: dict | None = None  
   crunchbaseUpdatedAt: datetime | None = None
   ```