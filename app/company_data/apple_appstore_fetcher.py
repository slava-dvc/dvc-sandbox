from typing import Dict
from urllib.parse import urlparse

from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from app.shared import Company, SerpApiClient
from app.foundation.primitives import datetime
from app.foundation.server import Logger
from .data_syncer import DataFetcher, FetchResult


__all__ = ["AppleAppStoreFetcher"]


class AppleAppStoreFetcher(DataFetcher):
    def __init__(
            self,
            database: AsyncDatabase,
            serpapi_client: SerpApiClient,
            logger: Logger
    ):
        self._database = database
        self._companies_collection = database["companies"]
        self._serpapi_client = serpapi_client
        self._logger = logger

    def source_id(self) -> str:
        return "appstore"

    def should_update(self, company: Company):
        return company.appStoreUpdatedAt is None or (
            company.appStoreData is not None and 
            company.appStoreUpdatedAt < datetime.now() - datetime.timedelta(days=7)
        )

    async def fetch_company_data(self, company: Company) -> FetchResult:
        product_id = await self._get_app_store_product_id(company.id)
        
        raw_data = {}
        app_data = None
        
        if product_id:
            raw_data = await self._serpapi_client.get_apple_product(product_id)
            if raw_data:
                app_data = self._extract_app_data(raw_data)
        else:
            self._logger.info("Company has no App Store presence", labels={
                "company_id": company.id,
                "company_name": company.name,
            })

        return FetchResult(
            raw_data=raw_data,
            remote_id=product_id,
            db_update_fields={
                "appStoreData": app_data,
                "appStoreId": product_id,
                "appStoreUpdatedAt": datetime.now()
            },
            updated_at=datetime.now()
        )

    async def _get_app_store_product_id(self, company_id: str) -> str:
        company = await self._companies_collection.find_one({"_id": ObjectId(company_id)})
        if not company:
            return ""
        
        # Check if we already have the product ID stored
        existing_product_id = company.get("appStoreId")
        if existing_product_id:
            return existing_product_id
        
        # If not, search for it using developer ID
        developer_id = self._extract_developer_id_from_itunes_url(company)
        if not developer_id:
            return ""
        
        # Search by company name and match developer ID
        company_name = company.get("name", "").split()[0]
        search_results = await self._serpapi_client.search_apple_app_store(
            term=company_name
        )
        
        if search_results and 'organic_results' in search_results:
            target_developer_id = int(developer_id)
            
            # Find the app that matches our developer ID
            for app in search_results['organic_results']:
                app_developer_id = app.get("developer", {}).get("id")
                if app_developer_id == target_developer_id:
                    product_id = str(app.get("id"))
                    
                    # Store for future use
                    await self._companies_collection.update_one(
                        {"_id": ObjectId(company_id)},
                        {"$set": {"appStoreId": product_id}}
                    )
                    return product_id
        
        return ""

    def _extract_developer_id_from_itunes_url(self, company_data: dict) -> str:
        spectr_data = company_data.get("spectrData") or {}
        socials = spectr_data.get("socials") or {}
        itunes = socials.get("itunes") or {}
        urls = itunes.get("urls") or []
        
        for url in urls:
            if '/developer/id' in url:
                developer_id = url.split('/developer/id')[-1]
                return developer_id.split('?')[0]
        
        return ""

    def _extract_app_data(self, raw_data: dict) -> dict:
        """Extract curated app data for storage in database"""
        if not raw_data:
            return {}
        
        # Get latest version info from version_history
        latest_version = {}
        version_history = raw_data.get("version_history", [])
        if version_history:
            latest = version_history[0]  # First item is latest
            latest_version = {
                "release_version": latest.get("release_version"),
                "release_notes": latest.get("release_notes"),
                "release_date": latest.get("release_date")
            }
        
        return {
            # Core app info
            "title": raw_data.get("title"),
            "id": raw_data.get("id"),
            "rating": raw_data.get("rating"),
            "rating_count": raw_data.get("rating_count"),
            "price": raw_data.get("price"),
            "age_rating": raw_data.get("age_rating"),
            "logo": raw_data.get("logo"),
            
            # Developer info
            "developer": raw_data.get("developer", {}),
            
            # Key metrics
            "description": raw_data.get("description"),
            "designed_for": raw_data.get("designed_for"),
            "in_app_purchases": raw_data.get("in_app_purchases"),
            
            # Rating breakdown
            "ratings_and_reviews": {
                "rating_percentage": raw_data.get("ratings_and_reviews", {}).get("rating_percentage", {})
            },
            
            # App details
            "information": {
                "seller": raw_data.get("information", {}).get("seller"),
                "size": raw_data.get("information", {}).get("size"),
                "categories": raw_data.get("information", {}).get("categories", []),
                "supported_languages": raw_data.get("information", {}).get("supported_languages", []),
                "age_rating": raw_data.get("information", {}).get("age_rating", {})
            },
            
            # Latest version info
            "latest_version": latest_version
        }