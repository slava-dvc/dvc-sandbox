import asyncio
import logging
import multiprocessing

import httpx
from contextlib import asynccontextmanager

import uvicorn
from functools import cached_property
from fastapi import FastAPI

from .async_server import AsyncServer
from .exception_handlers import *
from ..middleware import RequestTimeoutMiddleware


__all__ = ['FastAPIServer']


class FastAPIServer(AsyncServer):

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        yield

    @cached_property
    def app(self):
        app = FastAPI(
            dependencies=self.dependencies,
            debug=self.args['debug'],
            lifespan=self.lifespan
        )
        for exception_class in [
            ArithmeticError, AssertionError, AttributeError, LookupError, ImportError, MemoryError,
            ReferenceError, ValueError, TypeError, OSError, RuntimeError
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

        app.add_middleware(RequestTimeoutMiddleware, timeout=60)
        self.setup_app(app)
        return app

    @property
    def dependencies(self):
        return []

    def setup_app(self, app: FastAPI):
        pass

    def execute(self):
        multiprocessing.set_start_method('spawn')

        with self.loop_executor:
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