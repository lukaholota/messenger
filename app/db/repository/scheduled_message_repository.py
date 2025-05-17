from datetime import datetime

from sqlalchemy import select

from app.db.repository.base import BaseRepository
from app.models.scheduled_message import ScheduledMessage, \
    ScheduledMessageStatus
from app.schemas.scheduled_message import ScheduledMessageUpdate, \
    ScheduledMessageCreate


class ScheduledMessageRepository(
    BaseRepository[
        ScheduledMessage,
        ScheduledMessageCreate,
        ScheduledMessageUpdate
    ]
):
    async def create_scheduled_message(
            self,
            *,
            user_id: int,
            chat_id: int,
            content: str,
            scheduled_send_at: datetime
    ) -> ScheduledMessage:
        new_scheduled_message = ScheduledMessage(
            user_id=user_id,
            chat_id=chat_id,
            content=content,
            scheduled_send_at=scheduled_send_at
        )
        self.db.add(new_scheduled_message)

        return new_scheduled_message

    async def get_scheduled_messages(
            self,
            *,
            user_id: int,
            chat_id: int
    ):
        query = select(ScheduledMessage).where(
            ScheduledMessage.user_id == user_id
        ).where(ScheduledMessage.chat_id == chat_id).where(
            ScheduledMessage.status != ScheduledMessageStatus.CANCELED
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def check_scheduled_message_in_chat_and_belongs_to_user(
            self,
            *,
            scheduled_message_id: int,
            chat_id: int,
            user_id: int
    ):
        query = select(ScheduledMessage).where(
            ScheduledMessage.chat_id == chat_id
        ).where(
            ScheduledMessage.scheduled_message_id == scheduled_message_id
        ).where(
            ScheduledMessage.user_id == user_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
