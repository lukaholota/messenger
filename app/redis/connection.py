import redis.asyncio as redis
from fastapi import FastAPI

from app.core.config import settings
from logging import getLogger

logger = getLogger(__name__)

REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT
REDIS_PASSWORD = settings.REDIS_PASSWORD


async def add_redis_client_to_app_state(app: FastAPI):
    try:
        redis_client = redis.StrictRedis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True,
        )
        await redis_client.ping()
        app.state.redis_client = redis_client
        logger.info('Redis connection established!')
    except redis.ConnectionError as e:
        logger.error(f"Failed to establish Redis connection at "
                     f"{REDIS_HOST}:{REDIS_PORT} -> {e}")
        app.state.redis_client = None
        raise
