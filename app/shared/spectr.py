import httpx

from app.foundation import get_env, server
from typing import Dict, Any, List


class SpectrClient(object):

    def __init__(self, logging_client: server.ConsoleLogger, http_client: httpx.AsyncClient):
        self._api_key = str(get_env("SPECTR_API_KEY")).strip()
        self._http_client = http_client
        self._logging_client = logging_client
        self._base_url = "https://app.tryspecter.com/api/v1"

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

        self._logging_client.log_struct(
            {
                'message': f'Spectr request: {method} {url}',
                "rate_limit": rate_limit,
                "credit_limit": credit_limit
            },
            severity="INFO"
        )

        response.raise_for_status()  # Raises detailed HTTP errors (if any)
        return response.json()

    async def get_company_by_id(self, company_id: str) -> Dict[str, Any]:
        """
        Get company information by Specter company ID.
        https://api.tryspecter.com/api-ref/companies/get-company-info-by-id
    
        Args:
            company_id: The Specter ID for the company to retrieve.
    
        Returns:
            A dictionary containing the company information with fields like:
            - id: The Specter ID for the company
            - organization_name: The main public name for the organization
            - organization_rank: The Specter rank for this company
            - primary_role: The primary role of this company
            - roles: Other roles the company may have
            - description: A description of what the company does
            - customer_focus: The type of customers the company deals with
            - last_updated: Date when the company was last updated
            - tags: Tags related to the company
            - industries: List of industries associated with the company
            - sub_industries: List of sub-industries
            - operating_status: Status of the company
            - logo_url: URL to the company logo
            - highlights: All highlights (growth, funding, news, etc.)
            - new_highlights: Highlights new to this month
            - regions: List of regions the company operates in
            - founded_year: Year the company was founded
            - founders: Names of the founders
            - founder_count: Number of founders
            - employee_count: Number of employees
            - employee_count_range: Range of employee count
            - revenue_estimate_usd: Estimated revenue in USD
            - investors: List of investors
            - investor_count: Number of investors
            - patent_count: Number of patents owned
            - trademark_count: Number of trademarks
            - website: Website information
            - hq: HQ location information
            - contact: Contact information
            - ipo: List of IPOs
            - growth_stage: Company's growth stage
            - funding: Funding information
            - web: Web metrics
            - awards: List of awards
            - award_count: Number of awards
            - news: News items about the company
            - reviews: Product reviews
            - socials: Social media information
            - organization_name_aliases: Alternative company names
            - tagline: Company tagline
            - certifications: Industry certifications
            - customer_profile: Typical customer profile
            - traction_highlights: Impact data
            - reported_clients: List of clients
            - acquisition: Acquisition information
            - technologies: Technologies used by the company
            - it_spend: Annual IT spending
            - traction_metrics: Growth trends data
    
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
        return await self.request(method="POST", endpoint=endpoint, json=json_body)
