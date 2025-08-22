from pydantic import BaseModel


class CompanyUpdateRequest(BaseModel):
    memorandum: str | None = None