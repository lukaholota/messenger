from typing import Literal, Union

from pydantic import BaseModel, Field

from app.infrastructure.types.event import ServerToClientEvent
from app.schemas.chat_read_status import ChatReadStatusRead
from app.schemas.message import MessageRead


class WebSocketEvent(BaseModel):
    event: str
    data: dict

class RedisEvent(BaseModel):
    event: str
    data: dict

class ReadStatusUpdatedEvent(BaseModel):
    event: Literal[ServerToClientEvent.READ_STATUS_UPDATED] = Field(
        default=ServerToClientEvent.READ_STATUS_UPDATED,
    )
    data: ChatReadStatusRead

class MessageSentEvent(BaseModel):
    event: Literal[ServerToClientEvent.MESSAGE_SENT] = Field(
        default=ServerToClientEvent.MESSAGE_SENT,
    )
    data: MessageRead

class UndeliveredMessagesSentEvent(BaseModel):
    event: Literal[ServerToClientEvent.UNDELIVERED_MESSAGES_SENT] = Field(
        default=ServerToClientEvent.UNDELIVERED_MESSAGES_SENT,
    )
    data: list[MessageRead]


ServerEvent: type = Union[
    ReadStatusUpdatedEvent,
    MessageSentEvent,
    UndeliveredMessagesSentEvent
]
