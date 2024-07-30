from pydantic import BaseModel, EmailStr
from ..foundation import models


class SyncDealRequest(BaseModel):
    user_email: EmailStr
    startup: models.Startup
    features: dict[str, models.Feature]
    sources: dict[str, models.Source]


class SyncDealResponse(BaseModel):
    success: bool
