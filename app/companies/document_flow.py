import tempfile
from pathlib import Path
from bson import ObjectId
from google.cloud import storage
from pymongo.asynchronous.database import AsyncDatabase
import openai

from app.foundation.server import Logger
from app.foundation.primitives import datetime
from app.shared.company import CompanyStatus
from app.companies.models import CompanyCreateRequest, DocumentSourceType
from app.companies.pdf.downloader import URLDownloader
from app.companies.pdf.flyweight import PDFlyweight


class CompanyFromDocsFlow:
    """Flow for creating companies from PDF documents"""
    
    def __init__(
            self,
            database: AsyncDatabase,
            storage_client: storage.Client,
            openai_client: openai.AsyncOpenAI,
            logger: Logger
    ):
        self.database = database
        self.storage_client = storage_client
        self.openai_client = openai_client
        self.logger = logger
    
    async def __call__(self, request: CompanyCreateRequest) -> str:
        """Process documents and create company"""
        self.logger.info("Processing company from documents", labels={
            "company": {
                "id": request.id,
                "name": request.name
            }
        })
        
        try:
            # Fetch and store PDF
            pdf_bytes, gcs_path = await self._fetch_and_store_pdf(request.id, request.sources)
            
            # Extract text from PDF
            extracted_text = await self._extract_data_from_pdf(pdf_bytes)
            
            # Build public URL and update company
            public_url = f"https://api.dvcagent.com/media/{gcs_path}"
            company = await self._update_company_success(request.id, public_url)
            
        except Exception as e:
            await self._update_company_error(request.id, str(e))
            self.logger.error("Company processing failed", labels={
                "company": {
                    "id": request.id,
                    "name": request.name
                },
                "error": str(e)
            })
            raise
            
        self.logger.info("Company processing completed", labels={
            "company": {
                "id": request.id,
                "name": request.name
            },
            "textLength": len(extracted_text),
            "pdfUrl": public_url
        })
        
        return request.id


    async def _fetch_and_store_pdf(self, company_id: str, sources: list) -> tuple[bytes, str]:
        """Fetch PDF and store it in GCS, return bytes and GCS path"""
        pdf_bytes = None
        
        for source in sources:
            if source['type'] == 'url':
                # Download from URL
                downloader = URLDownloader(source['url'], self.logger)
                pdf_bytes = await downloader.process_content()
                break
            elif source['type'] == 'pdf':
                # Copy from temp bucket location
                bucket = self.storage_client.bucket(source['bucket'])
                temp_blob = bucket.blob(source['key'])
                pdf_bytes = temp_blob.download_as_bytes()
                break
        
        if not pdf_bytes:
            raise ValueError("No valid PDF source found")
        
        # Store in company folder
        final_path = f"companies/{company_id}/pitch.pdf"
        bucket = self.storage_client.bucket("dvc-pdfs")
        final_blob = bucket.blob(final_path)
        final_blob.upload_from_string(pdf_bytes, content_type="application/pdf")
        
        return pdf_bytes, final_path

    async def _extract_data_from_pdf(self, pdf_bytes: bytes) -> str:
        """Uses PDFlyweight to extract text from PDF"""
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
            
            return extracted_text

    async def _update_company_success(self, company_id: str, public_url: str):
        """Update company with successful processing results"""
        result = await self.database["companies"].find_one_and_update(
            {"_id": ObjectId(company_id)},
            {
                "$set": {
                    "status": CompanyStatus.NEW_COMPANY,
                    "ourData.linkToDeck": public_url,
                    "processedAt": datetime.now()
                },
                "$unset": {"lastError": "", "sources": ""}
            },
            return_document=True
        )
        return result

    async def _update_company_error(self, company_id: str, error_msg: str):
        """Update company with processing error"""
        await self.database["companies"].update_one(
            {"_id": ObjectId(company_id)},
            {"$set": {"lastError": error_msg}}
        )