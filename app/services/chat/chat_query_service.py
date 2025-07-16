from typing import List, Dict, Any

from app.db.repository.chat_repository import ChatRepository
from app.models import Chat
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

    async def get_chat_with_chat_participants(self, chat_id) -> Dict[str, Any]:
        data_raw = await (
            self.chat_repository.get_chat_with_chat_participants_raw(chat_id)
        )
        chat: Chat = data_raw[0][0] if data_raw else None
        participants = [p for _, p, _ in data_raw]
        users = [u for _, _, u in data_raw]

        return {
            'chat': chat,
            'participants': participants,
            'users': users,
        }
