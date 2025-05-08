from sqlalchemy import select, asc, delete
from sqlalchemy.orm import selectinload

from .base import BaseRepository
from app.models.chat import Chat as ChatModel
from app.models.user import User as UserModel
from app.schemas.chat import ChatCreate, ChatUpdate
from app.models.chat_participant import ChatParticipant


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

    async def check_if_user_in_chat(self, chat_id, user_id) -> bool:
        query = select(ChatParticipant).where(
            ChatParticipant.chat_id == chat_id,
            ChatParticipant.user_id == user_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_chat_with_relationships(self, chat_id):
        query = select(ChatModel).where(
            ChatModel.chat_id == chat_id
        ).order_by(asc(ChatModel.created_at)).options(
            selectinload(ChatModel.participants),
            selectinload(ChatModel.messages)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()


    async def delete_user_from_group_chats(self, user_id):
        delete_stmt = delete(ChatParticipant.chat_id).join(
            ChatModel, ChatParticipant.chat_id == ChatModel.chat_id
        ).where(ChatParticipant.user_id == user_id).where(
            ChatModel.is_group == True
        )
        return delete_stmt