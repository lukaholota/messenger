from starlette.websockets import WebSocket

from app.schemas.chat import ChatOverview
from app.schemas.chat_read_status import ChatReadStatusRead
from app.schemas.event import ReadStatusUpdatedEvent, MessageSentEvent, \
    NewChatSentEvent
from app.schemas.message import ChatMessage
from app.services.ws.event_sender import \
    EventSender
from app.services.ws.redis_chat_subscription_service import \
    RedisChatSubscriptionService


class RedisEventHandler:
    def __init__(
            self,
            websocket: WebSocket,
            event_sender: EventSender,
            redis_subscription_service: RedisChatSubscriptionService,
    ):
        self.websocket = websocket
        self.event_sender = event_sender
        self.redis_subscription_service = redis_subscription_service


    async def handle_message_sent(self, message_out: ChatMessage):
        event = MessageSentEvent(data=message_out)

        await self.event_sender.send_event(event)

    async def handle_read_status_updated(
            self, chat_read_status_out: ChatReadStatusRead
    ):
        event = ReadStatusUpdatedEvent(data=chat_read_status_out)
        await self.event_sender.send_event(event)

    async def handle_new_chat_sent(self, new_chat_sent_out=ChatOverview):
        await self.redis_subscription_service.subscribe_to_channel(
            f'chat:{new_chat_sent_out.chat_id}'
        )

        event = NewChatSentEvent(data=new_chat_sent_out)

        await self.event_sender.send_event(event)
