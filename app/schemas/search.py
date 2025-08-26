from pydantic import BaseModel

from app.schemas.user import SearchUser


class SearchIn(BaseModel):
    prompt: str

class SearchOut(BaseModel):
    found_users: list[SearchUser]
