from google.cloud import storage
from pymongo.asynchronous.database import AsyncDatabase

from app.foundation.server import Logger
from app.foundation.primitives import datetime
from app.companies.models import CompanyCreateRequest, DocumentSourceType
from app.companies.crud import Crud


class CompanyFromDocsFlow:
    """Flow for creating companies from PDF documents"""
    
    def __init__(
            self,
            database: AsyncDatabase,
            storage_client: storage.Client,
            logger: Logger
    ):
        self.database = database
        self.storage_client = storage_client
        self.logger = logger
        self.crud = Crud(database)
    
    async def __call__(self, request: CompanyCreateRequest) -> str:
        """Process documents and create company"""
        self.logger.info("Processing company from documents", extra={
            "data": request.model_dump()
        })
        
        extracted_data = []

        
        self.logger.info("Company created from documents", extra={
            "data": request.model_dump()
        })
        
        return company.id
    
