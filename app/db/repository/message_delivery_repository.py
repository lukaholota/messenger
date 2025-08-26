from typing import List, Dict

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.db.repository.base import BaseRepository
from app.models import Chat
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
            self, deliveries: List[Dict]
    ):
        delivery_objects = [
            MessageDelivery(**delivery) for delivery in deliveries
        ]
        self.db.add_all(delivery_objects)

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

    async def get_unread_counts(self, user_id: int, chat_ids: list[int]):
        query = (
            select(
                Chat.chat_id,
                func.count(
                    func.nullif(MessageDelivery.is_read, True)
                ).label('unread_count')
            ).outerjoin(
                MessageDelivery,
                onclause=(MessageDelivery.chat_id == Chat.chat_id) &
                         (MessageDelivery.user_id == user_id)
            ).where(Chat.chat_id.in_(chat_ids))
            .group_by(Chat.chat_id)
        )
        result = await self.db.execute(query)
        return result.all()
