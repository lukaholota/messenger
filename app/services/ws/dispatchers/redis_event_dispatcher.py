from app.infrastructure.events.base_event_dispatcher import BaseEventDispatcher
from app.schemas.event import RedisEvent


class ChatRedisEventDispatcher(BaseEventDispatcher):
    async def dispatch(self, redis_event: RedisEvent):
        event = redis_event.event
        data: dict = redis_event.data

        config = await self._get_config(event)

        dto = config.dto_class(**data)

        await config.handler(dto)
