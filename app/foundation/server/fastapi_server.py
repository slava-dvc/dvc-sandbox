import asyncio
import logging
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
        with self.loop_executor:
            uvicorn.run(
                app=self.app,
                host="0.0.0.0",
                port=self.args['port'],
                access_log=not self.args['cloud'],
                log_level=logging.DEBUG if self.args['debug'] else logging.INFO,
                use_colors=True
            )
