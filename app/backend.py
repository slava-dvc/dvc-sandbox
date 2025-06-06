import sys

from fastapi import FastAPI
from app.foundation import server

class BackendServer(server.FastAPIServer):

    def setup_routes(self, app: FastAPI):
        super().setup_routes(app)

        from app import integrations

        app.include_router(integrations.router, prefix='/v1')
    

    async def __aenter__(self) -> Dict[Str, Any]:
        state = await self.http_client.__aenter__()
        return state |  {
            "dataset_bucket": self.storage_client.bucket("dvc-dataset-v2"),
        }

server = BackendServer()
app: FastAPI = server.app


if __name__ == '__main__':
    sys.exit(server.run())
