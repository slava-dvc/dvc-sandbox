import asyncio
import multiprocessing
from contextlib import asynccontextmanager
from typing import Dict, Any, AnyStr as Str

import httpx
import uvicorn
from fastapi.exceptions import RequestValidationError

from pymongo import AsyncMongoClient
from pymongo.errors import PyMongoError
from pymongo.asynchronous import database
from google.cloud import firestore, pubsub, storage
from functools import cached_property
from fastapi import FastAPI, Depends, Request
from fastapi.middleware import gzip, trustedhost
from starlette.middleware.authentication import AuthenticationMiddleware

from .async_server import AsyncServer
from .exception_handlers import *
from ..middleware import RequestTimeoutMiddleware
from ..env import get_env
from .dependencies import get_logger


__all__ = ['FastAPIServer']


class FastAPIServer(AsyncServer):

    @cached_property
    def app(self) -> FastAPI:

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            async with self as resources:
                yield resources

        app = FastAPI(
            lifespan=lifespan,
            openapi_url="/docs/openapi.json"
        )

        self.setup_exception_handlers(app)
        self.setup_middleware(app)
        self.setup_routes(app)
        return app

    @cached_property
    def http_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            transport=httpx.AsyncHTTPTransport(retries=3),
            timeout=httpx.Timeout(60*5),
        )

    @cached_property
    def firestore_client(self) -> firestore.AsyncClient:
        return firestore.AsyncClient()

    @cached_property
    def pubsub_client(self) -> pubsub.PublisherClient:
        return pubsub.PublisherClient()

    @cached_property
    def mongo_client(self) -> AsyncMongoClient:
        return AsyncMongoClient(str(get_env('MONGODB_URI')), tz_aware=True)

    @cached_property
    def storage_client(self) -> Any:
        return storage.Client()

    @cached_property
    def default_database(self) -> database.AsyncDatabase:
        return self.mongo_client.get_default_database()

    async def __aenter__(self) -> Dict[Str, Any]:
        await self.http_client.__aenter__()
        state = {
            "http_client": self.http_client,
            "firestore_client": self.firestore_client,
            "pubsub_client": self.pubsub_client,
            "mongo_client": self.mongo_client,
            "storage_client": self.storage_client,
            "config": self.config,
            "args": self.args,
            "logging_client": self.logging_client,
        }
        return state

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.__aexit__(exc_type, exc_val, exc_tb)
        await self.mongo_client.close()
        self.firestore_client.close()
        self.pubsub_client.transport.close()

    def setup_exception_handlers(self, app: FastAPI):
        for exception_class in [
            RequestValidationError
        ]:
            app.add_exception_handler(exception_class, request_validation_exception_handler)

        for exception_class in [
            ArithmeticError, AssertionError, AttributeError, LookupError, ImportError, MemoryError,
            ReferenceError, ValueError, TypeError, OSError, RuntimeError, PyMongoError
        ]:
            app.add_exception_handler(exception_class, runtime_exception_handler)

        for exception_class in [
            asyncio.TimeoutError
        ]:
            app.add_exception_handler(exception_class, timeout_exception_handler)

        for exception_class in [
            httpx.HTTPStatusError
        ]:
            app.add_exception_handler(exception_class, http_exception_handler)

    def setup_middleware(self, app: FastAPI):
        app.add_middleware(RequestTimeoutMiddleware, timeout=1800)
        app.add_middleware(trustedhost.TrustedHostMiddleware, allowed_hosts=["*"])
        app.add_middleware(gzip.GZipMiddleware)
        # app.add_middleware(AuthenticationMiddleware)

    def setup_routes(self, app: FastAPI):

        @app.get('/ping')
        @app.get('/')
        @app.get('/ok')
        async def root(
                request: Request,
                logger = Depends(get_logger),
        ):
            logger.info("I'm alive!")
            if 'exception' in request.query_params:
                raise RuntimeError("Exception requested")
            return "OK"

    def execute(self):
        multiprocessing.set_start_method('spawn')
        return uvicorn.run(
            app=self.app,
            host="0.0.0.0",
            port=self.args['port'],
            # We don't need access logs in cloud environment
            access_log=not self.args['cloud'],
            # Autoreload creates more pain than benefit
            reload=False,
            # Following settings have to be None or false so uvicorn doesn't create its own logger'
            log_config=None,
            log_level=None,
            use_colors=False
        )