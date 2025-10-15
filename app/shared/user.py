from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    picture: Optional[str] = None
