import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from fastapi import Request

from app.infrastructure.cache.redis_cache import RedisCache

WINDOW_SIZE = 60
MAX_REQUESTS = 100

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        redis: RedisCache = getattr(request.app.state, 'redis', None)
        if redis is None:
            return JSONResponse(
                content={'detail': 'cant connect to redis'},
                status_code=500
            )

        client_ip = request.client.host
        now = int(time.time())

        key = f'rate_limit:{client_ip}:{now // WINDOW_SIZE}'

        current_count = await redis.incr(key)

        if current_count == 1:
            await redis.expire(key, WINDOW_SIZE)

        if current_count > MAX_REQUESTS:
            return JSONResponse(
                content={'detail': 'general request limit exceeded'},
                status_code=429
            )

        return await call_next(request)
