from time import time
from redis.asyncio import Redis


class RedisTokenBlacklistService:
    def __init__(
            self,
            redis_client: Redis
    ):
        self.redis_client: Redis = redis_client
        self.blacklist_prefix = "blacklisted_tokens:"

    async def add_to_blacklist(
            self,
            token_identifier: str,
            original_expiration_timestamp: int,
    ):
        current_time = int(time())

        if original_expiration_timestamp > current_time:
            ttl = original_expiration_timestamp - current_time
            await self.redis_client.setex(
                f"{self.blacklist_prefix}{token_identifier}",
                ttl,
                'invalidated'
            )

    async def is_blacklisted(self, token_identifier: str) -> bool:
        return await self.redis_client.exists(
            f"{self.blacklist_prefix}{token_identifier}"
        )
