import sys
from typing import Dict, Any, AnyStr as Str
from functools import cached_property
from fastapi import FastAPI
from app.foundation import server
from google import genai

class BackendServer(server.FastAPIServer):

    def setup_routes(self, app: FastAPI):
        super().setup_routes(app)

        from app import integrations, company_data, jobs, companies

        app.include_router(integrations.router, prefix='/v1')
        app.include_router(company_data.router, prefix='/v1')
        app.include_router(jobs.router, prefix='/v1')
        app.include_router(companies.router, prefix='/v1')

    @cached_property
    def genai_client(self):
        return genai.Client(
            vertexai=True,
            project=self.args['project_id'],
            location=self.args['region']
        )

    async def __aenter__(self) -> Dict[Str, Any]:
        state = await super().__aenter__()
        return state | {
            "dataset_bucket": self.storage_client.bucket("dvc-dataset-v2"),
            "genai_client": self.genai_client
        }

server = BackendServer()
app: FastAPI = server.app


if __name__ == '__main__':
    sys.exit(server.run())
