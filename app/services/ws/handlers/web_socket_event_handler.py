from app.schemas.chat_read_status import ChatReadStatusUpdate
from app.schemas.event import GetChatInfoEvent
from app.schemas.message import MessageCreate
from app.services.ws.chat_read_service import ChatReadService
from app.services.ws.message_web_socket_handler import MessageWebSocketHandler


class WebSocketEventHandler:
    def __init__(
            self,
            message_handler: MessageWebSocketHandler,
            chat_read_service: ChatReadService,
    ):
        self.message_handler = message_handler
        self.chat_read_service = chat_read_service

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
        pass
