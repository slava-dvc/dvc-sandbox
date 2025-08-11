from httpx import HTTPError
from fastapi.encoders import jsonable_encoder
from urllib.parse import urlparse
from pymongo.asynchronous.mongo_client import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection

from app.shared import SpectrClient, Company
from app.foundation.server import Logger
from app.foundation.primitives import datetime


class SpectrSyncAction:
    """
    Sync action for enriching company data with Spectr information.
    
    This class is callable and will process all companies in the MongoDB database,
    enriching them with Spectr data if they don't already have a spectrId,
    or updating existing companies with the latest Spectr data.
    """
    
    def __init__(
        self,
        mongo_client: AsyncMongoClient,
        spectr_client: SpectrClient,
        logger: Logger
    ):
        """
        Initialize the Spectr sync action with required dependencies.
        
        Args:
            mongo_client: MongoDB client for database operations
            spectr_client: SpectrClient for interacting with Spectr API
            logger: Logger instance for structured logging
        """
        self.mongo_client = mongo_client
        self.spectr_client = spectr_client
        self.logger = logger

    async def __call__(self, limit: int = 0xFFFFFFFF) -> int:
        """
        Process all companies in MongoDB, enriching them with Spectr data.
        
        For each company:
        - If it has no spectrId, use website to enrich and add spectrId
        - If it has a spectrId, use it to update company with latest data
        
        Returns:
            int: Number of companies processed
        """
        processed_count = 0
        
        # Get the companies collection
        default_database = self.mongo_client.get_default_database()
        companies_collection = default_database['companies']
        # Spectr credits are limited. So I update only companies witch were updated more than 3 days ago
        three_days_ago = datetime.now() - datetime.timedelta(days=3)
        # Get all companies
        cursor = companies_collection.find(
            filter={
                'status': 'Invested',
                '$or': [
                    {'spectrUpdatedAt': {'$lte': three_days_ago}},
                    {'spectrUpdatedAt': None}
                ],
            }
        )
        async for company_doc in cursor:
            try:
                # Convert to Company model with only valid fields
                company_data = {field: company_doc[field] for field in Company.model_fields if field in company_doc}
                company = Company(**company_data)

                # Process company based on whether it has a spectrId
                if not company.spectrId:
                    processed = await self._enrich_new_company(company, companies_collection)
                else:
                    processed = await self._update_existing_company(company, companies_collection)
            
                processed_count += int(processed)
                if processed_count >= limit:
                    break
            except HTTPError as e:
                self.logger.error(
                    'Error processing company',
                    labels={
                        'companyName': company_doc.get("name", "unknown"),
                        'airtableId': company_doc.get("airtableId"),
                        'spectrId': company_doc.get("spectrId"),
                        'website': company_doc.get("website"),
                        'error': str(e),
                        'company': jsonable_encoder(company.dict()),
                    },
                    exc_info=e
                )
        
        return processed_count
    
    async def _enrich_new_company(self, company: Company, collection: AsyncCollection) -> bool:
        """
        Enrich a company without spectrId using its website.
        
        Args:
            company: Company model to enrich
            collection: MongoDB collection for companies
            
        Returns:
            bool: True if company was successfully enriched
        """
        if not company.website:
            self.logger.warning(
                'Cannot enrich company: no website provided',
                labels={
                    'companyName': company.name,
                    'airtableId': company.airtableId,
                    'spectrId': company.spectrId
                }
            )
            return False
        parsed_url = urlparse(company.website)
        if parsed_url.netloc in {'docsend.com'}:
            self.logger.warning(
                'Cannot enrich company: not a company website',
                labels={
                    'companyName': company.name,
                    'airtableId': company.airtableId,
                    'spectrId': company.spectrId,
                    'website': company.website,
                    'netloc': parsed_url.netloc
                }
            )
            return False
        try:
            # Call Spectr API to enrich company by website
            enrichment_result = await self.spectr_client.enrich_companies(website_url=company.website)
            
            # No companies found
            if not enrichment_result or not isinstance(enrichment_result, list):
                self.logger.info(
                    'No Spectr data found for company',
                    labels={
                        'companyName': company.name,
                        'airtableId': company.airtableId,
                        'spectrId': company.spectrId,
                        'website': company.website
                    }
                )
                return False
                
            # Multiple companies found - ambiguous result
            if len(enrichment_result) > 1:
                self.logger.warning(
                    'Multiple Spectr matches found for company',
                    labels={
                        'companyName': company.name,
                        'airtableId': company.airtableId,
                        'spectrId': company.spectrId,
                        'website': company.website,
                        'matchCount': len(enrichment_result)
                    }
                )
                return False
            
            # Get the company data from enrichment result (we've verified there's exactly one item)
            spectr_company = enrichment_result[0]
            
            # Update company with spectrId and additional data
            update_data = {
                'spectrId': spectr_company['id'],
                'spectrUpdatedAt': datetime.now(),
                'spectrData': spectr_company
            }
            
            # Update in MongoDB
            result = await collection.update_one(
                {"airtableId": company.airtableId},
                {"$set": update_data}
            )
            
            if result.modified_count:
                self.logger.info(
                    'Enriched company with Spectr ID',
                    labels={
                        'companyName': company.name,
                        'airtableId': company.airtableId,
                        'spectrId': company.spectrId,
                        'website': company.website
                    }
                )
                return True
                
            return False
            
        except HTTPError as e:
            self.logger.error(
                'Error enriching company',
                labels={
                    'companyName': company.name,
                    'airtableId': company.airtableId,
                    'spectrId': company.spectrId,
                    'website': company.website,
                    'company': jsonable_encoder(company.dict()),
                    'error': str(e)
                },
                exc_info=e
            )
            return False
    
    async def _update_existing_company(self, company: Company, collection: AsyncCollection) -> bool:
        """
        Update a company that already has a spectrId.
        
        Args:
            company: Company model to update
            collection: MongoDB collection for companies
            
        Returns:
            bool: True if company was successfully updated
        """
        
        try:
            # Get updated company data from Spectr
            spectr_company = await self.spectr_client.get_company_by_id(company.spectrId)
            
            if not spectr_company:
                self.logger.warning(
                    'No Spectr data found for company',
                    labels={
                        'companyName': company.name,
                        'airtableId': company.airtableId,
                        'spectrId': company.spectrId,
                        'website': company.website
                    }
                )
                return False
            
            # Update the company's Spectr data
            update_data = {
                'spectrUpdatedAt': datetime.now(),
                'spectrData': spectr_company
            }
            
            # Update in MongoDB
            result = await collection.update_one(
                {"spectrId": company.spectrId},
                {"$set": update_data}
            )
            
            if result.modified_count:
                self.logger.info(
                    'Updated company with latest Spectr data',
                    labels={
                        'companyName': company.name,
                        'airtableId': company.airtableId,
                        'spectrId': company.spectrId,
                        'website': company.website
                    }
                )
                return True
            else:
                self.logger.error(
                    'Company does not exist in MongoDB or data is the same',
                    labels={
                        'companyName': company.name,
                        'airtableId': company.airtableId,
                        'spectrId': company.spectrId,
                        'website': company.website
                    }
                )
            return False
            
        except HTTPError as e:
            self.logger.error(
                'Error updating company',
                labels={
                    'companyName': company.name,
                    'airtableId': company.airtableId,
                    'spectrId': company.spectrId,
                    'website': company.website,
                    'company': jsonable_encoder(company.dict()),
                    'error': str(e)
                },
                exc_info=e
            )
            return False
