from datetime import datetime

from pydantic import BaseModel


class ChatReadStatusBase(BaseModel):
    pass


class ChatReadStatusRead(ChatReadStatusBase):
    chat_id: int
    user_id: int
    last_read_message_id: int
    read_at: datetime

    async def to_json(self):
        return self.model_dump(mode='json')


class ChatReadStatusCreate(ChatReadStatusBase):
    pass


class ChatReadStatusUpdate(ChatReadStatusBase):
    chat_id: int
    message_id: int
