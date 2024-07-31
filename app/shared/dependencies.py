import re
from fastapi import Depends, Query, Body, Request
from google.cloud import firestore
from .lifespan_objects import *


__all__ = ['workspace_by_user_email', 'lifespan_objects']



def workspace_collection(
        lifespan_objects: LifespanObjects = Depends(lifespan_objects)
) -> firestore.AsyncCollectionReference:
    return lifespan_objects.firestore_client.collection("workspaces")


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
