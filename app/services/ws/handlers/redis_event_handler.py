from starlette.websockets import WebSocket

from app.schemas.chat_read_status import ChatReadStatusRead
from app.schemas.message import MessageRead
from app.services.ws.chat_web_socket_connection_manager import \
    ChatWebSocketConnectionManager


class RedisEventHandler:
    def __init__(
            self,
            websocket: WebSocket,
            connection_manager: ChatWebSocketConnectionManager):
        self.websocket = websocket
        self.connection_manager = connection_manager

    async def handle_message_sent(self, message_out: MessageRead):
        message = message_out.model_dump(mode='json')
        await self.connection_manager.send_message_to_user(message)

    async def handle_read_status_updated(
            self, chat_read_status_out: ChatReadStatusRead
    ):
        await self.websocket.send_json(
            chat_read_status_out.model_dump(mode='json')
        )
