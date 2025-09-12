from enum import Enum
from pydantic import BaseModel


class CompanyUpdateRequest(BaseModel):
    memorandum: str | None = None


class DocumentSourceType(str, Enum):
    PDF = "pdf"
    URL = "url"


class DocumentSource(BaseModel):
    type: DocumentSourceType
    bucket: str | None = None  # For PDF files
    key: str | None = None     # For PDF files  
    url: str | None = None     # For URL sources


class CompanyCreateRequest(BaseModel):
    id: str
    name: str
    email: str
    website: str | None = None
    sources: list[DocumentSource]