from enum import Enum
from typing import Optional, List
from pydantic import BaseModel


class CompanyUpdateRequest(BaseModel):
    memorandum: Optional[str] = None


class DocumentSourceType(str, Enum):
    PDF = "pdf"
    URL = "url"


class DocumentSource(BaseModel):
    type: DocumentSourceType
    bucket: Optional[str] = None  # For PDF files
    key: Optional[str] = None     # For PDF files  
    url: Optional[str] = None     # For URL sources


class CompanyCreateRequest(BaseModel):
    id: str
    name: str
    email: str
    website: Optional[str] = None
    sources: List[DocumentSource]
    source: Optional[str] = None
    introduced_by: Optional[str] = None