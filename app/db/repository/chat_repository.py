from typing import Dict

from sqlalchemy import select, asc, delete, and_
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
            chat_name_map: Dict[int, str],
            is_group: bool,
            users_to_add: list[UserModel]
    ) -> ChatModel:
        new_chat = ChatModel(is_group=is_group)
        self.db.add(new_chat)

        await self.db.flush()

        chat_participants = []

        for user in users_to_add:
            chat_participants.append(ChatParticipant(
                user_id=user.user_id,
                chat_id=new_chat.chat_id,
                chat_name=chat_name_map[user.user_id]
            ))

        self.db.add_all(chat_participants)

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

    async def get_chat_with_users(self, chat_id) -> ChatModel | None:
        query = select(ChatModel).where(
            ChatModel.chat_id == chat_id
        ).options(
            selectinload(ChatModel.participants)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_chat_with_chat_participants_raw(self, chat_id):
        query = (
            select(ChatModel, ChatParticipant, UserModel)
            .select_from(ChatModel)
            .join(
                ChatParticipant,
                onclause=ChatParticipant.chat_id == ChatModel.chat_id,
            )
            .join(
                UserModel,
                onclause=ChatParticipant.user_id == UserModel.user_id
            )
            .where(ChatModel.chat_id == chat_id)
        )
        result = await self.db.execute(query)
        return result.all()

    async def delete_user_from_group_chats(self, user_id):
        group_chat_ids_subquery = select(ChatModel.chat_id).where(
            ChatModel.is_group == True
        ).scalar_subquery()

        delete_stmt = delete(ChatParticipant).where(
            and_(
                ChatParticipant.user_id == user_id,
                ChatParticipant.chat_id.in_(group_chat_ids_subquery)
            )
        )
        return delete_stmt

    async def get_user_chat_ids(self, user_id):
        query = select(ChatParticipant.chat_id).where(
            ChatParticipant.user_id == user_id
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_chats_with_names_for_user_raw(self, user_id):
        query = (
            select(ChatModel, ChatParticipant.chat_name)
            .join(ChatParticipant)
            .where(ChatParticipant.user_id == user_id)
        )

        result = await self.db.execute(query)
        return result.all()
