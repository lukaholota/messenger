from datetime import datetime, timezone

from sqlalchemy import select

from app.db.repository.base import BaseRepository
from app.models import Message
from app.models.chat_read_status import ChatReadStatus
from app.schemas.chat_read_status import ChatReadStatusCreate, \
    ChatReadStatusUpdate


class ChatReadStatusRepository(
    BaseRepository[ChatReadStatus, ChatReadStatusCreate, ChatReadStatusUpdate]
):
    async def get_unread_messages(
            self, chat_id: int, exclude_user_id: int, last_read_message_id: int
    ):
        query = (
            select(Message)
            .where(Message.chat_id == chat_id)
            .where(Message.user_id != exclude_user_id)
            .where(Message.message_id > last_read_message_id)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_last_read_message(self, chat_id: int, user_id: int):
        query = (
            select(ChatReadStatus)
            .where(ChatReadStatus.chat_id == chat_id)
            .where(ChatReadStatus.user_id == user_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def mark_as_read(
            self,
            last_read_message: ChatReadStatus,
            new_last_read_message_id: int,
    ):
        last_read_message.read_at = datetime.now(timezone.utc)
        last_read_message.last_read_message_id = new_last_read_message_id
        return last_read_message

    async def create_chat_read_status(self, chat_id: int, user_id: int):
        return ChatReadStatus(chat_id=chat_id, user_id=user_id)
