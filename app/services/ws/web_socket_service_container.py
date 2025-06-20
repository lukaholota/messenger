from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository.chat_read_status_repository import \
    ChatReadStatusRepository
from app.db.repository.chat_repository import ChatRepository
from app.db.repository.user_repository import UserRepository
from app.infrastructure.cache.json_serializer import JsonSerializer
from app.infrastructure.cache.redis_cache import RedisCache
from app.infrastructure.cache.redis_pubsub import RedisPubSub
from app.infrastructure.message_queue.rabbitmq_client import RabbitMQClient
from app.models import User, Chat
from app.models.chat_read_status import ChatReadStatus
from app.services.redis_token_blacklist_service import \
    RedisTokenBlacklistService
from app.services.ws.chat_read_service import ChatReadService
from app.services.ws.chat_web_socket_connection_manager import \
    ChatWebSocketConnectionManager
from app.services.ws.message_web_socket_handler import MessageWebSocketHandler
from app.services.ws.redis_chat_subscription_service import \
    RedisChatSubscriptionService


class WebSocketServiceContainer:
    def __init__(
            self,
            db: AsyncSession,
            redis_client: Redis,
    ):
        self.db = db
        self.redis_client = redis_client
        self.redis = RedisCache(redis_client, JsonSerializer())
        self.pubsub = RedisPubSub(redis_client)
        self.mq_client = RabbitMQClient()
        self.user_repository = UserRepository(db, User)
        self.chat_repository = ChatRepository(db, Chat)
        self.chat_read_status_repository = ChatReadStatusRepository(
            db, ChatReadStatus
        )

    async def get_redis_token_blacklist_service(self):
        return RedisTokenBlacklistService(self.redis)

    async def get_message_websocket_handler(self):
        return MessageWebSocketHandler(self.mq_client)

    async def get_redis_chat_subscription_service(self):
        return RedisChatSubscriptionService(self.pubsub)

    async def get_chat_websocket_connection_manager(self):
        return ChatWebSocketConnectionManager()

    async def get_chat_read_service(self):
        return ChatReadService(
            db=self.db,
            chat_read_status_repository=self.chat_read_status_repository,
            pubsub=self.pubsub,
        )
