from typing import Optional, List, Literal, ClassVar, Set

from pydantic import BaseModel
from app.foundation.primitives import datetime


class Company(BaseModel):

    DATA_FIELDS: ClassVar[Set[str]] = {
        "linkedInData", "spectrData",
    }

    _id: str
    airtableId: str
    name: str
    createdAt: datetime.datetime
    updatedAt: datetime.datetime | None

    website: str | None

    linkedInId: str | None = None
    linkedInData: dict | None = None
    linkedInUpdatedAt: datetime.datetime | None = None

    spectrId: str | None
    spectrUpdatedAt: datetime.datetime | None = None
    spectrData: dict | None = None


    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            _id=data['_id'],
            airtableId=data['airtableId'],
            name=data['name'],
            createdAt=datetime.any_to_datetime(data.get('createdAt')),
            updatedAt=datetime.any_to_datetime(data.get('updatedAt')),
            website=data.get('website'),
            linkedInId=data.get('linkedInId'),
            linkedInData=data.get('linkedInData'),
            linkedInUpdatedAt=datetime.any_to_datetime(data.get('linkedInUpdatedAt')),
            spectrId=data.get('spectrId'),
            spectrUpdatedAt=datetime.any_to_datetime(data.get('spectrUpdatedAt')),
            spectrData=data.get('spectrData'),
        )
