import sys
from app.foundation import server
from fastapi import APIRouter, FastAPI
from app import integrations


class BackendServer(server.FastAPIServer):

    def setup_app(self, app: FastAPI):
        super().setup_app(app)
        app.include_router(integrations.router)


server = BackendServer()
app = server.app


if __name__ == '__main__':
    sys.exit(server.run())
