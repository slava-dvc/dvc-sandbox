from typing import Dict, Any
from pymongo.asynchronous.mongo_client import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection

from app.shared import Company, CompanyStatus, AirTableClient
from app.foundation.server import Logger
from app.foundation.primitives import datetime
from app.company_data.job_dispatcher import JobDispatcher


_STATUS_MAP = {
    "Invested": CompanyStatus.INVESTED,
    "Exit": CompanyStatus.EXIT,
    "Write-off": CompanyStatus.WRITE_OFF,
    "Docs Sent": CompanyStatus.DOCS_SENT,
    "Offered to Invest": CompanyStatus.OFFERED_TO_INVEST,
    "New Company": CompanyStatus.NEW_COMPANY,
    "w8 Lead": CompanyStatus.DILIGENCE,
    "Diligence": CompanyStatus.DILIGENCE,
    "Contacted": CompanyStatus.CONTACTED,
    "Meeting": CompanyStatus.MEETING,
    "Checkin": CompanyStatus.CHECKIN,
    "Submitted AL": CompanyStatus.SUBMITTED_AL,
    "Second Meeting": CompanyStatus.MEETING,
    "DD/HomeWork": CompanyStatus.DILIGENCE,
    "Going to Pass": CompanyStatus.GOING_TO_PASS,
    "Going to pass": CompanyStatus.GOING_TO_PASS,
    "Radar": CompanyStatus.RADAR,
}



def _unwrap_single_item(value):
    if isinstance(value, list) and len(value) == 1:
        return value[0]
    return value


async def _process_company_record(record: Dict[str, Any], companies_collection: AsyncCollection, logger: Logger, job_dispatcher: JobDispatcher) -> None:
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
        "id": None,
        "name": (fields.get("Company") or "").strip(),
        "website": fields.get("URL"),
        "airtableId": record["id"],
        "blurb": fields.get("Blurb"),
        "status": _STATUS_MAP[status],
        "ourData": {
            "summary": fields.get("DVC Summary"),
            "businessModelType": fields.get("Business Model"),
            "category": fields.get("Category"),
            "companyHQ": fields.get("Company HQ"),
            "distributionModelType": fields.get("Distribution Strategy"),
            "linkToDeck": fields.get("Linktothepitchdeck"),
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
            'source': fields.get('Source'),
            'traction': fields.get('Traction (for minimemo)'),
            'businessModel': fields.get('Business Model'),
            'marketSize': fields.get('Market Size'),
        }
    }

    # Create Company model
    company = Company.model_validate(company_data)

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
        company.id = str(result.upserted_id)
        logger.info(
            "Company inserted",
            labels={
                "company": company.model_dump_for_logs(),
                "operation": "insert",
                "airtableId": company.airtableId
            }
        )
        # Trigger Spectr update if company has valid website
        if company.has_valid_website():
            try:
                await job_dispatcher.trigger_one(company, "spectr")
            except Exception as e:
                logger.error(
                    "Failed to trigger Spectr update",
                    exc_info=e,
                    labels={
                        "company": company.model_dump_for_logs(),
                    }
                )
    else:
        logger.info(
            "Company updated", 
            labels={
                "company": company.model_dump_for_logs(),
                "operation": "update",
                "airtableId": company.airtableId,
                "matchedCount": result.matched_count,
                "modifiedCount": result.modified_count
            }
        )
    

    
    return True


async def pull_companies_from_airtable(
    airtable_client: AirTableClient,
    mongo_client: AsyncMongoClient,
    table_id: str,
    logger: Logger,
    job_dispatcher: JobDispatcher,
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
                    "airtableId": record["id"],
                    "company": name,
                    "status": status,
                }
            )
            skipped_count += 1
            continue

        if not name:
            logger.info(
                "Skipping record - missing company name",
                labels={
                    "airtableId": record["id"],
                    "status": status
                }
            )
            skipped_count += 1
            continue

        await _process_company_record(record, companies_collection, logger, job_dispatcher)
        processed_count += 1

    # Summary logging
    logger.info(
        "Airtable companies sync completed",
        labels={
            "tableId": table_id,
            "totalRecords": len(records),
            "processedCount": processed_count,
            "skippedCount": skipped_count,
            "successRate": round((processed_count / len(records)) * 100, 1) if records else 0
        }
    )
    
    return processed_count

