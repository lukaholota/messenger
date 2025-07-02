from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository.chat_repository import ChatRepository
from app.db.repository.message_repository import MessageRepository
from app.infrastructure.exceptions.exceptions import DatabaseError, MessageValidationError
from app.models import Message
from app.schemas.message import MessageCreate
from app.services.message_delivery_service import MessageDeliveryService


class MessageService:
    def __init__(
            self,
            db: AsyncSession,
            *,
            message_repository: MessageRepository,
            chat_repository: ChatRepository,
            message_delivery_service: MessageDeliveryService,
            current_user_id: int,
    ):
        self.db = db
        self.message_repository = message_repository
        self.chat_repository = chat_repository
        self.current_user_id = current_user_id
        self.message_delivery_service = message_delivery_service

    async def create_message(self, message_in: MessageCreate) -> Message:
        if not message_in.content:
            raise MessageValidationError('The message is empty')

        existing_chat = await self.chat_repository.get_chat_with_participants(
            message_in.chat_id
        )
        if not existing_chat:
            raise MessageValidationError('Wrong chat')

        chat_participant_ids = [
            user.user_id for user in existing_chat.participants
        ]
        if not chat_participant_ids:
            raise MessageValidationError('No participants in chat')

        if self.current_user_id not in chat_participant_ids:
            raise MessageValidationError('User not in chat')

        try:
            message = await self.message_repository.create_message(
                content=message_in.content,
                user_id=self.current_user_id,
                chat_id=existing_chat.chat_id,
            )

            await self.db.flush()


            recipient_ids = [
                user_id for user_id in chat_participant_ids
                if user_id != self.current_user_id
            ]

            await self.message_delivery_service.create_message_deliveries_bulk(
                user_ids=recipient_ids,
                message_id=message.message_id,
                chat_id=message.chat_id,
            )

            await self.db.commit()
            await self.db.refresh(message)

            return message

        except SQLAlchemyError as db_exc:
            await self.db.rollback()
            raise DatabaseError(
                "Failed to create message due to database issue"
            ) from db_exc
        except Exception as e:
            await self.db.rollback()
            raise e
