from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository.chat_repository import ChatRepository
from app.db.repository.scheduled_message_repository import \
    ScheduledMessageRepository
from app.exceptions import ScheduledInPastError, MessagingConnectionError, \
    InvalidMessageDataError, MessagePublishError, ChatValidationError, \
    ScheduledMessageValidationError
from app.models import User
from app.models.scheduled_message import ScheduledMessage, \
    ScheduledMessageStatus
from app.rabbitmq_client import publish_scheduled_message


class ScheduledMessageService:
    def __init__(
            self,
            db: AsyncSession,
            *,
            scheduled_message_repository: ScheduledMessageRepository,
            chat_repository: ChatRepository,
            current_user: User,
    ):
        self.db = db
        self.scheduled_message_repository = scheduled_message_repository
        self.chat_repository = chat_repository
        self.current_user = current_user

    async def schedule_new_message(
            self,
            *,
            chat_id: int,
            content: str,
            scheduled_send_at: datetime,
    ) -> ScheduledMessage | None:
        await self.check_user_in_chat(
            chat_id, self.current_user.user_id
        )

        scheduled_message_in_db = await self.save_scheduled_message_to_db(
            user_id=self.current_user.user_id,
            chat_id=chat_id,
            content=content,
            scheduled_send_at=scheduled_send_at,
        )
        await self.send_to_messaging(
            chat_id=chat_id,
            user_id=self.current_user.user_id,
            scheduled_message_db_id=(
                scheduled_message_in_db.scheduled_message_id
            ),
            content=content,
            scheduled_send_at=scheduled_send_at,
        )
        return scheduled_message_in_db

    async def check_user_in_chat(
            self,
            chat_id: int,
            user_id: int,
    ):
        if not await self.chat_repository.check_if_user_in_chat(
            user_id=user_id,
            chat_id=chat_id,
        ):
            raise ChatValidationError(
                f"User '{user_id}' not in chat '{chat_id}'"
            )

    async def save_scheduled_message_to_db(
            self,
            *,
            chat_id: int,
            user_id: int,
            content: str,
            scheduled_send_at: datetime,
    ) -> ScheduledMessage:
        new_scheduled_message_db = await (
            self.scheduled_message_repository.create_scheduled_message(
                user_id=user_id,
                chat_id=chat_id,
                content=content,
                scheduled_send_at=scheduled_send_at,
        ))
        await self.db.commit()
        await self.db.refresh(new_scheduled_message_db)

        return new_scheduled_message_db

    async def send_to_messaging(
            self,
            chat_id: int,
            user_id: int,
            scheduled_message_db_id: int,
            content: str,
            scheduled_send_at: datetime,
    ):
        now = datetime.now(timezone.utc)

        if scheduled_send_at <= now:
            raise ScheduledInPastError

        delay = scheduled_send_at - now
        delay_seconds = int(delay.total_seconds())

        message_payload = {
            'chat_id': chat_id,
            'user_id': user_id,
            'scheduled_message_db_id': scheduled_message_db_id,
            'content': content,
            'scheduled_at': scheduled_send_at.isoformat(),
            'created_at': now.isoformat(),
        }
        try:
            await publish_scheduled_message(message_payload, delay_seconds)
        except MessagingConnectionError:
            raise
        except InvalidMessageDataError:
            raise
        except MessagePublishError:
            raise

    async def get_scheduled_messages(
            self,
            chat_id: int,
    ):
        await self.check_user_in_chat(
            chat_id, self.current_user.user_id
        )

        return await self.scheduled_message_repository.get_scheduled_messages(
            user_id=self.current_user.user_id,
            chat_id=chat_id
        )

    async def cancel_scheduled_message(
            self,
            *,
            scheduled_message_id: int,
            chat_id: int,
    ):
        await self.check_user_in_chat(
            chat_id=chat_id,
            user_id=self.current_user.user_id,
        )

        scheduled_message: ScheduledMessage = await (
            self.get_and_validate_existing_scheduled_message(
                chat_id=chat_id,
                user_id=self.current_user.user_id,
                scheduled_message_id=scheduled_message_id
        ))

        scheduled_message.status = ScheduledMessageStatus.CANCELED
        await self.db.commit()
        await self.db.refresh(scheduled_message)

        return scheduled_message

    async def get_and_validate_existing_scheduled_message(
            self,
            chat_id: int,
            user_id: int,
            scheduled_message_id: int
    ) -> ScheduledMessage:
        existing_scheduled_message = await (
            self.scheduled_message_repository
            .check_scheduled_message_in_chat_and_belongs_to_user(
                scheduled_message_id=scheduled_message_id,
                chat_id=chat_id,
                user_id=user_id,
        ))
        if not existing_scheduled_message:
            raise ScheduledMessageValidationError(
                f"Message '{scheduled_message_id}' not in chat '{chat_id}' or "
                f"does not belong to user {user_id}"
            )
        return existing_scheduled_message

    async def update_scheduled_message(
            self,
            chat_id: int,
            scheduled_message_id: int,
            content: str,
            scheduled_send_at: datetime,
    ):
        old_scheduled_message = await self.cancel_scheduled_message(
            scheduled_message_id=scheduled_message_id,
            chat_id=chat_id,
        )

        new_scheduled_message = await self.schedule_new_message(
            chat_id=chat_id,
            content=content,
            scheduled_send_at=scheduled_send_at,
        )

        return old_scheduled_message, new_scheduled_message
