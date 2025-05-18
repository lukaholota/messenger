from time import time

from app.infrastructure.cache.redis_cache import RedisCache


class CacheTokenBlacklistService:
    def __init__(
            self,
            cache: RedisCache
    ):
        self.cache: RedisCache = cache
        self.blacklist_prefix = "blacklisted_tokens:"

    async def add_to_blacklist(
            self,
            token_identifier: str,
            original_expiration_timestamp: int,
    ):
        current_time = int(time())

        if original_expiration_timestamp > current_time:
            ttl = original_expiration_timestamp - current_time
            await self.cache.setex(
                key=f"{self.blacklist_prefix}{token_identifier}",
                ttl=ttl,
                value='invalidated'
            )

    async def is_blacklisted(self, token_identifier: str) -> bool:
        return await self.cache.exists(
            f"{self.blacklist_prefix}{token_identifier}"
        )
