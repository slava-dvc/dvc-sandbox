import sys
from contextlib import asynccontextmanager

from app.foundation import server
from fastapi import  FastAPI
from .lifespan_objects import lifespan_objects


class BackendServer(server.FastAPIServer):

    def setup_app(self, app: FastAPI):
        super().setup_app(app)

        from app import integrations

        app.include_router(integrations.router, prefix='/v1')

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        async with lifespan_objects:
            yield


server = BackendServer()
app = server.app


if __name__ == '__main__':
    sys.exit(server.run())
