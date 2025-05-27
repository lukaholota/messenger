from typing import Any

from redis.asyncio import Redis
import logging

from app.core.cache.base import Serializer, Cache


class RedisCache(Cache):
    def __init__(
            self,
            redis: Redis,
            serializer: Serializer,
            default_ttl: int = 900,
    ):
        self._redis = redis
        self._ttl = default_ttl
        self._serializer = serializer
        self._log = logging.getLogger(__name__)

    async def get(self, key: str) -> Any | None:
        raw = await self._redis.get(key)
        return self._serializer.loads(raw) if raw else None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        await self._redis.set(
            key,
            self._serializer.dumps(value),
            ex = ttl or self._ttl,
        )

    async def delete(self, key: str) -> None:
        await self._redis.delete(key)

    async def delete_pattern(
            self,
            pattern: str,
            batch: int = 500
    ):
        cursor = "0"
        while cursor:
            cursor, keys = await self._redis.scan(
                cursor=cursor, match=pattern, batch=batch
            )
            if keys:
                await self._redis.unlink(*keys)

    async def exists(self, key: str) -> bool:
        return await self._redis.exists(key)

    async def setex(
            self,
            *,
            key: str,
            value: Any,
            ttl: int | None = None
    ) -> None:
        await self._redis.setex(
            key, ttl or self._ttl, self._serializer.dumps(value)
        )

    async def incr(self, key: str):
        return await self._redis.incr(key)

    async def expire(self, key: str, ttl: int | None = None) -> bool:
        return await self._redis.expire(key, ttl or self._ttl)
