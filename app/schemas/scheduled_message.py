from datetime import datetime

from pydantic import BaseModel

class ScheduledMessageBase(BaseModel):
    pass


class ScheduledMessageCreate(ScheduledMessageBase):
    chat_id: int
    content: str
    scheduled_send_at: datetime

    class Config:
        from_attributes = True


class ScheduledMessageRead(ScheduledMessageBase):
    scheduled_message_id: int
    chat_id: int
    user_id: int
    content: str
    status: str
    scheduled_send_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScheduledMessageReadMultiple(ScheduledMessageBase):
    scheduled_messages: list[ScheduledMessageRead]

    class Config:
        from_attributes = True


class ScheduledMessageGet(ScheduledMessageBase):
    chat_id: int


class ScheduledMessageDelete(ScheduledMessageBase):
    chat_id: int
    scheduled_message_id: int


class ScheduledMessageUpdate(ScheduledMessageBase):
    chat_id: int
    scheduled_message_id: int
    content: str
    scheduled_send_at: datetime


class ScheduledMessageUpdateResponse(ScheduledMessageBase):
    old_scheduled_message: ScheduledMessageRead
    new_scheduled_message: ScheduledMessageRead
