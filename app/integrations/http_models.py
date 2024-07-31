from pydantic import BaseModel, EmailStr
from ..foundation import models


class SyncDealRequest(BaseModel):
    user_email: EmailStr
    startup: models.Startup
    features: dict[str, models.Feature]
    people: list[models.Person]
    sources: dict[str, models.Source]


class SyncDealResponse(BaseModel):
    success: bool
