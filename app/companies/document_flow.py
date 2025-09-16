import os
import pathlib
import tempfile
from pathlib import Path
from typing import Dict

import httpx
import openai
from bson import ObjectId
from google.cloud import storage
from pymongo.asynchronous.database import AsyncDatabase

from app.companies.models import CompanyCreateRequest
from app.companies.pdf.downloader import URLDownloader
from app.companies.pdf.flyweight import PDFlyweight
from app.company_data.job_dispatcher import JobDispatcher
from app.foundation.primitives import datetime, json
from app.foundation.server import Logger
from app.shared.company import CompanyStatus, Company
from app.shared.url_utils import is_valid_website_url, normalize_url, extract_domain


def _unwrap_single_item(value):
    """Helper to unwrap single-item lists to their value"""
    if isinstance(value, list) and len(value) == 1:
        return value[0]
    return value


class CompanyFromDocsFlow:
    """Flow for creating companies from PDF documents"""

    PDF_BUCKET_NAME = "dvc-pdfs"
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

    def __init__(
            self,
            database: AsyncDatabase,
            storage_client: storage.Client,
            openai_client: openai.AsyncOpenAI,
            http_client: httpx.AsyncClient,
            job_dispatcher: JobDispatcher,
            logger: Logger
    ):
        self.database = database
        self.storage_client = storage_client
        self.openai_client = openai_client
        self.http_client = http_client
        self.job_dispatcher = job_dispatcher
        self.logger = logger

    async def __call__(self, request: CompanyCreateRequest) -> str:
        """Process documents and create company"""
        log_labels = {
            "company": {
                "id": request.id,
                "name": request.name,
                'website': request.website
            }
        }
        self.logger.info("Processing company from documents", labels=log_labels)

        try:
            # Fetch and store PDF
            pdf_bytes, gcs_path = await self._fetch_and_store_pdf(request.id, request.sources)

            # Extract text from PDF and upload to bucket
            extracted_text = await self._extract_and_upload_text_from_pdf(request.id, pdf_bytes)
            self.logger.info("Extracted text from PDF", labels=log_labels | {"textLength": len(extracted_text)})

            # Extract structured data and upload to bucket
            extracted_data = await self._extract_and_upload_data_from_pitch_text(request.id, extracted_text)

            # Store extracted data to company record
            key_fields, data = self._flatten_extracted_data(extracted_data)
            public_url = f"https://api.dvcagent.com/media/{gcs_path}"

            company = await self._update_company(request, key_fields, data, public_url)

            # Trigger data source updates if company has valid website
            if company.has_valid_website():
                await self._trigger_data_source_updates(company)

        except Exception as e:
            await self._update_company_error(request.id, str(e))
            self.logger.error("Company processing failed", labels=log_labels | {"error": str(e)})
            raise

        self.logger.info("Company processing completed", labels=log_labels)

        return request.id

    async def _fetch_and_store_pdf(self, company_id: str, sources: list) -> tuple[bytes, str]:
        """Fetch PDF and store it in GCS, return bytes and GCS path"""
        pdf_bytes = None

        for source in sources:
            if source.type == 'url':
                # Download from URL
                downloader = URLDownloader(source.url, self.logger)
                pdf_bytes = await downloader.process_content()
                break
            elif source.type == 'pdf':
                # Copy from temp bucket location
                bucket = self.storage_client.bucket(source.bucket)
                temp_blob = bucket.blob(source.key)
                pdf_bytes = temp_blob.download_as_bytes()
                break

        if not pdf_bytes:
            raise ValueError("No valid PDF source found")

        # Store in company folder
        final_path = f"companies/{company_id}/pitch.pdf"
        bucket = self.storage_client.bucket(self.PDF_BUCKET_NAME)
        final_blob = bucket.blob(final_path)
        final_blob.upload_from_string(pdf_bytes, content_type="application/pdf")

        return pdf_bytes, final_path

    async def _extract_and_upload_data_from_pitch_text(self, company_id: str, text: str) -> Dict:
        """Extract structured data from pitch text and upload to bucket"""
        url = "https://api.dvcagent.com/dealflow/run/main"
        data = {
            "graph": "Subgraphs #0 Main Graph",
            "openAiKey": self.OPENAI_API_KEY,
            "inputs": {
                "input_pitch_deck": text,
            },
        }
        headers = {
            "Content-Type": "application/json",
            "Deal": str(company_id),
        }
        result = await self.http_client.post(url, headers=headers, json=data)
        result.raise_for_status()
        extracted_data = result.json()

        # Upload structured data to bucket
        bucket = self.storage_client.bucket(self.PDF_BUCKET_NAME)
        json_path = f"companies/{company_id}/pitch.json"
        json_blob = bucket.blob(json_path)
        json_blob.upload_from_string(json.dumps(extracted_data), content_type="application/json")

        return extracted_data

    async def _extract_and_upload_text_from_pdf(self, company_id: str, pdf_bytes: bytes) -> str:
        """Uses PDFlyweight to extract text from PDF and uploads to bucket"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save PDF to temp file
            temp_pdf_path = Path(temp_dir) / "document.pdf"
            temp_pdf_path.write_bytes(pdf_bytes)

            # Initialize PDFlyweight with working directory
            work_dir = Path(temp_dir) / "work"
            pdf_processor = PDFlyweight(work_dir, self.openai_client, self.logger)

            # Convert PDF to pages and extract text
            pdf_processor.to_pages(str(temp_pdf_path))
            extracted_text = await pdf_processor.to_text()

            # Upload extracted text to bucket
            bucket = self.storage_client.bucket(self.PDF_BUCKET_NAME)
            text_path = f"companies/{company_id}/pitch.txt"
            text_blob = bucket.blob(text_path)
            text_blob.upload_from_string(extracted_text, content_type="text/plain")

            return extracted_text

    def _flatten_extracted_data(self, extracted_data: Dict) -> tuple[Dict, Dict]:
        """Flatten extracted data for MongoDB storage following existing schema"""
        output = extracted_data.get('output', {}).get('value', {})
        structured = output.get('structured', {})
        unstructured = output.get('unstructured', {})

        # Extract key terms
        key_terms = structured.get('key_terms', {})
        company_info = key_terms.get('company_info', {})
        fundraising = key_terms.get('fundrasing_summary', {})

        # Extract indicators (also contains some fields)
        indicators = output.get('indicators', {})

        # Extract founders info
        founders_data = structured.get('founders_info', {})

        # Main company fields (not in ourData)
        main_fields = {
            'name': company_info.get('Company Name', {}).get('value'),
            'website': company_info.get('Company Site', {}).get('value'),
            'email': company_info.get('Company Email', {}).get('value'),
            'blurb': unstructured.get('key_facts', {}).get('Product Solution', {}).get('value'),  # Solution Statement -> blurb
        }

        # ourData fields matching existing schema
        our_data_fields = {
            'summary': unstructured.get('executive_summary'),  # executive_summary -> summary
            'businessModelType': _unwrap_single_item(indicators.get('Business Model', {}).get('value')),  # Single value expected
            'problem': unstructured.get('key_facts', {}).get('Problem', {}).get('value'),
            'traction': unstructured.get('key_facts', {}).get('Traction', {}).get('value'),
            'marketSize': unstructured.get('key_facts', {}).get('Market', {}).get('value'),
            'founders': founders_data,
            'companyHQ': company_info.get('Headquarter Location', {}).get('value'),
            'foundationYear': company_info.get('Year of Foundation', {}).get('value'),
            'employeeCount': company_info.get('Quantity of Employee', {}).get('value'),

            # Additional ourData fields from dvc_mapping.yml - using correct JSON paths
            'category': _unwrap_single_item(indicators.get('Product Type', {}).get('value')),  # Single value expected
            'mainIndustry': _unwrap_single_item(key_terms.get('not_validated_flags', {}).get('Industry', {}).get('value')),  # Single value expected
            'productStructureType': _unwrap_single_item(indicators.get('Product Structure Type', {}).get('value')),  # Single value expected
            'targetMarket': key_terms.get('not_validated_flags', {}).get('Target market', {}).get('value'),  # Target market -> targetMarket
            'revenueModelType': _unwrap_single_item(indicators.get('Revenue Model Type', {}).get('value')),  # Single value expected
            'distributionModelType': _unwrap_single_item(indicators.get('Distribution Strategy', {}).get('value')),  # Single value expected

            # Fundraising fields
            'targetAmount': _unwrap_single_item(fundraising.get('Target Amount', {}).get('value')),  # Single value expected
            'dealSize': _unwrap_single_item(fundraising.get('Deal Size', {}).get('value')),  # Single value expected
            'raisedAmount': _unwrap_single_item(fundraising.get('Raised Amount', {}).get('value')),  # Single value expected
            'coinvestorsList': fundraising.get('CoInvestors List', {}).get('value'),  # Keep as list

            # Additional extracted fields
            'competitors': unstructured.get('key_facts', {}).get('Competitors', {}).get('value'),
        }

        return (
            {k: v for k, v in main_fields.items() if v is not None},
            {k: v for k, v in our_data_fields.items() if v is not None}
        )

    async def _update_company(self, request: CompanyCreateRequest, key_fields: Dict, data: Dict, public_url: str) -> Company:
        """Update company in MongoDB with extracted data and processing status"""
        update_fields = {}

        if not request.name:
            update_fields['name'] = key_fields.get('name')

        if not request.website:
            extracted_website = key_fields.get('website')
            if extracted_website and is_valid_website_url(extracted_website):
                normalized_website = normalize_url(extracted_website.strip())
                domain = extract_domain(extracted_website.strip())
                update_fields['website'] = normalized_website
                update_fields['domain'] = domain

        if not request.email:
            update_fields['email'] = key_fields.get('email')

        update_fields['blurb'] = key_fields.get('blurb')
        update_fields['ourData'] = data
        update_fields['ourData']['linkToDeck'] = public_url

        # Add processing status and timestamps
        update_fields['status'] = CompanyStatus.NEW_COMPANY
        update_fields['updatedAt'] = datetime.now()

        result = await self.database["companies"].find_one_and_update(
            {"_id": ObjectId(request.id)},
            {
                "$set": update_fields,
                "$unset": {"lastError": ""}
            },
            return_document=True
        )
        return Company.model_validate(result)

    async def _trigger_data_source_updates(self, company: Company):
        """Trigger job dispatcher updates for all supported data sources"""
        supported_sources = ["linkedin", "spectr", "googleplay", "appstore", "google_jobs"]

        for source in supported_sources:
            await self.job_dispatcher.trigger_one(company, source)

    async def _update_company_error(self, company_id: str, error_msg: str):
        """Update company with processing error"""
        await self.database["companies"].update_one(
            {"_id": ObjectId(company_id)},
            {"$set": {"lastError": error_msg}}
        )
