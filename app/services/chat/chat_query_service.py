from typing import List

from app.db.repository.chat_repository import ChatRepository
from app.schemas.chat import ChatWithName


class ChatQueryService:
    def __init__(
            self,
            chat_repository: ChatRepository,
    ):
        self.chat_repository = chat_repository

    async def get_chats_for_user(self, user_id: int) -> List[ChatWithName]:
        data_raw = await (
            self.chat_repository.get_chats_with_names_for_user_raw(user_id)
        )

        return [
            ChatWithName(chat=chat, chat_name=chat_name)
            for chat, chat_name in data_raw
        ]

