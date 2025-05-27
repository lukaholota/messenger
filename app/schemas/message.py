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

    async def to_json(self):
        return self.model_dump(mode='json')

    class Config:
        from_attributes = True


class MessageCreate(MessageBase):
    chat_id: int
    content: str


class MessageUpdate(MessageBase):
    pass
