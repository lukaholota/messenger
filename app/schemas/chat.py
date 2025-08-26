from pydantic import BaseModel

from app.models import Chat
from app.schemas.message import MessageRead, MessageInChatOverview
from app.schemas.user import UserRead


class ChatBase(BaseModel):
    chat_name: str | None = None
    is_group: bool | None = None


class ChatCreate(ChatBase):
    participant_ids: list[int]
    is_group: bool


class ChatUpdate(ChatBase):
    chat_id: int
    name: str


class ChatRead(ChatBase):
    chat_id: int
    chat_name: str
    is_group: bool
    participants: list[UserRead]

    class Config:
        from_attributes = True


class ChatWithDetails(ChatBase):
    chat_name: str
    is_group: bool
    participants: list[UserRead]
    messages: list[MessageRead]

    class Config:
        from_attributes = True


class ChatUpdateRead(ChatBase):
    chat_id: int
    chat_name: str


class ChatAddParticipants(BaseModel):
    chat_id: int
    participant_ids: list[int]


class ChatOverview(BaseModel):
    chat_id: int
    chat_name: str
    last_message: MessageInChatOverview | None
    unread_count: int

class ChatInfo(BaseModel):
    chat_id: int
    chat_name: str
    is_group: bool
    participants: list[UserRead]
    participant_count: int

class ChatWithName(BaseModel):
    chat: Chat
    chat_name: str

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class StartNewChatIn(BaseModel):
    target_user_id: int
    content: str
