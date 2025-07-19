from starlette.websockets import WebSocket

from app.schemas.chat_read_status import ChatReadStatusRead
from app.schemas.event import ReadStatusUpdatedEvent, MessageSentEvent
from app.schemas.message import ChatMessage
from app.services.ws.event_sender import \
    EventSender


class RedisEventHandler:
    def __init__(
            self,
            websocket: WebSocket,
            event_sender: EventSender):
        self.websocket = websocket
        self.event_sender = event_sender

    async def handle_message_sent(self, message_out: ChatMessage):
        event = MessageSentEvent(data=message_out)

        await self.event_sender.send_event(event)

    async def handle_read_status_updated(
            self, chat_read_status_out: ChatReadStatusRead
    ):
        event = ReadStatusUpdatedEvent(data=chat_read_status_out)
        await self.event_sender.send_event(event)
