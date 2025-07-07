from jose import ExpiredSignatureError

from app.core.security import decode_jwt_token
from app.infrastructure.exceptions.exceptions import InvalidAccessTokenException
from app.infrastructure.cache.redis_cache import RedisCache
from app.infrastructure.exceptions.websocket import WebSocketException
from app.schemas.token import TokenPayload
from app.services.redis_token_blacklist_service import \
    RedisTokenBlacklistService

from logging import getLogger

from app.services.user.user_query_service import UserQueryService

logger = getLogger(__name__)

async def get_current_user_id_ws(
        token: str,
        user_query_service: UserQueryService,
        redis_token_blacklist_service: RedisTokenBlacklistService,
        redis: RedisCache,
) -> int:
    token_payload = await get_access_token_payload(token)

    if await redis_token_blacklist_service.is_blacklisted(token_payload.jti):
        raise WebSocketException('this access token is blacklisted')

    redis_key = f'auth:{token_payload.jti}'
    cached_user_id = await redis.get(redis_key)
    if cached_user_id:
        return int(cached_user_id)

    user = await user_query_service.get_user_by_id(int(token_payload.user_id))
    if not user:
        raise WebSocketException('user not found')
    if user.deleted_at:
        raise WebSocketException('user has been deleted')

    await redis.set(redis_key, user.user_id)
    return user.user_id


async def get_access_token_payload(
        token: str
) -> TokenPayload:
    try:
        token_data = decode_jwt_token(token)
        if (not token_data.user_id or not token_data.token_type
                or not token_data.jti or not token_data.expires_at):
            raise InvalidAccessTokenException
        return token_data
    except ExpiredSignatureError as e:
        raise WebSocketException('Access token expired') from e
    except Exception as e:
        logger.error(f'error decoding access token: {e}', exc_info=e)
        raise WebSocketException('Access token decoding error') from e
