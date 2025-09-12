from fastapi import APIRouter, Depends, HTTPException, Request, Body
from pymongo.asynchronous.database import AsyncDatabase
from google.cloud import storage
import openai

from app.foundation.server import dependencies, Logger
from app.companies.crud import Crud
from app.companies.models import CompanyUpdateRequest, CompanyCreateRequest
from app.companies.document_flow import CompanyFromDocsFlow


router = APIRouter(
    prefix="/companies",
)


public_router = APIRouter(
    prefix="/companies",
    tags=["public"]
)


@router.patch("/{company_id}")
async def update_company(
    company_id: str,
    update_request: CompanyUpdateRequest,
    database: AsyncDatabase = Depends(dependencies.get_default_database),
    logger: Logger = Depends(dependencies.get_logger),
):
    """Update a company"""
    crud = Crud(database)
    
    company = await crud.update_company(company_id, update_request)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    return company.model_dump(by_alias=True)

@router.post("/{company_id}/memorandum")
@public_router.post("/{company_id}/memorandum")
async def update_memorandum_webhook(
    company_id: str,
    request: Request,
    database: AsyncDatabase = Depends(dependencies.get_default_database),
    logger: Logger = Depends(dependencies.get_logger),
):
    """Webhook endpoint to update company memorandum with plain text"""
    crud = Crud(database)
    body = (await request.body()).decode("utf-8")
    update_request = CompanyUpdateRequest(memorandum=body)
    
    company = await crud.update_company(company_id, update_request)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    return {"status": "success", "companyId": company_id}


@router.post("/create_from_docs/consume")
async def create_from_docs_consume(
    create_request: CompanyCreateRequest,
    database: AsyncDatabase = Depends(dependencies.get_default_database),
    logger: Logger = Depends(dependencies.get_logger),
    storage_client: storage.Client = Depends(dependencies.get_storage_client),
    openai_client: openai.AsyncOpenAI = Depends(dependencies.get_openai_client),
):
    """Pub/Sub consumer endpoint to create company from documents"""
    flow = CompanyFromDocsFlow(database, storage_client, openai_client, logger)    
    await flow(create_request)