import json
from typing import Dict
from urllib.parse import urlparse

from bson import ObjectId
from google import genai
from google.genai import types as genai_types
from pymongo.asynchronous.database import AsyncDatabase

from app.foundation import as_async
from app.foundation.primitives import datetime
from app.foundation.server import Logger
from app.shared import Company, SerpApiClient
from .data_syncer import DataFetcher, FetchResult, DataSyncer

__all__ = ["GoogleJobsDataSyncer", "GoogleJobsFetcher"]

STOP_WORDS = {'company', 'the', 'llc', 'inc', 'ai', 'health', 'to', 'go', 'com', 'a', 'n', 'in', 'tech', 'of', 'and', '&'}

JOB_VALIDATION_PROMPT = """
You are analyzing whether a job posting matches a specific company based on the job description and company information.

Company Name: {company_name}
Company Description: {company_blurb}
Job Company Name: {job_company_name}
Job Description: {job_description}

Task: Determine if this job posting is actually for the target company ({company_name}) or if it's for a different company with a similar name.

Consider:
- Does the job description align with the company's business/industry?
- Are there conflicting details that suggest this is a different company?
- Does the job company name match or could be a reasonable variation?

Response format: {{"is_match": boolean}}
"""

class GoogleJobsDataSyncer(DataSyncer):
    async def store_db_data(self, company: Company, result: FetchResult):
        update_result = await self._companies_collection.update_one(
            {
                '_id': ObjectId(company.id)
            },
            {
                "$set": {
                    "googleJobsUpdatedAt": result.updated_at,
                }
            },
        )
        googleJobsData = result.db_update_fields.get("googleJobsData") or []
        jobs_collection = self._database["jobs"]
        for job in googleJobsData:
            result = await jobs_collection.update_one(
                filter={
                    'companyId': company.id,
                    'title': job.get('title'),
                    'location': job.get('location')
                },
                update={
                    '$set': {
                        'updatedAt': datetime.now(),
                        'applyOptions': job.get('apply_options'),
                        'companyId': company.id,
                        'companyName': company.name,
                        'description': job.get('description'),
                        'extensions': job.get('extensions'),
                        'jobHighlights': job.get('job_highlights'),
                        'location': job.get('location'),
                        'title': job.get('title'),
                        'via': job.get('via'),
                    },
                    '$setOnInsert': {
                        'createdAt': datetime.now(),
                    }
                },
                upsert=True,
            )


class GoogleJobsFetcher(DataFetcher):
    def __init__(
            self,
            database: AsyncDatabase,
            serpapi_client: SerpApiClient,
            logger: Logger,
            genai_client: genai.Client = None
    ):
        self._database = database
        self._companies_collection = database["companies"]
        self._serpapi_client = serpapi_client
        self._logger = logger
        self._genai_client: genai.Client = genai_client

    def source_id(self) -> str:
        return "google-jobs"

    def should_update(self, company: Company):
        return company.googleJobsUpdatedAt is None or (
            company.googleJobsUpdatedAt < datetime.now() - datetime.timedelta(days=3)
        )

    async def is_description_matches(self, company: Company, job: Dict) -> bool:
        company_blurb = company.blurb
        job_description = job.get('description', '')
        job_company_name = job.get('company_name', '')
        
        if not job_description.strip():
            return False
            
        prompt = JOB_VALIDATION_PROMPT.format(
            company_name=company.name,
            company_blurb=company_blurb,
            job_company_name=job_company_name,
            job_description=job_description
        )
        response_schema = {
            "type": "OBJECT",
            "properties": {
                "is_match": {"type": "BOOLEAN", "nullable": False},
            },
            "required": ["is_match"],
        }

        response = await as_async(self._genai_client.models.generate_content,
            model="gemini-2.5-flash",
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
            )
        )

        parsed = json.loads(response.text)
        return parsed.get('is_match', False)

    async def fetch_company_data(self, company: Company) -> FetchResult:
        website = f"https://{company.website}" if not company.website.startswith('http') else company.website
        domain = urlparse(website).netloc.replace('www.', '') if website else None
        raw_data = await self._serpapi_client.search_google_jobs(domain)
        search_metadata = raw_data.get('search_metadata') or {}
        jobs_results = raw_data.get('jobs_results') or []

        company_name_set = set(company.name.lower().replace('.', ' ').replace(',', ' ').split()) - STOP_WORDS
        
        async def _is_job_valid(job: Dict):
            job_company_name_set = set(job.get('company_name', '').lower().replace('.', ' ').replace(',', ' ').split()) - STOP_WORDS
            basic_name_match = len(company_name_set.intersection(job_company_name_set)) > 0
            
            if not basic_name_match:
                self._logger.info(
                    "Job does not contain company name",
                    labels={
                        "company": company.model_dump_for_logs(),
                        "job": {k: v for k,v in job.items() if k in {'title', 'location', 'company_name'}}
                    }
                )
                return False
            if not company.blurb:
                self._logger.info(
                    "Job filtered since company has no blurb",
                    labels={
                        "company": company.model_dump_for_logs(),
                    }
                )
                return False
            llm_validation = await self.is_description_matches(company, job)
            if not llm_validation:
                self._logger.info(
                    "Job filtered by LLM validation",
                    labels={
                        "company": company.model_dump_for_logs(),
                        "job": {k: v for k,v in job.items() if k in {'title', 'location', 'company_name'}}
                    }
                )
                return False
                
            return True
            
        filtered_jobs = []
        for job in jobs_results:
            if await _is_job_valid(job):
                filtered_jobs.append(job)
        jobs_results = filtered_jobs

        return FetchResult(
            raw_data=raw_data,
            remote_id=None,
            db_update_fields={
                "googleJobsData": jobs_results,
                "googleJobsUpdatedAt": datetime.now()
            } if jobs_results else {},
            updated_at=datetime.now()
        )
