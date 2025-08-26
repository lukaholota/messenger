from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository.chat_read_status_repository import \
    ChatReadStatusRepository
from app.db.repository.chat_repository import ChatRepository
from app.db.repository.contact_repository import ContactRepository
from app.db.repository.message_delivery_repository import \
    MessageDeliveryRepository
from app.db.repository.message_repository import MessageRepository
from app.db.repository.user_repository import UserRepository
from app.infrastructure.cache.json_serializer import JsonSerializer
from app.infrastructure.cache.redis_cache import RedisCache
from app.infrastructure.cache.redis_pubsub import RedisPubSub
from app.infrastructure.message_queue.rabbitmq_client import RabbitMQClient
from app.models import User, Chat, MessageDelivery, Message, Contact
from app.models.chat_read_status import ChatReadStatus
from app.services.chat.chat_create_helper import ChatCreateHelper
from app.services.chat.chat_info_service import ChatInfoService
from app.services.chat.chat_query_service import ChatQueryService
from app.services.chat.chat_service import ChatService
from app.services.chat_overview_service import ChatOverviewService
from app.services.contact.contact_service import ContactService
from app.services.message.chat_messages_constructor import \
    ChatMessagesConstructor
from app.services.message.message_query_service import MessageQueryService
from app.services.message_delivery_service import MessageDeliveryService
from app.services.redis_token_blacklist_service import \
    RedisTokenBlacklistService
from app.services.search.search_service import SearchService
from app.services.user.user_query_service import UserQueryService
from app.services.ws.chat_read_service import ChatReadService
from app.services.ws.dispatchers.redis_event_dispatcher import \
    ChatRedisEventDispatcher
from app.services.ws.message_web_socket_handler import MessageWebSocketHandler
from app.services.ws.redis_chat_subscription_service import \
    RedisChatSubscriptionService


class WebSocketServiceContainer:
    def __init__(self, db: AsyncSession, redis_client: Redis):
        self.db = db
        self.redis_client = redis_client
        self.redis = RedisCache(redis_client, JsonSerializer())
        self.pubsub = RedisPubSub(redis_client)
        self.mq_client = RabbitMQClient()

        self.user_repository = UserRepository(db, User)
        self.chat_repository = ChatRepository(db, Chat)
        self.message_repository = MessageRepository(db, Message)
        self.chat_read_status_repository = ChatReadStatusRepository(
            db, ChatReadStatus
        )
        self.message_delivery_repository = MessageDeliveryRepository(
            db, MessageDelivery
        )
        self.contact_repository = ContactRepository(
            db, Contact
        )
        self.redis_token_blacklist_service = RedisTokenBlacklistService(
            self.redis
        )
        self.message_delivery_service = MessageDeliveryService(
            db, self.message_delivery_repository
        )
        self.chat_query_service = ChatQueryService(self.chat_repository)
        self.message_query_service = MessageQueryService(
            self.message_repository
        )
        self.chat_message_constructor = ChatMessagesConstructor(
            message_query_service=self.message_query_service,
        )
        self.user_query_service = UserQueryService(self.user_repository)
        self.chat_overview_service = ChatOverviewService(
            self.message_delivery_service,
            self.message_query_service
        )
        self.message_websocket_handler = MessageWebSocketHandler(
            self.mq_client
        )
        self.chat_read_service = ChatReadService(
            db=self.db,
            chat_read_status_repository=self.chat_read_status_repository,
            message_delivery_service=self.message_delivery_service,
            pubsub=self.pubsub
        )
        self.chat_info_service = ChatInfoService(
            chat_query_service=self.chat_query_service,
        )
        self.chat_service = ChatService(
            db=self.db,
            user_repository=self.user_repository,
            chat_repository=self.chat_repository,
            chat_read_status_repository=self.chat_read_status_repository,
            redis=self.redis
        )
        self.search_service = SearchService(
            user_repository=self.user_repository,
        )
        self.redis_event_dispatcher = ChatRedisEventDispatcher()
        self.redis_chat_subscription_service = RedisChatSubscriptionService(
            pubsub=self.pubsub,
            dispatch=self.redis_event_dispatcher.dispatch
        )
        self.chat_create_helper = ChatCreateHelper(
            pubsub=self.pubsub,
            chat_service=self.chat_service,
            chat_info_service=self.chat_info_service
        )
        self.contact_service = ContactService(
            contact_repository=self.contact_repository,
            user_repository=self.user_repository
        )
