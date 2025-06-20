from app.infrastructure.events.base_event_dispatcher import BaseEventDispatcher
from app.schemas.event import WebSocketEvent


class ChatWebSocketEventDispatcher(BaseEventDispatcher):
    async def dispatch(self, user_id: int, websocket_event: WebSocketEvent):
        event = websocket_event.event
        data: dict = websocket_event.data

        config = await self._get_config(event)

        dto = config.dto_class(**data)

        await config.handler(dto, user_id)
