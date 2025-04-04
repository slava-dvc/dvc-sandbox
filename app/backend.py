import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.foundation import server
from app.shared.lifespan_objects import lifespan_objects


class BackendServer(server.FastAPIServer):

    def setup_routes(self, app: FastAPI):
        super().setup_routes(app)

        from app import integrations, pdftotext

        app.include_router(integrations.router, prefix='/v1')
        app.include_router(pdftotext.router, prefix='/v1')


server = BackendServer()
app = server.app


if __name__ == '__main__':
    sys.exit(server.run())
