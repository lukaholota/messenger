from .base import BaseRepository
from app.models.message import Message as MessageModel
from app.schemas.message import MessageCreate, MessageUpdate


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
