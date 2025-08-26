from app.infrastructure.events.base_event_dispatcher import BaseEventDispatcher
from app.infrastructure.exceptions.websocket import WebSocketException
from app.schemas.event import WebSocketEvent


class ChatWebSocketEventDispatcher(BaseEventDispatcher):
    async def dispatch(self, user_id: int, websocket_event: WebSocketEvent):
        event = websocket_event.event

        config = await self._get_config(event)

        if config.dto_class:
            if websocket_event.data is None:
                raise WebSocketException(
                    f"Event '{event}' requires 'data' field"
                )
            dto = config.dto_class(**websocket_event.data)

            await config.handler(dto, user_id)
        else:
            await config.handler(user_id)
