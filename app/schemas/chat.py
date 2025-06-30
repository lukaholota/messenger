from pydantic import BaseModel

from app.schemas.message import MessageRead
from app.schemas.user import UserRead


class ChatBase(BaseModel):
    name: str | None = None
    is_group: bool | None = None


class ChatCreate(ChatBase):
    participant_ids: list[int]
    is_group: bool


class ChatUpdate(ChatBase):
    chat_id: int
    name: str


class ChatRead(ChatBase):
    chat_id: int
    name: str
    is_group: bool
    participants: list[UserRead]

    class Config:
        from_attributes = True


class ChatWithDetails(ChatBase):
    name: str
    is_group: bool
    participants: list[UserRead]
    messages: list[MessageRead]

    class Config:
        from_attributes = True


class ChatUpdateRead(ChatBase):
    chat_id: int
    name: str


class ChatAddParticipants(BaseModel):
    chat_id: int
    participant_ids: list[int]


class ChatOverview(BaseModel):
    chat_id: int
    name: str
    last_message: MessageRead
    unread_count: int
