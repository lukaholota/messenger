from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.repository.base import BaseRepository
from app.models.message_delivery import MessageDelivery
from app.schemas.message_delivery import MessageDeliveryCreate, \
    MessageDeliveryUpdate


class MessageDeliveryRepository(
    BaseRepository[
        MessageDelivery,
        MessageDeliveryCreate,
        MessageDeliveryUpdate
    ]
):
    async def create_message_delivery(
            self, user_id: int, message_id: int, chat_id: int
    ) -> MessageDelivery:
        message_delivery = MessageDelivery(
            user_id=user_id,
            message_id=message_id,
            chat_id=chat_id,
        )
        self.db.add(message_delivery)
        return message_delivery

    async def create_message_deliveries_bulk(
            self, user_ids: list[int], message_id: int, chat_id: int
    ):
        deliveries = [
            MessageDelivery(
                user_id=user_id,
                message_id=message_id,
                chat_id=chat_id,
            ) for user_id in user_ids
        ]
        self.db.add_all(deliveries)

    async def get_undelivered_messages_with_content(self, user_id: int):
        query = (
            select(MessageDelivery)
            .options(selectinload(MessageDelivery.message))
            .where(
                MessageDelivery.user_id == user_id,
                MessageDelivery.is_delivered == False
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_unread_messages(self, chat_id: int, user_id: int):
        query = (
            select(MessageDelivery)
            .where(
                MessageDelivery.is_read == False,
                MessageDelivery.chat_id == chat_id,
                MessageDelivery.user_id == user_id,
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()
