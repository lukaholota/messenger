from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class tokenData(BaseModel):
    username: str | None = None
    