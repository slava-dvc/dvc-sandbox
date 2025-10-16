import sys
from typing import Dict, Any, AnyStr as Str
from fastapi import FastAPI
from app.foundation import server

class PublicServer(server.FastAPIServer):

    def setup_routes(self, app: FastAPI):
        super().setup_routes(app)

        from app import jobs, companies, meetings

        app.include_router(jobs.public_router, prefix='/api')
        app.include_router(companies.public_router, prefix='/api')
        app.include_router(meetings.public_router, prefix='/api')

    async def __aenter__(self) -> Dict[Str, Any]:
        state = await super().__aenter__()
        return state | {
            "dataset_bucket": self.storage_client.bucket("dvc-dataset-v2"),
        }

server = PublicServer()
app: FastAPI = server.app


if __name__ == '__main__':
    sys.exit(server.run())