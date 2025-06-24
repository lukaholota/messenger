from starlette.websockets import WebSocket

from app.db.repository.chat_repository import ChatRepository

from logging import getLogger

from app.schemas.chat_read_status import ChatReadStatusRead, \
    ChatReadStatusUpdate
from app.schemas.message import MessageRead, MessageCreate
from app.services.ws.chat_read_service import ChatReadService
from app.services.ws.dispatchers.websocket_event_dispatcher import \
    ChatWebSocketEventDispatcher
from app.services.ws.dispatchers.redis_event_dispatcher import (
    ChatRedisEventDispatcher)
from app.services.ws.chat_web_socket_connection_manager import \
    ChatWebSocketConnectionManager
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
            connection_manager: ChatWebSocketConnectionManager,
            subscription_service: RedisChatSubscriptionService,
            chat_read_service: ChatReadService,
            message_handler: MessageWebSocketHandler,
            chat_repository: ChatRepository,
    ):
        self.websocket = websocket
        self.connection_manager = connection_manager
        self.subscription_service = subscription_service
        self.message_handler = message_handler
        self.chat_repository = chat_repository
        self.redis_dispatcher = ChatRedisEventDispatcher()
        self.websocket_dispatcher = ChatWebSocketEventDispatcher()
        self.websocket_event_handler = WebSocketEventHandler(
            message_handler=self.message_handler,
            chat_read_service=chat_read_service,
        )
        self.redis_event_handler = RedisEventHandler(
            websocket=self.websocket,
            connection_manager=self.connection_manager,
        )

    async def start(self, user_id: int):
        await self.connection_manager.connect(user_id, self.websocket)
        await self.register_handlers()

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

    async def send_all_unread_messages(self):


    async def stop(self, user_id):
        await self.connection_manager.disconnect(user_id, self.websocket)
        await self.subscription_service.cleanup()
        await self.websocket.close()
