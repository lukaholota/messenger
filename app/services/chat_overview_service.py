from typing import List

from app.schemas.chat import ChatOverview
from app.services import message_delivery_service
from app.services.chat_service import ChatService
from app.services.message_delivery_service import MessageDeliveryService
from app.services.message_service import MessageService


class ChatOverviewService:
    def __init__(
            self,
            chat_service: ChatService,
            message_delivery_service: MessageDeliveryService,
            message_service: MessageService,
    ):
        self.chat_service = chat_service
        self.message_delivery_service = message_delivery_service
        self.message_service = message_service

    async def get_chat_overview_list(self, user_id: int) -> (
            List[ChatOverview] | []
    ):
        chat_ids = await self.chat_service.get_user_chat_ids(user_id)

        if not chat_ids:
            return []

        unread_counts_map = await (
            self.message_delivery_service.get_unread_counts_map(user_id)
        )

        last_messages_map = await (
            self.message_service.get_last_messages_from_every_chat_map(
                chat_ids
            )
        )

        chat_overviews = []

        for chat_id in chat_ids:
            chat_overviews.append(
                ChatOverview(
                    chat_id=chat_id,
                    unread_count=unread_counts_map[chat_id],
                )
            )


