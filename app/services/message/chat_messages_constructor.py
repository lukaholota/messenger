from app.schemas.message import ChatMessage
from app.services.message.message_query_service import MessageQueryService


class ChatMessagesConstructor:
    def __init__(self, message_query_service: MessageQueryService):
        self.message_query_service = message_query_service

    async def construct_chat_messages(self, chat_id, user_id):
        messages = await self.message_query_service.get_chat_messages(chat_id)
        return [
            ChatMessage(
                message_id=message.message_id,
                chat_id=chat_id,
                user_id=message.user_id,
                content=message.content,
                is_read=any(delivery.is_read for delivery in message.deliveries),
                read_at_list=[{delivery.user_id: delivery.read_at} for delivery in message.deliveries],
                display_name=message.sender.display_name,
                sent_at=message.sent_at
            ) for message in messages
        ]