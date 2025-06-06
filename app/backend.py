import sys

from fastapi import FastAPI
from app.foundation import server

class BackendServer(server.FastAPIServer):

    def setup_routes(self, app: FastAPI):
        super().setup_routes(app)

        from app import integrations

        app.include_router(integrations.router, prefix='/v1')
    


server = BackendServer()
app: FastAPI = server.app


if __name__ == '__main__':
    sys.exit(server.run())
