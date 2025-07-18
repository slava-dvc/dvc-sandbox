import re
from fastapi import Depends, Query, Body, Request
from google.cloud import firestore
from app.foundation.server.dependencies import get_logger, get_http_client, get_firestore_client, get_dataset_bucket

from .spectr_client import SpectrClient
from .scrapin_client import ScrapinClient
from .serpapi_client import SerpApiClient


async def get_scrapin_clinet(
    logger = Depends(get_logger),
    http_client = Depends(get_http_client),
) -> ScrapinClient:

    return ScrapinClient(
        logger=logger,
        http_client=http_client
    )


async def get_spectr_client(
    logger = Depends(get_logger),
    http_client = Depends(get_http_client),
    dataset_bucket = Depends(get_dataset_bucket)
) -> SpectrClient:
    return SpectrClient(
        logger=logger,
        http_client=http_client,
        dataset_bucket=dataset_bucket
    )


async def get_serpapi_client(
    logger = Depends(get_logger),
    http_client = Depends(get_http_client),
) -> SerpApiClient:
    return SerpApiClient(
        logger=logger,
        http_client=http_client
    )


def get_genai_client(request: Request):
    return request.state.genai_client


def workspace_collection(
        firestore_client = Depends(get_firestore_client)
) -> firestore.AsyncCollectionReference:
    return firestore_client.collection("workspaces")


async def workspace_by_user_email(
    request: Request,
    user_email: str = Query(None),
    # body: dict = Body(default_factory=dict),
    workspace_collection: firestore.AsyncCollectionReference = Depends(workspace_collection)
):
    body = await request.json()
    # Fetch email from user_email parameter or body
    email = user_email or body.get('user_email')

    # Validate email
    if not email or not is_valid_email(email):
        return None

    # Extract domain
    _, domain = email.split("@")

    # Validate domain
    if not is_valid_domain(domain):
        return None

    # Query workspaces where relay_email matches the domain
    async for workspace in workspace_collection.where("domain", "==", domain).stream():
        w: firestore.DocumentSnapshot = workspace
        return w.to_dict()
    return None


def is_valid_email(email: str) -> bool:
    # Basic email validation using regex
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None


def is_valid_domain(domain: str) -> bool:
    # Basic domain validation using regex
    domain_regex = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(domain_regex, domain) is not None
