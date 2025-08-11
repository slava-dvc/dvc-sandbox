from pydantic import BaseModel, EmailStr
from app.shared import models


class SyncDealRequest(BaseModel):
    user_email: EmailStr
    startup: models.Startup
    people: list[models.Person]
    sources: list[models.Source]


class SyncDealResponse(BaseModel):
    success: bool
