import json

from starlette.websockets import WebSocket

from app.db.repository.chat_repository import ChatRepository
from app.schemas.message import MessageCreate, MessageRead

from logging import getLogger

from app.services.ws.chat_web_socket_connection_manager import \
    ChatWebSocketConnectionManager
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
            message_handler: MessageWebSocketHandler,
            chat_repository: ChatRepository,
    ):
        self.websocket = websocket
        self.connection_manager = connection_manager
        self.subscription_service = subscription_service
        self.message_handler = message_handler
        self.chat_repository = chat_repository

    async def start(self, user_id: int):
        await self.connection_manager.connect(user_id, self.websocket)

        chat_ids = await self.chat_repository.get_user_chat_ids(user_id)
        await self.subscription_service.subscribe_to_every_chat(
            user_id,
            chat_ids,
            callback=self._on_redis_message
        )

    async def _on_redis_message(self, data: str):
        json_data = json.loads(data)
        message = await MessageRead(**json_data['message_data']).to_json()

        await self.connection_manager.send_message_to_user(message)

    async def stop(self, user_id):
        await self.connection_manager.disconnect(user_id, self.websocket)
        await self.subscription_service.cleanup()
        await self.websocket.close()

    async def handle_message(self, user_id: int, message_in: MessageCreate):
        await self.message_handler.send_to_mq(user_id, message_in)
