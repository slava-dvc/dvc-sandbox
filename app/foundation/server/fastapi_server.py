import logging
from contextlib import asynccontextmanager

import uvicorn
from functools import cached_property
from fastapi import FastAPI

from .async_server import AsyncServer
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
