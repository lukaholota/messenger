from datetime import datetime

from pydantic import BaseModel


class MessageBase(BaseModel):
    pass


class MessageRead(MessageBase):
    message_id: int
    content: str
    sent_at: datetime
    user_id: int
    chat_id: int

    class Config:
        from_attributes = True


class MessageInChatOverview(MessageBase):
    sent_at: datetime
    content: str
    display_name: str


class MessageCreate(MessageBase):
    chat_id: int
    content: str
    user_id: int | None = None


class MessageUpdate(MessageBase):
    pass


class ChatMessage(BaseModel):
    message_id: int
    chat_id: int
    user_id: int
    is_read: bool = False
    read_at_list: list[dict[int, datetime | None]] | None = None
    display_name: str
    content: str
    sent_at: datetime

