import httpx
try:
    from google.cloud import storage
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    storage = None
from app.foundation import get_env, as_async
from app.foundation.server.logger import Logger
from typing import Dict, Any, List


__all__ = ["SpectrClient"]


class SpectrClient(object):

    def __init__(
            self,
            logger: Logger,
            http_client: httpx.AsyncClient,
            dataset_bucket: Any = None,  # storage.Bucket
    ):
        self._api_key = str(get_env("SPECTR_API_KEY")).strip()
        self._http_client = http_client
        self._logger = logger
        self._base_url = "https://app.tryspecter.com/api/v1"
        self._dataset_bucket = dataset_bucket

    async def request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self._base_url}/{endpoint}"
        headers = {"X-API-KEY": self._api_key, "accept": "application/json"}
        kwargs["headers"] = {**headers, **kwargs.get("headers", {})}

        response = await self._http_client.request(method=method, url=url, **kwargs)

        # Process rate limits and credit limits
        rate_limit = {
            "limit": response.headers.get("X-RateLimit-Limit"),
            "remaining": response.headers.get("X-RateLimit-Remaining"),
            "reset": response.headers.get("X-RateLimit-Reset")
        }

        credit_limit = {
            "limit": response.headers.get("X-CreditLimit-Limit"),
            "remaining": response.headers.get("X-CreditLimit-Remaining"),
            "reset": response.headers.get("X-CreditLimit-Reset")
        }
        kwargs.pop("headers", None)
        self._logger.info(f'Spectr request', labels={
            "spectrEndpoint": endpoint,
            "rateLimit": rate_limit,
            "creditLimit": credit_limit,
            'kwargs': kwargs,
        })

        response.raise_for_status()  # Raises detailed HTTP errors (if any)
        company_data = response.json()
        return company_data

    async def get_company_by_id(self, company_id: str) -> Dict[str, Any]:
        """
        Get company information by Specter company ID.
        https://api.tryspecter.com/api-ref/companies/get-company-info-by-id
    
        Args:
            company_id: The Specter ID for the company to retrieve.
    
        Returns:
            A dictionary containing the company information with fields like:
            - id: The Specter ID for the company
    
        Raises:
            HTTPError: For 404 if the company doesn't exist or other HTTP errors.
            RuntimeError: If max retries are exceeded due to rate limits.
        """
        endpoint = f"companies/{company_id}"
        return await self.request(method="GET", endpoint=endpoint)

    async def enrich_companies(
            self,
            website_url: str = None,
            domain: str = None,
            linkedin_url: str = None,
            linkedin_id: str = None,
            crunchbase_url: str = None,
    ) -> List[Dict[str, Any]]:
        """
        Enrich companies using the POST /companies endpoint.
        https://api.tryspecter.com/api-ref/companies
    
        Args:
            website_url: Company website URL (with or without 'http://', 'https://')
            domain: Domain or domain aliases of the company
            linkedin_url: URL of the company's LinkedIn profile
            linkedin_id: The LinkedIn numeric ID for the company
            crunchbase_url: Full URL from Crunchbase
    
        Returns:
            The list of companies that were found in the query
    
        Raises:
            HTTPError: For server-side or client-side HTTP errors.
            ValueError: If the input parameters are invalid or contain multiple properties.
        """
        json_body = {
            key: value for key, value in {
                "website_url": website_url,
                "domain": domain,
                "linkedin_url": linkedin_url,
                "linkedin_id": linkedin_id,
                "crunchbase_url": crunchbase_url
            }.items()
            if value is not None
        }

        if len(json_body) != 1:
            raise ValueError("Exactly one parameter must be provided.")

        endpoint = "companies"
        companies = await self.request(method="POST", endpoint=endpoint, json=json_body)
        return companies
