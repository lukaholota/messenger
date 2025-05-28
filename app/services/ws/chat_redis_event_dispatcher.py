import json
from app.infrastructure.types import EventHandlerMap, EventCallback


class ChatRedisEventDispatcher:
    def __init__(self):
        self._handlers: EventHandlerMap = {}

    async def register(self, event: str, handler: EventCallback):
        self._handlers[event] = handler

    async def dispatch(self, raw_data: str):
        data = json.loads(raw_data)
        event = data.get('event')
        payload = data.get('data')

        if event in self._handlers.keys():
            await self._handlers[event](payload)
