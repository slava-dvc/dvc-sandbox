import httpx
from typing import Dict

from app.foundation import get_env
from app.foundation.server.logger import Logger


__all__ = ['SerpApiClient']


class SerpApiClient(object):
    BASE_URL = "https://serpapi.com"

    def __init__(
        self,
        logger: Logger,
        http_client: httpx.AsyncClient,
    ):
        self._api_key = str(get_env("SERPAPI_API_KEY")).strip()
        self._http_client = http_client
        self._logger = logger

    async def request(self, method: str, engine: str, **kwargs) -> dict:
        url = f"{self.BASE_URL}/search"
        params = kwargs.get('params', {})
        params['api_key'] = self._api_key
        params['engine'] = engine
        kwargs['params'] = params
        
        self._logger.info(f'SerpApi request', labels={
            "serpapi_engine": engine,
            "params": {k: v for k, v in params.items() if k != 'api_key'}
        })
        
        response = await self._http_client.request(method=method, url=url, **kwargs)
        if response.status_code == httpx.codes.NOT_FOUND:
            return {}
        response.raise_for_status()
        return response.json()

    async def search_google_play(self, q: str) -> Dict:
        data = await self.request("GET", "google_play", params={
            "q": q,
            "gl": "us",
            "hl": "en"
        })
        return data

    async def search_apple_app_store(self, term: str, **kwargs) -> Dict:
        params = {
            "term": term,
            "country": "us",
            "device": "mobile",
            "num": "10"
        }
        params.update(kwargs)
        
        data = await self.request("GET", "apple_app_store", params=params)
        return data

    async def get_apple_product(self, product_id: str, **kwargs) -> Dict:
        params = {
            "product_id": product_id,
            "country": "us",
            "type": "app"
        }
        params.update(kwargs)
        
        data = await self.request("GET", "apple_product", params=params)
        return data