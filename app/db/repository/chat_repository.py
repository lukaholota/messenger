from sqlalchemy import select

from .base import BaseRepository
from app.models.chat import Chat as ChatModel
from app.models.user import User as UserModel
from app.schemas.chat import ChatCreate, ChatUpdate


class ChatRepository(BaseRepository[ChatModel, ChatCreate, ChatUpdate]):
    async def create_chat_with_participants(
            self,
            *,
            name: str,
            is_group: bool,
            users_to_add: list[UserModel]
    ) -> ChatModel:
        new_chat = ChatModel(name=name, is_group=is_group)
        self.db.add(new_chat)

        if users_to_add:
            new_chat.participants.extend(users_to_add)

        return new_chat

    async def get_chat_by_participants_ids(
            self,
            participants_ids: list[int],
    ) -> ChatModel | None:
        participant_1_id, participant_2_id = participants_ids
        query = (select(ChatModel)
        .where(ChatModel.is_group == False)
        .where(ChatModel.participants.any(
            UserModel.user_id == participant_1_id
        )).where(ChatModel.participants.any(
            UserModel.user_id == participant_2_id
        ))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
