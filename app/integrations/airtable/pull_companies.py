from typing import Dict, Any
from pymongo.asynchronous.mongo_client import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection

from app.shared import Company, CompanyStatus, AirTableClient
from app.foundation.server import Logger
from app.foundation.primitives import datetime


_STATUS_MAP = {
    "Invested": CompanyStatus.Invested,
    "Exit": CompanyStatus.Exit,
    "Write-off": CompanyStatus.WriteOff,
    "Docs Sent": CompanyStatus.DocsSent,
    "Offered to Invest": CompanyStatus.OfferedToInvest,
    "New Company": CompanyStatus.NewCompany,
    "w8 Lead": CompanyStatus.Diligence,
    "Diligence": CompanyStatus.Diligence,
    "Contacted": CompanyStatus.InProgress,
    "Checkin": CompanyStatus.InProgress,
    "Second Meeting": CompanyStatus.InProgress,
    "DD/HomeWork": CompanyStatus.InProgress,
    "Fast Track": CompanyStatus.InProgress,
    "Going to Pass": CompanyStatus.GoingToPass,
}


def _unwrap_single_item(value):
    if isinstance(value, list) and len(value) == 1:
        return value[0]
    return value


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
            "businessModelType": fields.get("Business Model"),
            "category": fields.get("Category"),
            "companyHQ": fields.get("Company HQ"),
            "distributionModelType": fields.get("Distribution Strategy"),
            "linkToDeck": fields.get("Linktothepitchdeck"),
            "logo": fields.get("Logo"),
            "mainIndustry": fields.get("Main Industry"),
            "problem": fields.get("Problem"),
            "productStructureType": fields.get("Product Structure"),
            "revenueModelType": fields.get("Revenue Model Type"),
            "targetMarket": fields.get("Target Market"),
            'burnRate': fields.get('Burnrate'),
            'currentStage': _unwrap_single_item(fields.get('Company Stage')),
            'entryStage': _unwrap_single_item(fields.get('Stage when we invested')),
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

    if result.upserted_id:
        logger.info(
            "Company inserted",
            labels={
                "company": company.model_dump(exclude_none=True, exclude=['ourData']),
                "operation": "insert",
                "airtableId": company.airtableId
            }
        )
    else:
        logger.info(
            "Company updated", 
            labels={
                "company": company.model_dump(exclude_none=True,  exclude=['ourData']),
                "operation": "update",
                "airtableId": company.airtableId,
                "matched_count": result.matched_count,
                "modified_count": result.modified_count
            }
        )
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
    logger.info(
        "Starting Airtable companies sync",
        labels={"table_id": table_id}
    )
    records = await airtable_client.list_records(table_id=table_id, resolve=True)
    logger.info(
        "Fetched records from Airtable",
        labels={"table_id": table_id, "total_records": len(records)}
    )
    
    default_database = mongo_client.get_default_database()
    companies_collection = default_database['companies']

    # Process each record
    processed_count = 0
    skipped_count = 0
    
    for i, record in enumerate(records, 1):
        fields = record["fields"]
        status = fields.get("Status")
        name = fields.get("Company")
        url = fields.get('URL')

        if status not in _STATUS_MAP:
            logger.info(
                "Skipping record - invalid status",
                labels={
                    "record_id": record["id"],
                    "company": name,
                    "status": status,
                    "valid_statuses": list(_STATUS_MAP.keys())
                }
            )
            skipped_count += 1
            continue

        if not name:
            logger.info(
                "Skipping record - missing company name",
                labels={
                    "record_id": record["id"],
                    "status": status
                }
            )
            skipped_count += 1
            continue

        await _process_company_record(record, companies_collection, logger)
        processed_count += 1

    # Summary logging
    logger.info(
        "Airtable companies sync completed",
        labels={
            "table_id": table_id,
            "total_records": len(records),
            "processed_count": processed_count,
            "skipped_count": skipped_count,
            "success_rate": round((processed_count / len(records)) * 100, 1) if records else 0
        }
    )
    
    return processed_count

