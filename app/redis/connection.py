from redis import StrictRedis
from redis.exceptions import ConnectionError
from app.core.config import settings
from logging import getLogger

logger = getLogger(__name__)

REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT
REDIS_PASSWORD = settings.REDIS_PASSWORD

redis_client = None

def get_redis_client() -> StrictRedis:
    global redis_client
    if redis_client is None:
        try:
            redis_client = StrictRedis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                decode_responses=True,
            )
            redis_client.ping()
            logger.info('Redis connection established!')
        except ConnectionError as e:
            logger.error(f"Failed to establish Redis connection at "
                         f"{REDIS_HOST}:{REDIS_PORT} -> {e}")
            redis_client = None

    if redis_client is None:
        raise ConnectionError("Failed to establish Redis connection")

    return redis_client
