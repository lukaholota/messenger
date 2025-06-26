from typing import List

from starlette.websockets import WebSocket

from app.models import Message
from app.schemas.event import ServerEvent
from app.schemas.message import MessageRead


class EventSender:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket

    async def send_event(self, event: ServerEvent):
        await self.websocket.send_json(event.model_dump(mode='json'))

    async def send_bulk_messages(self, messages: List[Message]):
        message_schemas = [
            MessageRead.model_validate(message)
            for message in messages
        ]

        await self.websocket.send_json({
            'event': 'bulk_messages',
            'messages': [m.model_dump(mode='json') for m in message_schemas]
        })
