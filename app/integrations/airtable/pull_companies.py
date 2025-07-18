from typing import Dict, Any
from pymongo.asynchronous.mongo_client import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
import httpx

from .client import AirTableClient
from .company_model import Company
from ...foundation.server.logger import Logger


async def process_company_record(record: Dict[str, Any], companies_collection: AsyncCollection, logger: Logger) -> None:
    """
    Process an individual Airtable record and store it in MongoDB.

    Args:
        record (Dict[str, Any]): Airtable record data containing fields and metadata.
        companies_collection (AsyncCollection): MongoDB collection for storing company data.

    Returns:
        None: This function performs database operations but does not return a value.
    """
    fields = record["fields"]

    # Skip records without a name
    if not fields.get("Company") or not fields.get('URL'):
        logger.warning(f"Skipping record {record['id']} - missing company name")
        return False

    # Extract company data from record
    company_data = {
        "name": (fields.get("Company") or "").strip(),
        "website": fields.get("URL"),
        "airtableId": record["id"],
        "blurb": fields.get("Blurb"),
    }

    # Create Company model
    company = Company(**company_data)

    # Upsert to MongoDB (update if exists, insert if new)
    result = await companies_collection.update_one(
        {"airtableId": company.airtableId},
        {
            "$set": company.model_dump(exclude_none=True)
        },
        upsert=True
    )

    if result.upserted_id:
        logger.info(f"Inserted new company: {company.name}")
    else:
        logger.info(f"Updated existing company: {company.name}")

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
    records = await airtable_client.list_records(table_id)
    default_database = mongo_client.get_default_database()
    companies_collection = default_database['companies']

    # Process each record
    processed_count = 0
    for record in records:
        fields = record["fields"]
        initial_fund_invested = fields.get('Initial Fund Invested From')
        if not initial_fund_invested or not isinstance(initial_fund_invested, str):
            logger.debug(f"Skipping record {record['id']}, {fields.get('Company')} - missing initial fund invested")
            continue
        processed = await process_company_record(record, companies_collection, logger)
        processed_count += processed
    
    return processed_count
