import httpx
from google.cloud import firestore

from ..foundation.server import AppConfig


__all__ = ['lifespan_objects', 'LifespanObjects']


class LifespanObjects(object):

    def __init__(self):
        self.http_client = httpx.AsyncClient(transport=httpx.AsyncHTTPTransport(retries=3), timeout=httpx.Timeout(60))
        self.firestore_client = firestore.AsyncClient()
        self.config = AppConfig()

    async def __aenter__(self):
        await self.http_client.__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.__aexit__()

    async def __call__(self):
        return self


lifespan_objects = LifespanObjects()
