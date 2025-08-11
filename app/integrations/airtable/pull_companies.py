from typing import Dict, Any
from pymongo.asynchronous.mongo_client import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection

from app.shared import Company, AirTableClient
from app.foundation.server import Logger
from app.foundation.primitives import datetime


_STATUS_MAP = {
    "Invested":"Invested",
    "Exit": "Exit",
    "Write-off": "Write-off",
    "Docs Sent": "Docs Sent",
    "Offered to Invest": "Offered to Invest",
    "New Company": "New Company",
    "w8 Lead": "Diligence",
    "Diligence": "Diligence",
    "Contacted": "In Progress",
    "Checkin": "In Progress",
    "Second Meeting": "In Progress",
    "DD/HomeWork": "In Progress",
    "Fast Track": "In Progress",
    "Going to Pass": "Going to Pass",
}


async def _process_company_record(record: Dict[str, Any], companies_collection: AsyncCollection, logger: Logger) -> None:
    """
    Process an individual Airtable record and store it in MongoDB.

    Args:
        record (Dict[str, Any]): Airtable record data containing fields and metadata.
        companies_collection (AsyncCollection): MongoDB collection for storing company data.

    Returns:
        None: This function performs database operations but does not return a value.
    """
    fields = record["fields"]
    status = fields.get("Status")

    company_data = {
        "name": (fields.get("Company") or "").strip(),
        "website": fields.get("URL"),
        "airtableId": record["id"],
        "blurb": fields.get("Blurb"),
        "status": _STATUS_MAP[status],
        "ourData": {
            "businessModel": fields.get("Business Model"),
            "category": fields.get("Category"),
            "companyHQ": fields.get("Company HQ"),
            "distributionModelType": fields.get("Distribution Strategy"),
            "linkToDeck": fields.get("Linktothepitchdeck"),
            "logo": fields.get("Logo"),
            "mainIndustry": fields.get("Main Industry"),
            "problem": fields.get("Problem"),
            "productStructure": fields.get("Product Structure"),
            "revenueModelType": fields.get("Revenue Model Type"),
            "targetMarket": fields.get("Target Market"),
            'burnRate': fields.get('Burnrate'),
            'currentStage': fields.get('Company Stage'),
            'entryStage': fields.get('Stage when we invested'),
            'entryValuation': fields.get('Initial Valuation'),
            'investingFund': fields.get('Initial Fund Invested From'),
            'latestValuation': fields.get('Last Valuation/cap (from DVC Portfolio 3)'),
            'performanceOutlook': fields.get('Expected Performance'),
            'revenue': fields.get('Revenue copy'),
            'runway': fields.get('Runway'),
        }
    }

    # Create Company model
    company = Company(**company_data)

    # Upsert to MongoDB (update if exists, insert if new)
    result = await companies_collection.update_one(
        {"airtableId": company.airtableId},
        {
            "$set": company.model_dump(exclude_none=True),
            "$setOnInsert": {
                "createdAt": datetime.now(),
            }
        },
        upsert=True
    )

    # if result.upserted_id:
    #     logger.info(f"Inserted new company: {company.name}")
    # else:
    #     logger.info(f"Updated existing company: {company.name}")

    return True


async def pull_companies_from_airtable(
    airtable_client: AirTableClient,
    mongo_client: AsyncMongoClient,
    table_id: str,
    logger: Logger,
) -> int:
    """
    Pull companies from Airtable and store them in MongoDB.
    
    Args:
        http_client: HTTP client for Airtable API calls
        mongo_client: MongoDB client for storing data
        api_key: Airtable API key
        base_id: Airtable base ID
        table_id: Airtable table ID containing company data
        
    Returns:
        Number of records processed
    """

    # Get records from Airtable
    records = await airtable_client.list_records(table_id=table_id, resolve=True)
    default_database = mongo_client.get_default_database()
    companies_collection = default_database['companies']

    # Process each record
    processed_count = 0
    for record in records:
        fields = record["fields"]
        status = fields.get("Status")
        name = fields.get("Company")
        url = fields.get('URL')

        if status not in _STATUS_MAP:
            logger.info(
                msg="Skipping record",
                labels={
                    "id": record["id"],
                    "reason": "Invalid status",
                    "status": status,
                    "company": name,
                }
            )
            continue
        if not name:
            logger.info(
                msg="Skipping record",
                labels={
                    "id": record["id"],
                    "company": name,
                    "reason": "Missing company name",

                }
            )
            continue
        if not url:
            logger.info(
                msg="Skipping record",
                labels={
                    "id": record["id"],
                    "company": name,
                    "reason": "Missing URL",
                }
            )
            continue
        processed = await _process_company_record(record, companies_collection, logger)
        processed_count += processed
    
    return processed_count

