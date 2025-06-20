import asyncio
import json
from typing import List, Dict, Callable, Awaitable

from redis.asyncio.client import PubSub

from app.infrastructure.cache.redis_pubsub import RedisPubSub

from logging import getLogger

from app.infrastructure.exceptions.websocket import WebSocketException
from app.schemas.event import RedisEvent

logger = getLogger(__name__)


class RedisChatSubscriptionService:
    def __init__(
            self,
            pubsub: RedisPubSub
    ):
        self.tasks: List = [asyncio.Task]
        self.pubsubs: Dict[str, PubSub] = {}
        self.pubsub = pubsub

    async def subscribe_to_every_chat(
            self,
            user_id,
            chat_ids,
            callback: Callable[[RedisEvent], Awaitable[None]],
    ):
        for chat_id in chat_ids:
            channel = f'chat:{chat_id}'
            pubsub = await self.pubsub.subscribe(channel)
            task = asyncio.create_task(self.listen_to_channel(
                pubsub,
                callback
            ))
            self.tasks.append(task)
            self.pubsubs[channel] = pubsub

            logger.debug(f'User {user_id} subscribed to channel {channel}')

    async def listen_to_channel(self, pubsub: PubSub, callback: Callable):
        try:
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    logger.debug(f'Redis Pubsub got a message {message}')
                    data = json.loads(message['data'])

                    redis_event = RedisEvent(**data)
                    await callback(redis_event)
        except Exception as e:
            logger.exception(f'Error in listen_to_channel {e}')
            raise WebSocketException('error listening to channel')


    async def cleanup(self):
        try:
            for channel, pubsub in self.pubsubs.items():
                await pubsub.unsubscribe(channel)
                await pubsub.close()
            self.pubsubs.clear()
            for task in self.tasks:
                task.cancel()
        except Exception as e:
            logger.error(f'error: {e}', exc_info=e)
            raise WebSocketException('error cleaning up')
