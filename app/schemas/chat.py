from pydantic import BaseModel

from app.schemas.user import UserRead


class ChatBase(BaseModel):
    name: str | None = None
    is_group: bool


class ChatCreate(ChatBase):
    participants_ids: list[int]


class ChatUpdate(ChatBase):
    name: str


class ChatRead(ChatBase):
    chat_id: int
    name: str
    is_group: bool
    participants: list[UserRead]

    class Config:
        from_attributes = True
