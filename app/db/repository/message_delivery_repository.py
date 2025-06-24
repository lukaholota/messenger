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
    async def create_message_delivery(self, user_id: int, message_id: int) \
            -> MessageDelivery:
        message_delivery = MessageDelivery(
            user_id=user_id,
            message_id=message_id,
        )
        self.db.add(message_delivery)
        return message_delivery

    async def update_message_delivery(self, ):