from typing import Literal, Union, List

from pydantic import BaseModel, Field

from app.infrastructure.types.event import ServerToClientEvent
from app.schemas.chat import ChatOverview, ChatInfo
from app.schemas.chat_read_status import ChatReadStatusRead
from app.schemas.contact import ContactRead
from app.schemas.message import MessageRead, ChatMessage
from app.schemas.search import SearchOut


class WebSocketEvent(BaseModel):
    event: str
    data: dict | None = None

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
    data: ChatMessage

class UndeliveredMessagesSentEvent(BaseModel):
    event: Literal[ServerToClientEvent.UNDELIVERED_MESSAGES_SENT] = Field(
        default=ServerToClientEvent.UNDELIVERED_MESSAGES_SENT,
    )
    data: list[MessageRead]

class ChatOverviewListSentEvent(BaseModel):
    event: Literal[ServerToClientEvent.CHAT_OVERVIEW_LIST_SENT] = Field(
        default=ServerToClientEvent.CHAT_OVERVIEW_LIST_SENT,
    )
    data: list[ChatOverview]

class GetChatInfoEvent(BaseModel):
    chat_id: int

class GetChatMessagesEvent(BaseModel):
    chat_id: int

class ChatMessagesSentEvent(BaseModel):
    event: Literal[ServerToClientEvent.CHAT_MESSAGES_SENT] = Field(
        default=ServerToClientEvent.CHAT_MESSAGES_SENT,
    )
    data: List[ChatMessage]

class ChatInfoSentEvent(BaseModel):
    event: Literal[ServerToClientEvent.CHAT_INFO_SENT] = Field(
        default=ServerToClientEvent.CHAT_INFO_SENT,
    )
    data: ChatInfo

class ChatCreatedEvent(BaseModel):
    event: Literal[ServerToClientEvent.CHAT_CREATED] = Field(
        default=ServerToClientEvent.CHAT_CREATED,
    )
    data: ChatInfo

class SearchResultSentEvent(BaseModel):
    event: Literal[ServerToClientEvent.SEARCH_RESULT_SENT] = Field(
        default=ServerToClientEvent.SEARCH_RESULT_SENT,
    )
    data: SearchOut

class NewChatSentEvent(BaseModel):
    event: Literal[ServerToClientEvent.NEW_CHAT_SENT] = Field(
        default=ServerToClientEvent.NEW_CHAT_SENT
    )
    data: ChatOverview

class AddedToContactsEvent(BaseModel):
    event: Literal[ServerToClientEvent.ADDED_TO_CONTACTS] = Field(
        default=ServerToClientEvent.ADDED_TO_CONTACTS
    )
    data: ContactRead

class ContactsSentEvent(BaseModel):
    event: Literal[ServerToClientEvent.CONTACTS_SENT] = Field(
        default=ServerToClientEvent.CONTACTS_SENT
    )
    data: list[ContactRead]

ServerEvent: type = Union[
    ReadStatusUpdatedEvent,
    MessageSentEvent,
    UndeliveredMessagesSentEvent,
    ChatOverviewListSentEvent,
    ChatInfoSentEvent,
    ChatMessagesSentEvent,
    ChatCreatedEvent,
    SearchResultSentEvent,
    NewChatSentEvent,
    AddedToContactsEvent,
    ContactsSentEvent
]
