from .base import BaseRepository
from app.models.message import Message as MessageModel
from app.schemas.message import MessageCreate, MessageUpdate
from app.models.user import User as UserModel
from app.models.chat import Chat as ChatModel


class MessageRepository(
    BaseRepository[MessageModel, MessageCreate, MessageUpdate]
):
    async def create_message(
            self,
            content: str,
            sender: UserModel,
            chat: ChatModel,
    ) -> MessageModel | None:
        new_message = MessageModel(content=content, sender=sender, chat=chat)
        self.db.add(new_message)
        return new_message
