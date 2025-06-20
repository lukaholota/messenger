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


class MessageCreate(MessageBase):
    chat_id: int
    content: str
    user_id: int | None = None


class MessageUpdate(MessageBase):
    pass
