from pydantic import BaseModel

class User(BaseModel):
    name: str | None = None
    email: str | None = None
    picture: str | None = None
