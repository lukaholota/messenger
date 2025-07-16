from app.schemas.chat_read_status import ChatReadStatusUpdate
from app.schemas.event import GetChatInfoEvent, ChatInfoSentEvent, \
    GetChatMessagesEvent
from app.schemas.message import MessageCreate
from app.services.chat.chat_info_service import ChatInfoService
from app.services.message.message_query_service import MessageQueryService
from app.services.ws.chat_read_service import ChatReadService
from app.services.ws.event_sender import EventSender
from app.services.ws.message_web_socket_handler import MessageWebSocketHandler


class WebSocketEventHandler:
    def __init__(
            self,
            message_handler: MessageWebSocketHandler,
            message_query_service: MessageQueryService,
            chat_read_service: ChatReadService,
            chat_info_service: ChatInfoService,
            event_sender: EventSender,
    ):
        self.message_handler = message_handler
        self.message_query_service = message_query_service
        self.chat_read_service = chat_read_service
        self.chat_info_service = chat_info_service
        self.event_sender = event_sender

    async def handle_new_message(
            self, message_in: MessageCreate, user_id: int,
    ):
        await self.message_handler.send_to_mq(user_id, message_in)

    async def handle_read_message(
            self, data_in: ChatReadStatusUpdate, user_id: int
    ):
        await self.chat_read_service.update_read_status(user_id, data_in)

    async def handle_get_chat_info(
            self, data_in: GetChatInfoEvent, user_id: int
    ):
        chat_info = await self.chat_info_service.get_chat_info(
            data_in.chat_id, user_id
        )

        event = ChatInfoSentEvent(data=chat_info)

        await self.event_sender.send_event(event)

    async def handle_get_messages(
            self, data_in: GetChatMessagesEvent, user_id: int
    ):


