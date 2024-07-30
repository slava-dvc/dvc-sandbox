import httpx
from typing import Dict, Any, List
from pydantic import BaseModel


__all__ = ['AirTableClient', 'Table', 'Field']


class Field(BaseModel):
    id: str
    type: str
    name: str
    description: str | None = None
    options: Dict[str, Any] | None = None


class Table(BaseModel):
    id: str
    name: str
    primaryFieldId: str
    description: str | None = None
    fields: List['Field']
    views: List[Any]


class AirTableClient(object):
    def __init__(self, api_key: str, base_id: str, http_client: httpx.AsyncClient):
        self.api_key = api_key
        self.http_client = http_client
        self.base_id = base_id
        self.base_url = f"https://api.airtable.com/v0"
        self.headers = {"Authorization": f"Bearer {self.api_key.strip()}","Content-Type": "application/json"}

    async def list_records(self, table_name: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Lists records from a table.

        Args:
            table_name: The name of the table.
            **kwargs: Additional query parameters.

        Returns:
            A list of records.
        """
        url = f"{self.base_url}/{self.base_id}/{table_name}"
        response = await self.http_client.get(url, headers=self.headers, params=kwargs)
        response.raise_for_status()
        return response.json()["records"]

    async def get_record(self, table_name: str, record_id: str) -> Dict[str, Any]:
        """
        Gets a single record by ID.

        Args:
            table_name: The name of the table.
            record_id: The ID of the record.

        Returns:
            The record.
        """
        url = f"{self.base_url}/{self.base_id}/{table_name}/{record_id}"
        response = await self.http_client.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    async def create_record(self, table_name: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new record.

        Args:
            table_name: The name of the table.
            fields: The data for the new record.

        Returns:
            The created record.
        """
        url = f"{self.base_url}/{self.base_id}/{table_name}"
        response = await self.http_client.post(url, headers=self.headers, json={"fields": fields})
        response.raise_for_status()
        return response.json()

    async def update_record(self, table_name: str, record_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates an existing record.

        Args:
            table_name: The name of the table.
            record_id: The ID of the record.
            fields: The updated data for the record.

        Returns:
            The updated record.
        """
        url = f"{self.base_url}/{self.base_id}/{table_name}/{record_id}"
        response = await self.http_client.patch(url, headers=self.headers, json={"fields": fields})
        response.raise_for_status()
        return response.json()

    async def get_base_data(self, **kwargs) -> List[Table]:
        """
        Gets the base schema.

        Args:
            **kwargs: Additional query parameters.

        Returns:
            A list of tables with their schemas.
        """
        url = f"{self.base_url}/meta/bases/{self.base_id}/tables"
        response = await self.http_client.get(url, headers=self.headers, params=kwargs)
        response.raise_for_status()
        data = response.json()
        return [Table(**table) for table in data["tables"]]
