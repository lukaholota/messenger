from typing import List

from app.models import Chat
from app.schemas.chat import ChatOverview
from app.schemas.message import MessageInChatOverview
from app.services.message.message_query_service import MessageQueryService
from app.services.message_delivery_service import MessageDeliveryService


class ChatOverviewService:
    def __init__(
            self,
            message_delivery_service: MessageDeliveryService,
            message_query_service: MessageQueryService,
    ):
        self.message_delivery_service = message_delivery_service
        self.message_query_service = message_query_service

    async def get_chat_overview_list(
            self, user_id: int, chats: list[Chat]) -> List[ChatOverview] | []:
        chat_ids = [chat.chat_id for chat in chats]

        unread_counts_map = await (
            self.message_delivery_service.get_unread_counts_map(user_id)
        )

        last_messages_map = await (
            self.message_query_service.get_last_messages_from_every_chat_map(
                chat_ids
            )
        )

        chat_overviews = []

        for chat in chats:
            chat_id = chat.chat_id

            message = last_messages_map[chat_id]
            last_message = MessageInChatOverview(
                sent_at=message.sent_at,
                content=message.content,
                display_name=message.display_name
            )

            chat_overviews.append(
                ChatOverview(
                    chat_id=chat_id,
                    name=chat.name,
                    unread_count=unread_counts_map[chat_id],
                    last_message=last_message,
                )
            )

        return chat_overviews
