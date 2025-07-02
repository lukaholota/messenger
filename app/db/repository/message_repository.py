from sqlalchemy import select, func

from .base import BaseRepository
from app.models.message import Message as MessageModel
from app.schemas.message import MessageCreate, MessageUpdate
from ...models import User


class MessageRepository(
    BaseRepository[MessageModel, MessageCreate, MessageUpdate]
):
    async def create_message(
            self,
            content: str,
            user_id: int,
            chat_id: int,
    ) -> MessageModel | None:
        new_message = MessageModel(
            content=content,
            user_id=user_id,
            chat_id=chat_id
        )
        self.db.add(new_message)
        return new_message

    async def get_last_messages_from_every_chat(self, chat_ids):
        subquery = (
            select(
                MessageModel.chat_id,
                func.max(MessageModel.message_id).label('last_message_id')
            ).where(MessageModel.chat_id.in_(chat_ids))
            .group_by(MessageModel.chat_id)
            .subquery()
        )

        query = (
            select(MessageModel, User.display_name)
            .join(
                subquery, MessageModel.message_id == subquery.c.last_message_id
            ).join(User)
        )
        result = await self.db.execute(query)

        return result.scalars().all()
