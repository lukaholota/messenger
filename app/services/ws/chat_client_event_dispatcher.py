import json

from app.infrastructure.exceptions.websocket import WebSocketException
from app.infrastructure.types import EventHandlerMap, EventCallback


class ChatClientEventDispatcher:
    def __init__(self):
        self._handlers: EventHandlerMap = {}

    async def register(self, event: str, handler: EventCallback):
        self._handlers[event] = handler

    async def dispatch(self, user_id: int, payload: dict):
        event_type = payload.get('event_type')
        payload = payload.get('data')

        if not event_type or event_type not in self._handlers:
            raise WebSocketException('Invalid event type')

        handler = self._handlers[event_type]

        await handler(user_id, payload)
