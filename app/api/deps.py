from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_jwt_token
from app.db.repository.chat_repository import ChatRepository
from app.db.repository.message_repository import MessageRepository
from app.db.repository.refresh_token_repository import RefreshTokenRepository
from app.db.repository.scheduled_message_repository import \
    ScheduledMessageRepository
from app.db.repository.user_repository import UserRepository
from app.db.session import get_db_session
from app.exceptions import InvalidAccessTokenException, DeletedUserError, \
    RedisConnectionError, TokenInvalidatedError
from app.infrastructure.cache.json_serializer import JsonSerializer
from app.infrastructure.cache.redis_cache import RedisCache
from app.models import User, Chat, Message
from app.models.scheduled_message import ScheduledMessage
from app.schemas.token import TokenPayload
from app.services.auth_service import AuthService
from app.services.chat_service import ChatService
from app.services.message_service import MessageService
from app.services.cache_token_blacklist_service import \
    CacheTokenBlacklistService
from app.services.scheduled_message_service import ScheduledMessageService
from app.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/token')


async def get_cache(request: Request) -> RedisCache:
    if (
            not hasattr(request.app.state, 'redis_client') or
            request.app.state.redis_client is None
    ):
        raise RedisConnectionError
    return RedisCache(
        request.app.state.redis_client,
        serializer=JsonSerializer()
    )


async def get_user_repository(
        db: AsyncSession = Depends(get_db_session),
) -> UserRepository:
    user_repository = UserRepository(db, User)
    return user_repository


async def get_chat_repository(
        db: AsyncSession = Depends(get_db_session),
) -> ChatRepository:
    chat_repository = ChatRepository(db, Chat)
    return chat_repository


async def get_message_repository(
        db: AsyncSession = Depends(get_db_session)
) -> MessageRepository:
    message_repository = MessageRepository(db, Message)
    return message_repository


async def get_scheduled_message_repository(
        db: AsyncSession = Depends(get_db_session)
) -> ScheduledMessageRepository:
    scheduled_message_repository = ScheduledMessageRepository(
        db,
        ScheduledMessage
    )
    return scheduled_message_repository


async def get_refresh_token_repository(
        db: AsyncSession = Depends(get_db_session)
) -> RefreshTokenRepository:
    refresh_token_repository = RefreshTokenRepository(db)
    return refresh_token_repository


async def get_cache_token_blacklist_service(
        cache: RedisCache = Depends(get_cache),
):
    cache_token_blacklist_service = CacheTokenBlacklistService(
        cache=cache
    )
    return cache_token_blacklist_service


async def get_access_token_payload(
        token: str = Depends(oauth2_scheme)
) -> TokenPayload:
    token_data = decode_jwt_token(token)
    if (not token_data.user_id or not token_data.token_type
            or not token_data.jti or not token_data.expires_at):
        raise InvalidAccessTokenException
    return token_data


async def get_current_user_id(
        user_repository: UserRepository = Depends(get_user_repository),
        cache_token_blacklist_service: CacheTokenBlacklistService = (
                Depends(get_cache_token_blacklist_service)
        ),
        token_data: TokenPayload = Depends(get_access_token_payload),
        cache: RedisCache = Depends(get_cache),
) -> int:
    if await cache_token_blacklist_service.is_blacklisted(token_data.jti):
        raise TokenInvalidatedError

    cache_key = f'auth:{token_data.jti}'
    cached_user_id = await cache.get(cache_key)
    if cached_user_id:
        return int(cached_user_id)

    user = await user_repository.get_by_id(token_data.user_id)
    if not user:
        raise InvalidAccessTokenException
    if user.deleted_at:
        raise DeletedUserError

    await cache.set(cache_key, user.user_id)
    return user.user_id


async def get_current_user_db_bound(
        user_repository: UserRepository = Depends(get_user_repository),
        cache_token_blacklist_service: CacheTokenBlacklistService = (
                Depends(get_cache_token_blacklist_service)
        ),
        token_data: TokenPayload = Depends(get_access_token_payload)
) -> User:
    if await cache_token_blacklist_service.is_blacklisted(token_data.jti):
        raise TokenInvalidatedError

    user = await user_repository.get_by_id(token_data.user_id)
    if not user:
        raise InvalidAccessTokenException
    if user.deleted_at:
        raise DeletedUserError
    return user


async def get_user_service(
        db: AsyncSession = Depends(get_db_session),
        user_repository: UserRepository = Depends(get_user_repository),
        chat_repository: ChatRepository = Depends(get_chat_repository),
        refresh_token_repository: RefreshTokenRepository = (
                Depends(get_refresh_token_repository)
        ),
        current_user: User = Depends(get_current_user_db_bound),
) -> UserService:
    return UserService(
        db=db,
        user_repository=user_repository,
        chat_repository=chat_repository,
        refresh_token_repository=refresh_token_repository,
        current_user=current_user
    )


async def get_user_service_for_token_operations(
        db: AsyncSession = Depends(get_db_session),
        user_repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(
        db=db,
        user_repository=user_repository
    )


async def get_chat_service(
        db: AsyncSession = Depends(get_db_session),
        chat_repository: ChatRepository = Depends(get_chat_repository),
        user_repository: UserRepository = Depends(get_user_repository),
        current_user_id: int = Depends(get_current_user_id),
        cache: RedisCache = Depends(get_cache)
) -> ChatService:
    chat_service = ChatService(
        db=db,
        chat_repository=chat_repository,
        user_repository=user_repository,
        current_user_id=current_user_id,
        cache=cache
    )
    return chat_service


async def get_message_service(
        db: AsyncSession = Depends(get_db_session),
        message_repository = Depends(get_message_repository),
        chat_repository: ChatRepository = Depends(get_chat_repository),
        current_user_id: int = Depends(get_current_user_id),
        cache: RedisCache = Depends(get_cache)
) -> MessageService:
    message_service = MessageService(
        db,
        message_repository=message_repository,
        chat_repository=chat_repository,
        current_user_id=current_user_id,
        cache=cache
    )
    return message_service


async def get_scheduled_message_service(
        db: AsyncSession = Depends(get_db_session),
        scheduled_message_repository = Depends(
            get_scheduled_message_repository
        ),
        chat_repository: ChatRepository = Depends(get_chat_repository),
        current_user_id: int = Depends(get_current_user_id)
) -> ScheduledMessageService:
    scheduled_message_service = ScheduledMessageService(
        db,
        scheduled_message_repository=scheduled_message_repository,
        chat_repository=chat_repository,
        current_user_id=current_user_id,
    )
    return scheduled_message_service


async def get_auth_service(
        db: AsyncSession = Depends(get_db_session),
        refresh_token_repository: RefreshTokenRepository =
        Depends(get_refresh_token_repository),
        cache_token_blacklist_service = Depends(
            get_cache_token_blacklist_service
        ),
) -> AuthService:
    auth_service = AuthService(
        db=db,
        refresh_token_repository=refresh_token_repository,
        cache_token_blacklist_service=cache_token_blacklist_service
    )
    return auth_service
