from fastapi import APIRouter
from fastapi.params import Depends
from fastapi_limiter.depends import RateLimiter

from app.api.deps import get_message_service, get_redis
from app.infrastructure.cache.redis_cache import RedisCache

from app.schemas.message import MessageRead, MessageCreate
from app.services.message.message_service import MessageService

router = APIRouter()


@router.post(
    '/send-message',
    response_model=MessageRead,
    dependencies=[Depends(RateLimiter(times=60, seconds=60))],
)
async def send_message(
        message_in: MessageCreate,
        message_service: MessageService = Depends(get_message_service),
        redis: RedisCache = Depends(get_redis),
):
    redis_key = f'chat:{message_in.chat_id}:*'
    new_message = await message_service.create_message(message_in)
    await redis.delete_pattern(redis_key)
    return new_message
