import httpx
from pydantic import BaseModel
from typing import Optional, Tuple, AnyStr

from app.foundation import get_env
from app.foundation.server.logger import Logger


__all__ = ['ScrapinClient']



class LIAccountPosition(BaseModel):
    position: str | None = None
    description: str | None = None


class LIAccountEducation(BaseModel):
    title: str | None = None
    url: str | None = None
    degree: str | None = None


class LIAccountHonor(BaseModel):
    title: str | None = None
    description: str | None = None


class LIAccountProject(BaseModel):
    title: str | None = None
    url: str | None = None
    description: str | None = None


class LIAccountLicense(BaseModel):
    title: str | None = None
    url: str | None = None
    description: str | None = None


class LIAccountExperience(BaseModel):
    name: str | None = None
    url: str | None = None
    position: list[LIAccountPosition] = None


class LIAccount(BaseModel):
    name: str | None = None
    query: str | None = None
    tagline: str | None = None
    description: str | None = None
    linkedin: str | None = None
    experience: list[LIAccountExperience] = []
    education: list[LIAccountEducation] = []
    licenses: list[LIAccountLicense] = []
    projects: list[LIAccountProject] = []
    honors: list[LIAccountHonor] = []


class LICompany(BaseModel):
    name: str | None = None
    tagline: str | None = None
    description: str | None = None
    website: str | None = None
    employees: list[LIAccount] = []
    employees_count: int = 0
    industry: str | None = None
    headquarters: str | None = None
    founded_year: int | None = None
    stage:  str | None = None


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

    async def search_company(self, domain: str) -> Tuple[LICompany, AnyStr]:
        domain = domain.replace('http://', '').replace('https://', '').replace('www.', '')
        data = await self.request("GET", "/enrichment/company/domain", params={"domain": domain})
        return self._parse_company_data(data.get('company')) if data else (None, None)

    async def extract_company_data(self, linkedin_url: str) -> Tuple[LICompany, AnyStr]:
        data = await self.request("GET", "/enrichment/company", params={"linkedInUrl": linkedin_url})
        return self._parse_company_data(data.get('company')) if data else (None, None)

    async def extract_person_data(self, linkedin_url: str) -> Tuple[LIAccount, AnyStr]:
        data = await self.request("GET", "/enrichment/profile", params={"linkedInUrl": linkedin_url})
        return self._parse_person_data(data.get('person')) if data else (None, None)

    async def search_person(self, **kwargs) -> Tuple[LIAccount, AnyStr]:
        valid_params = ['firstName', 'lastName', 'companyDomain', 'email']
        params = {k: v for k, v in kwargs.items() if k in valid_params and v is not None}
        if params.get('companyDomain'):
            params['companyDomain'] = params['companyDomain'].replace('http://', '').replace('https://', '').replace('www.', '').strip('/')
        data = await self.request("GET", "/enrichment", params=params)
        return self._parse_person_data(data.get('person')) if data else (None, None)

    def _parse_company_data(self, data: dict) -> Tuple[LICompany, AnyStr]:
        if not data:
            return None, None
        headquarter = data.get('headquarter') or {}
        founded_on = data.get('foundedOn') or {}
        hq = None
        if isinstance(headquarter, dict):
            parts = [headquarter.get(f) for f in ['city', 'geographicArea', 'country'] if headquarter.get(f)]
            if parts:
                hq = ', '.join(parts)
        elif isinstance(headquarter, str):
            hq = headquarter
        else:
            self._logger.warning(f"Invalid headquarter data: {headquarter} ({type(headquarter)})")

        return LICompany(
            name=data.get('name'),
            tagline=data.get('tagline'),
            description=data.get('description'),
            website=data.get('websiteUrl'),
            employees_count=data.get('employeeCount'),
            industry=data.get('industry'),
            headquarters=hq if headquarter else None,
            founded_year=founded_on.get('year') if founded_on else None,
            stage=None,
        ), data.get('linkedInUrl')

    def _parse_person_data(self, data: dict) -> Tuple[LIAccount, AnyStr]:
        if not data:
            return None, None
        experience = [
            LIAccountExperience(
                name=pos['companyName'],
                url=pos['linkedInUrl'],
                position=[LIAccountPosition(position=pos['title'], description=pos['description'])]
            )
            for pos in data.get('positions', {}).get('positionHistory', [])
        ]

        education = [
            LIAccountEducation(
                title=edu['schoolName'],
                url=edu['linkedInUrl'],
                degree=edu['degreeName']
            )
            for edu in data.get('schools', {}).get('educationHistory', [])
        ]

        return LIAccount(
            name=f"{data['firstName']} {data['lastName']}",
            query=data.get('publicIdentifier'),
            tagline=data.get('headline'),
            description=data.get('summary'),
            linkedin=data.get('linkedInUrl'),
            experience=experience,
            education=education,
            # Note: licenses, projects, and honors are not provided in the API response
        ), data.get('linkedInUrl')
