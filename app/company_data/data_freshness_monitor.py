from typing import Dict, Any
from pymongo.asynchronous.database import AsyncDatabase
from app.foundation.primitives import datetime
from app.foundation.server.logger import Logger
from .constants import ACTIVE_COMPANY_STATUSES


__all__ = ["DataFreshnessMonitor"]


class DataFreshnessMonitor:

    def __init__(self, database: AsyncDatabase, logger: Logger):
        self.database = database
        self.logger = logger
        self.companies_collection = database.companies

    async def check_data_freshness(self) -> Dict[str, Any]:
        """Check data freshness for all active companies"""
        data_sources = [
            ("spectrUpdatedAt", 32),
            ("linkedinUpdatedAt", 10),
            ("googlePlayUpdatedAt", 10),
            ("googleJobsUpdatedAt", 10),
            ("appStoreUpdatedAt", 10)
        ]

        # Get total count of active companies
        total_active_companies = await self.companies_collection.count_documents({
            "status": {"$in": ACTIVE_COMPANY_STATUSES}
        })

        report = {
            "activeCompaniesCount": total_active_companies,
            "generatedAt": datetime.now(),
            "isHealthy": True
        }

        # Check each data source
        for field_name, days_threshold in data_sources:
            stats = await self._check_source_freshness(field_name, days_threshold)
            # Convert field name to report key (e.g., "spectrUpdatedAt" -> "spectrData")
            report_key = field_name.replace("UpdatedAt", "Data")
            report[report_key] = stats

            # Check if this data source has issues
            if stats["stale"] > 0 or stats["missing"] > 0:
                report["isHealthy"] = False

        self.logger.info("Generated data freshness report", labels={
            "activeCompaniesCount": total_active_companies,
            "dataSources": len(data_sources),
            "isHealthy": report["isHealthy"]
        })

        return report

    async def _check_source_freshness(self, field_name: str, days_threshold: int) -> Dict[str, Any]:
        """Check freshness for a specific data source"""
        now = datetime.now()
        threshold = now - datetime.timedelta(days=days_threshold)

        # Count fresh (updated within threshold)
        fresh_count = await self.companies_collection.count_documents({
            "status": {"$in": ACTIVE_COMPANY_STATUSES},
            field_name: {"$gte": threshold}
        })

        # Count stale (updated but outside threshold)
        stale_count = await self.companies_collection.count_documents({
            "status": {"$in": ACTIVE_COMPANY_STATUSES},
            field_name: {"$lt": threshold}
        })

        # Count missing (never updated)
        missing_count = await self.companies_collection.count_documents({
            "status": {"$in": ACTIVE_COMPANY_STATUSES},
            field_name: None
        })

        return {
            "fresh": fresh_count,
            "stale": stale_count,
            "missing": missing_count
        }