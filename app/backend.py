import sys
from typing import Dict, Any, AnyStr as Str

from fastapi import FastAPI
from app.foundation import server
from app.shared.spectr import SpectrClient


class BackendServer(server.FastAPIServer):

    def setup_routes(self, app: FastAPI):
        super().setup_routes(app)

        from app import integrations, pdftotext

        app.include_router(integrations.router, prefix='/v1')
        app.include_router(pdftotext.router, prefix='/v1')
    
    async def __aenter__(self) -> Dict[Str, Any]:
        resources = await super().__aenter__()
        resources["spectr_client"] = SpectrClient(resources["logging_client"], resources["http_client"])
        return resources


server = BackendServer()
app: FastAPI = server.app


if __name__ == '__main__':
    sys.exit(server.run())
