from datetime import datetime, timezone
from typing import List, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository.message_delivery_repository import \
    MessageDeliveryRepository


class MessageDeliveryService:
    def __init__(
            self,
            db: AsyncSession,
            message_delivery_repository: MessageDeliveryRepository,
    ):
        self.db = db
        self.message_delivery_repository = message_delivery_repository

    async def create_message_delivery(self, user_id: int, message_id, chat_id):
        await self.message_delivery_repository.create_message_delivery(
            user_id=user_id, message_id=message_id, chat_id=chat_id
        )

    async def create_message_deliveries_bulk(
            self, deliveries: List[Dict]
    ):
        await self.message_delivery_repository.create_message_deliveries_bulk(
            deliveries=deliveries
        )

    async def mark_messages_delivered(self, user_id):
        deliveries = await (
            self.message_delivery_repository.
                get_undelivered_messages_with_content(user_id=user_id)
        )
        if not deliveries:
            return []

        for delivery in deliveries:
            delivery.is_delivered = True
            delivery.delivered_at = datetime.now(timezone.utc)

        await self.db.commit()

        return [delivery.message for delivery in deliveries]

    async def read_messages(
            self, chat_id: int, user_id: int, last_read_message_id: int
    ):
        unread_messages = await (
            self.message_delivery_repository.get_unread_messages(
                chat_id=chat_id, user_id=user_id
            )
        )

        for unread_message in unread_messages:
            if unread_message.message_id <= last_read_message_id:
                unread_message.is_read = True
                unread_message.read_at = datetime.now(timezone.utc)

        await self.db.commit()

    async def get_unread_counts_map(
            self, user_id: int, chat_ids: list[int]
    ) -> dict[int, int]:
        raw_results = await (
            self.message_delivery_repository
            .get_unread_counts(user_id, chat_ids)
        )

        return {
            raw_result.chat_id: raw_result.unread_count
            for raw_result in raw_results
        }
