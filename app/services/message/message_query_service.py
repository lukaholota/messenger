from typing import Sequence

from app.db.repository.message_repository import MessageRepository
from app.models import Message


class MessageQueryService:
    def __init__(self, message_repository: MessageRepository):
        self.message_repository = message_repository

    async def get_last_messages_from_every_chat_map(
            self, chat_ids: list[int]):
        raw_results = await (
            self.message_repository.get_last_messages_from_every_chat(
            chat_ids=chat_ids,
        ))

        return {
            message.chat_id: {'message': message, 'display_name': display_name}
            for message, display_name in raw_results
        }

    async def get_chat_messages(self, chat_id) -> Sequence[Message]:
        return await self.message_repository.get_chat_messages(chat_id)
