from redis.asyncio import Redis
from redis.asyncio.client import PubSub


class RedisPubSub:
    def __init__(self, redis: Redis):
        self._redis = redis

    async def publish(self, channel: str, message: str):
        await self._redis.publish(channel, message)

    async def subscribe(self, channel: str) -> PubSub:
        pubsub = self._redis.pubsub()
        await pubsub.subscribe(channel)
        return pubsub
