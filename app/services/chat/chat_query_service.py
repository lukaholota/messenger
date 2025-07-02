from app.db.repository.chat_repository import ChatRepository


class ChatQueryService:
    def __init__(
            self,
            chat_repository: ChatRepository,
    ):
        self.chat_repository = chat_repository

    async def get_chats_for_user(self, user_id: int):
        return await self.chat_repository.get_chats_for_user(user_id)
