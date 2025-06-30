from typing import List

from starlette.websockets import WebSocket

from app.db.repository.chat_repository import ChatRepository

from logging import getLogger

from app.models import Message, Chat
from app.schemas.chat import ChatOverview
from app.schemas.chat_read_status import ChatReadStatusRead, \
    ChatReadStatusUpdate
from app.schemas.event import UndeliveredMessagesSentEvent
from app.schemas.message import MessageRead, MessageCreate
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
            message_delivery_service: MessageDeliveryService,
            message_handler: MessageWebSocketHandler,
            chat_repository: ChatRepository,

    ):
        self.websocket = websocket
        self.event_sender = EventSender(websocket)
        self.subscription_service = subscription_service
        self.message_handler = message_handler
        self.chat_repository = chat_repository
        self.message_delivery_service = message_delivery_service
        self.redis_dispatcher = ChatRedisEventDispatcher()
        self.websocket_dispatcher = ChatWebSocketEventDispatcher()
        self.websocket_event_handler = WebSocketEventHandler(
            message_handler=self.message_handler,
            chat_read_service=chat_read_service,
        )
        self.redis_event_handler = RedisEventHandler(
            websocket=self.websocket,
            event_sender=self.event_sender,
        )

    async def start(self, user_id: int):
        await self.register_handlers()

        chats = await chat_service

        await self.handle_reconnect(user_id)

        chat_ids = await self.chat_repository.get_user_chat_ids(user_id)
        await self.subscription_service.subscribe_to_every_chat(
            user_id,
            chat_ids,
            callback=self.redis_dispatcher.dispatch
        )

    async def register_handlers(self):
        await self.redis_dispatcher.register(
            event='message_sent',
            dto_class=MessageRead,
            handler=self.redis_event_handler.handle_message_sent
        )
        await self.redis_dispatcher.register(
            event='read_status_updated',
            dto_class=ChatReadStatusRead,
            handler=self.redis_event_handler.handle_read_status_updated
        )

        await self.websocket_dispatcher.register(
            event='new_message',
            dto_class=MessageCreate,
            handler=self.websocket_event_handler.handle_new_message
        )
        await self.websocket_dispatcher.register(
            event='read_message',
            dto_class=ChatReadStatusUpdate,
            handler=self.websocket_event_handler.handle_read_message
        )

    async def handle_reconnect(self, user_id: int, chats: list[Chat]):
        undelivered_messages = await (
            self.message_delivery_service
            .mark_messages_delivered(user_id)
        )
        await self.send_undelivered_messages(undelivered_messages)

    async def send_undelivered_messages(self, messages: list[Message]):
        message_schemas = [
            MessageRead.model_validate(message)
            for message in messages
        ]

        event = UndeliveredMessagesSentEvent(data=message_schemas)

        await self.event_sender.send_event(event)

    async def prepare_chat_list_on_reconnect(
            self, user_id: int, chats: list[Chat]
    ) -> List[ChatOverview]:



    async def stop(self):
        await self.subscription_service.cleanup()
