from typing import Type

from pydantic import BaseModel

from app.infrastructure.types.types import EventCallback


class EventHandlerConfig:
    def __init__(self, dto_class: Type[BaseModel], handler: EventCallback):
        self.dto_class = dto_class
        self.handler = handler
