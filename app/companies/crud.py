from typing import Optional
from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase
from app.foundation.primitives import datetime
from app.shared.company import Company
from app.companies.models import CompanyUpdateRequest


class Crud(object):
    """Data access layer for companies collection"""
    def __init__(self, database: AsyncDatabase):
        self._database = database
        self._companies_collection = database["companies"]
    
    async def update_company(self, company_id: str, update_request: CompanyUpdateRequest) -> Optional[Company]:
        """Update a company by ID"""
        update_data = update_request.model_dump(exclude_none=True)
        if not update_data:
            company_doc = await self._companies_collection.find_one({"_id": ObjectId(company_id)})
            return Company.model_validate(company_doc) if company_doc else None
        
        update_data["updatedAt"] = datetime.now()
        
        result = await self._companies_collection.find_one_and_update(
            {"_id": ObjectId(company_id)},
            {"$set": update_data},
            return_document=True
        )
        return Company.model_validate(result) if result else None
