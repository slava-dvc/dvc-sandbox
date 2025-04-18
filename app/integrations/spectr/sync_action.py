import logging
from typing import Dict, Any, Optional
from pymongo.asynchronous.mongo_client import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.errors import PyMongoError

from app.shared.spectr import SpectrClient
from app.foundation.server import ConsoleLogger
from app.integrations.airtable.company_model import Company


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
        logging_client: ConsoleLogger
    ):
        """
        Initialize the Spectr sync action with required dependencies.
        
        Args:
            mongo_client: MongoDB client for database operations
            spectr_client: SpectrClient for interacting with Spectr API
            logging_client: Logging client for structured logging
        """
        self.mongo_client = mongo_client
        self.spectr_client = spectr_client
        self.logging_client = logging_client
        
    async def __call__(self) -> int:
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
        
        # Get all companies
        async for company_doc in companies_collection.find():
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
                if processed_count > 10:
                    break
            except Exception as e:
                self.logging_client.log_struct(
                    {
                        'message': f'Error processing company {company_doc.get("name", "unknown")}',
                        'error': str(e)
                    },
                    severity='ERROR'
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
            self.logging_client.log_struct(
                {
                    'message': f'Cannot enrich company {company.name}: no website provided'
                },
                severity='WARNING'
            )
            return False
        
        try:
            # Call Spectr API to enrich company by website
            enrichment_result = await self.spectr_client.enrich_companies(website_url=company.website)
            
            # No companies found
            if not enrichment_result or not isinstance(enrichment_result, list):
                self.logging_client.log_struct(
                    {
                        'message': f'No Spectr data found for company {company.name} with website {company.website}'
                    },
                    severity='INFO'
                )
                return False
                
            # Multiple companies found - ambiguous result
            if len(enrichment_result) > 1:
                self.logging_client.log_struct(
                    {
                        'message': f'Multiple {len(enrichment_result)} Spectr matches found for company {company.name} with website {company.website}',
                        'match_count': len(enrichment_result)
                    },
                    severity='WARNING'
                )
                return False
                
            # No companies in the result
            if len(enrichment_result) == 0:
                self.logging_client.log_struct(
                    {
                        'message': f'Empty result list from Spectr for company {company.name} with website {company.website}'
                    },
                    severity='INFO'
                )
                return False
            
            # Get the company data from enrichment result (we've verified there's exactly one item)
            spectr_company = enrichment_result[0]
            
            # Update company with spectrId and additional data
            update_data = {
                'spectrId': spectr_company['id'],
                'spectrData': spectr_company
            }
            
            # Update in MongoDB
            result = await collection.update_one(
                {"airtableId": company.airtableId},
                {"$set": update_data}
            )
            
            if result.modified_count:
                self.logging_client.log_struct(
                    {
                        'message': f'Enriched company {company.name} with Spectr ID {spectr_company["id"]}'
                    },
                    severity='INFO'
                )
                return True
                
            return False
            
        except Exception as e:
            self.logging_client.log_struct(
                {
                    'message': f'Error enriching company {company.name}',
                    'error': str(e)
                },
                severity='ERROR'
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
                self.logging_client.log_struct(
                    {
                        'message': f'No Spectr data found for company {company.name} with ID {company.spectrId}'
                    },
                    severity='WARNING'
                )
                return False
            
            # Update the company's Spectr data
            update_data = {
                'spectrData': spectr_company
            }
            
            # Update in MongoDB
            result = await collection.update_one(
                {"spectrId": company.spectrId},
                {"$set": update_data}
            )
            
            if result.modified_count:
                self.logging_client.log_struct(
                    {
                        'message': f'Updated company {company.name} with latest Spectr data'
                    },
                    severity='INFO'
                )
                return True
                
            return False
            
        except Exception as e:
            self.logging_client.log_struct(
                {
                    'message': f'Error updating company {company.name}',
                    'error': str(e)
                },
                severity='ERROR'
            )
            return False
