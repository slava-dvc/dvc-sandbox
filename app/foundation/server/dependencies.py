from fastapi import Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pymongo import MongoClient
from google.cloud import firestore, pubsub, logging
from httpx import AsyncClient

from .config import AppConfig


security = HTTPBearer(auto_error=False)


# Dependency to get the application config
def get_config(request: Request) -> AppConfig:
    return request.state.config


# Dependency to get the logger
def get_cloud_logger(request: Request) -> logging.Logger:
    return request.state.logger


# Dependency to get the MongoDB client
def get_mongo_client(request: Request) -> MongoClient:
    return request.state.mongo_client


# Dependency to get the default MongoDB database
def get_default_database(request: Request):
    return request.state.mongo_client.get_default_database()


# Dependency to get the Firestore client
def get_firestore_client(request: Request) -> firestore.Client:
    return request.state.firestore_client


# Dependency to get the PubSub client
def get_pubsub_client(request: Request) -> pubsub.PublisherClient:
    return request.state.pubsub_client


# Dependency to get the HTTP client
def get_http_client(request: Request) -> AsyncClient:
    return request.state.http_client


# Dependency to extract token from a Bearer authorization header
def get_auth_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    if credentials:
        return credentials.credentials
    return None
