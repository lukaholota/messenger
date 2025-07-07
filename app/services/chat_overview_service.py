from datetime import datetime
from typing import List

from app.schemas.chat import ChatOverview, ChatWithName
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
            self,
            user_id: int,
            chats: list[ChatWithName],
            chat_ids: list[int]
    ) -> List[ChatOverview]:

        unread_counts_map = await (
            self.message_delivery_service.get_unread_counts_map(
                user_id, chat_ids
            )
        )

        last_messages_map = await (
            self.message_query_service.get_last_messages_from_every_chat_map(
                chat_ids
            )
        )

        chat_overviews = []

        for chat_with_name in chats:
            chat_name = chat_with_name.chat_name
            chat_id = chat_with_name.chat.chat_id


            message_data = last_messages_map.get(chat_id)
            last_message = None

            if message_data:
                last_message = MessageInChatOverview(
                    sent_at=message_data['message'].sent_at,
                    content=message_data['message'].content,
                    display_name=message_data['display_name']
                )

            chat_overviews.append(
                ChatOverview(
                    chat_id=chat_id,
                    chat_name=chat_name,
                    unread_count=unread_counts_map[chat_id],
                    last_message=last_message,
                )
            )

        chat_overviews.sort(
            key=lambda co: co.last_message.sent_at
            if co.last_message else datetime.min,
            reverse=True
        )
        return chat_overviews
