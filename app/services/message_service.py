from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository.chat_repository import ChatRepository
from app.db.repository.message_repository import MessageRepository
from app.infrastructure.exceptions.exceptions import DatabaseError, MessageValidationError
from app.models import Message
from app.schemas.message import MessageCreate


class MessageService:
    def __init__(
            self,
            db: AsyncSession,
            *,
            message_repository: MessageRepository,
            chat_repository: ChatRepository,
            current_user_id: int,
    ):
        self.db = db
        self.message_repository = message_repository
        self.chat_repository = chat_repository
        self.current_user_id = current_user_id

    async def create_message(self, message_in: MessageCreate) -> Message:
        if not message_in.content:
            raise MessageValidationError('The message is empty')

        existing_chat = await self.chat_repository.get_by_id(
            message_in.chat_id
        )
        if not existing_chat:
            raise MessageValidationError('Wrong chat')

        if not await self.chat_repository.check_if_user_in_chat(
            message_in.chat_id, self.current_user_id
        ):
            raise MessageValidationError('User not in chat')

        try:
            message = await self.message_repository.create_message(
                content=message_in.content,
                user_id=self.current_user_id,
                chat_id=existing_chat.chat_id,
            )
            await self.db.commit()
            await self.db.refresh(message)

            return message
        except SQLAlchemyError as db_exc:
            await self.db.rollback()
            raise DatabaseError(
                "Failed to create message due to database issue"
            ) from db_exc
        except Exception as exc:
            await self.db.rollback()
            raise exc
