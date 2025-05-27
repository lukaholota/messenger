from contextlib import asynccontextmanager

import redis.asyncio as redis

from app.core.config import settings
from logging import getLogger

logger = getLogger(__name__)

REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT
REDIS_PASSWORD = settings.REDIS_PASSWORD


async def get_redis_client() -> redis.Redis:
    try:
        redis_client = redis.StrictRedis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True,
        )
        await redis_client.ping()

        logger.info('Redis connection established!')

        return redis_client
    except redis.ConnectionError as e:
        logger.error(f"Failed to establish Redis connection at "
                     f"{REDIS_HOST}:{REDIS_PORT} -> {e}")
        raise


@asynccontextmanager
async def get_lifespan_redis_client():
    redis = await get_redis_client()
    try:
        yield redis
    finally:
        pass
