from typing import List

from starlette.websockets import WebSocket

from logging import getLogger

from app.infrastructure.types.event import ServerToClientEvent, \
    ClientToServerEvent
from app.models import Message
from app.schemas.chat import ChatOverview, ChatWithName
from app.schemas.chat_read_status import ChatReadStatusRead, \
    ChatReadStatusUpdate
from app.schemas.event import UndeliveredMessagesSentEvent, \
    ChatOverviewListSentEvent, GetChatInfoEvent, GetChatMessagesEvent
from app.schemas.message import MessageRead, MessageCreate, ChatMessage
from app.services.chat.chat_info_service import ChatInfoService
from app.services.chat.chat_query_service import ChatQueryService
from app.services.chat_overview_service import ChatOverviewService
from app.services.message.chat_messages_constructor import \
    ChatMessagesConstructor
from app.services.message_delivery_service import MessageDeliveryService
from app.services.ws.chat_read_service import ChatReadService
from app.services.ws.dispatchers.websocket_event_dispatcher import \
    ChatWebSocketEventDispatcher
from app.services.ws.dispatchers.redis_event_dispatcher import (
    ChatRedisEventDispatcher)
from app.services.ws.event_sender import \
    EventSender
from app.services.ws.handlers.redis_event_handler import RedisEventHandler
from app.services.ws.handlers.web_socket_event_handler import \
    WebSocketEventHandler
from app.services.ws.message_web_socket_handler import MessageWebSocketHandler
from app.services.ws.redis_chat_subscription_service import \
    RedisChatSubscriptionService

logger = getLogger(__name__)


class ChatWebSocketService:
    def __init__(
            self,
            websocket: WebSocket,
            subscription_service: RedisChatSubscriptionService,
            chat_read_service: ChatReadService,
            chat_query_service: ChatQueryService,
            chat_overview_service: ChatOverviewService,
            message_delivery_service: MessageDeliveryService,
            message_handler: MessageWebSocketHandler,
            chat_info_service: ChatInfoService,
            chat_message_constructor: ChatMessagesConstructor,
    ):
        self.websocket = websocket
        self.event_sender = EventSender(websocket)
        self.subscription_service = subscription_service
        self.message_handler = message_handler
        self.message_delivery_service = message_delivery_service
        self.chat_query_service = chat_query_service
        self.chat_overview_service = chat_overview_service
        self.chat_info_service = chat_info_service
        self.redis_dispatcher = ChatRedisEventDispatcher()
        self.websocket_dispatcher = ChatWebSocketEventDispatcher()
        self.websocket_event_handler = WebSocketEventHandler(
            message_handler=self.message_handler,
            chat_message_constructor = chat_message_constructor,
            chat_read_service=chat_read_service,
            chat_info_service=self.chat_info_service,
            event_sender=self.event_sender
        )
        self.redis_event_handler = RedisEventHandler(
            websocket=self.websocket,
            event_sender=self.event_sender,
        )

    async def start(self, user_id: int):
        await self.register_handlers()

        chats_with_names = await self.chat_query_service.get_chats_for_user(
            user_id
        )
        chat_ids = [chat.chat.chat_id for chat in chats_with_names]

        await self.handle_reconnect(user_id, chats_with_names, chat_ids)

        await self.subscription_service.subscribe_to_every_chat(
            user_id,
            chat_ids,
            callback=self.redis_dispatcher.dispatch
        )

    async def register_handlers(self):
        await self.redis_dispatcher.register(
            event=ServerToClientEvent.MESSAGE_SENT,
            dto_class=ChatMessage,
            handler=self.redis_event_handler.handle_message_sent
        )
        await self.redis_dispatcher.register(
            event=ServerToClientEvent.READ_STATUS_UPDATED,
            dto_class=ChatReadStatusRead,
            handler=self.redis_event_handler.handle_read_status_updated
        )

        await self.websocket_dispatcher.register(
            event=ClientToServerEvent.NEW_MESSAGE,
            dto_class=MessageCreate,
            handler=self.websocket_event_handler.handle_new_message
        )
        await self.websocket_dispatcher.register(
            event=ClientToServerEvent.READ_MESSAGE,
            dto_class=ChatReadStatusUpdate,
            handler=self.websocket_event_handler.handle_read_message
        )
        await self.websocket_dispatcher.register(
            event=ClientToServerEvent.GET_CHAT_INFO,
            dto_class=GetChatInfoEvent,
            handler=self.websocket_event_handler.handle_get_chat_info
        )
        await self.websocket_dispatcher.register(
            event=ClientToServerEvent.GET_CHAT_MESSAGES,
            dto_class=GetChatMessagesEvent,
            handler=self.websocket_event_handler.handle_get_chat_messages
        )

    async def handle_reconnect(
            self, user_id: int, chats: list[ChatWithName], chat_ids: list[int]
    ):
        undelivered_messages = await (
            self.message_delivery_service
            .mark_messages_delivered(user_id)
        )
        await self.send_undelivered_messages(undelivered_messages)

        chat_overview_list = await (
            self.prepare_chat_overview_list_on_reconnect(
                user_id, chats, chat_ids
            )
        )

        print('chat_overview_list: ', chat_overview_list)

        await self.send_chat_overview_list(chat_overview_list)

    async def send_undelivered_messages(self, messages: list[Message]):
        message_schemas = [
            MessageRead.model_validate(message)
            for message in messages
        ]

        event = UndeliveredMessagesSentEvent(data=message_schemas)

        await self.event_sender.send_event(event)

    async def send_chat_overview_list(
            self, chat_overview_list: list[ChatOverview]
    ):
        event = ChatOverviewListSentEvent(data=chat_overview_list)

        await self.event_sender.send_event(event)

    async def prepare_chat_overview_list_on_reconnect(
            self, user_id: int, chats: list[ChatWithName], chat_ids: list[int]
    ) -> List[ChatOverview]:
        return await (
            self.chat_overview_service.get_chat_overview_list(
                user_id, chats, chat_ids
            )
        )

    async def stop(self):
        await self.subscription_service.cleanup()
