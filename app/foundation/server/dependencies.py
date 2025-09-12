from fastapi import Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pymongo.asynchronous.mongo_client import AsyncMongoClient
from google.cloud import firestore, pubsub, logging, storage
from httpx import AsyncClient
import openai

from .config import AppConfig
from .logger import CloudLogger, LocalLogger, Logger

__all__ = [
    'get_config', 'get_mongo_client', 'get_default_database', 'get_firestore_client',
    'get_publisher_client', 'get_http_client', 'get_auth_token', 'get_logger', 'get_storage_client',
    'get_dataset_bucket', 'get_openai_client'
]


security = HTTPBearer(auto_error=False)


# Dependency to get the application config
def get_config(request: Request) -> AppConfig:
    return request.state.config


def get_logger(request: Request) -> Logger:
    if request.state.logging_client:
        return CloudLogger(
            logger_client=request.state.logging_client,
            request=request,
            project_id=request.state.config['project_id']
        )
    return LocalLogger(request=request)


# Dependency to get the MongoDB client
def get_mongo_client(request: Request) -> AsyncMongoClient:
    return request.state.mongo_client


# Dependency to get the default MongoDB database
def get_default_database(request: Request):
    return request.state.mongo_client.get_default_database()


# Dependency to get the Firestore client
def get_firestore_client(request: Request) -> firestore.AsyncClient:
    return request.state.firestore_client


# Dependency to get the PubSub client
def get_publisher_client(request: Request) -> pubsub.PublisherClient:
    return request.state.publisher_client


# Dependency to get the HTTP client
def get_http_client(request: Request) -> AsyncClient:
    return request.state.http_client


# Dependency to get the Storage client
def get_storage_client(request: Request) -> storage.Client:
    return request.state.storage_client


# Dependency to get the dataset bucket
def get_dataset_bucket(request: Request) -> storage.Bucket:
    return request.state.dataset_bucket


# Dependency to get the OpenAI client
def get_openai_client(request: Request) -> openai.AsyncOpenAI:
    return request.state.openai_client


# Dependency to extract token from a Bearer authorization header
def get_auth_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    if credentials:
        return credentials.credentials
    return None
