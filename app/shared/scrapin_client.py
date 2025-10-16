import httpx
from pydantic import BaseModel
from typing import Dict

from app.foundation import get_env
from app.foundation.server.logger import Logger


__all__ = ['ScrapinClient']


class ScrapinClient(object):
    BASE_URL = "https://api.scrapin.io"

    def __init__(
        self,
        logger: Logger,
        http_client: httpx.AsyncClient,
    ):
        self._api_key = str(get_env("SCRAPIN_API_KEY")).strip()
        self._http_client = http_client
        self._logger = logger

    async def request(self, method: str, endpoint: str, **kwargs) -> dict:
        url = f"{self.BASE_URL}{endpoint}"
        params = kwargs.get('params', {})
        params['apikey'] = self._api_key
        kwargs['params'] = params
        
        self._logger.info(f'Scrapin request', labels={
            "scrapin_endpoint": endpoint,
            "params": {k: v for k, v in params.items() if k != 'apikey'}
        })
        
        response = await self._http_client.request(method=method, url=url, **kwargs)
        if response.status_code == httpx.codes.NOT_FOUND:
            return {}
        response.raise_for_status()
        return response.json()

    async def search_company(self, domain: str) -> Dict:
        domain = domain.replace('http://', '').replace('https://', '').replace('www.', '')
        data = await self.request("GET", "/enrichment/company/domain", params={"domain": domain})
        return data.get('company')

    async def extract_company_data(self, linkedin_url: str) -> Dict:
        data = await self.request("GET", "/enrichment/company", params={"linkedInUrl": linkedin_url})
        return data.get('company')

    async def extract_person_data(self, linkedin_url: str) -> Dict:
        data = await self.request("GET", "/enrichment/profile", params={"linkedInUrl": linkedin_url})
        return data.get('person')

    async def search_person(self, **kwargs) -> Dict:
        valid_params = ['firstName', 'lastName', 'companyDomain', 'email']
        params = {k: v for k, v in kwargs.items() if k in valid_params and v is not None}
        if params.get('companyDomain'):
            params['companyDomain'] = params['companyDomain'].replace('http://', '').replace('https://', '').replace('www.', '').strip('/')
        data = await self.request("GET", "/enrichment", params=params)
        return data.get('person')
