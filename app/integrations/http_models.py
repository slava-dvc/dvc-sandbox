from pydantic import BaseModel
from ..foundation import models


class SyncDealRequest(BaseModel):
    startup: models.Startup
    features: dict[str, models.Feature]
    sources: dict[str, models.Source]


class SyncDealResponse(BaseModel):
    success: bool

