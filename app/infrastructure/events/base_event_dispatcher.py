from abc import ABC
from typing import Type

from pydantic import BaseModel

from app.infrastructure.events.event_handler_config import EventHandlerConfig
from app.infrastructure.exceptions.websocket import WebSocketException
from app.infrastructure.types.types import EventCallback
from app.infrastructure.types.types_common import EventHandlerMap


class BaseEventDispatcher(ABC):
    def __init__(self):
        self._handlers: EventHandlerMap = {}

    async def register(
            self,
            event: str, 
            dto_class: Type[BaseModel],
            handler: EventCallback
    ):
        self._handlers[event] = EventHandlerConfig(dto_class, handler)

    async def _get_config(self, event: str) -> EventHandlerConfig:
        if not event or not event in self._handlers:
            raise WebSocketException('Invalid event')
        return self._handlers[event]

    async def dispatch(self, *args, **kwargs): ...
