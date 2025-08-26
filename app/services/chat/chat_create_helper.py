import json

from app.infrastructure.cache.redis_pubsub import RedisPubSub
from app.schemas.chat import ChatCreate, ChatOverview, ChatInfo
from app.schemas.event import NewChatSentEvent
from app.services.chat.chat_info_service import ChatInfoService
from app.services.chat.chat_service import ChatService


class ChatCreateHelper:
    def __init__(
            self,
            chat_service: ChatService,
            pubsub: RedisPubSub,
            chat_info_service: ChatInfoService
    ):
        self.chat_service = chat_service
        self.pubsub = pubsub
        self.chat_info_service = chat_info_service

    async def init_new_chat(self, chat_in: ChatCreate, user_id) -> ChatInfo:
        chat_with_name = await self.chat_service.create_chat_in_db(
            chat_in, user_id
        )

        for participant_id in chat_in.participant_ids:
            chat_overview_dict = ChatOverview(
                chat_id=chat_with_name.chat.chat_id,
                chat_name=chat_with_name.chat_name,
                unread_count=0,
                last_message=None
            ).model_dump(mode='json')

            redis_event = NewChatSentEvent(
                data=chat_overview_dict
            ).model_dump(mode='json')

            event_json = json.dumps(redis_event)

            await self.pubsub.publish(
                f'user:{participant_id}',
                event_json,
            )

        chat_info = await self.chat_info_service.construct_chat_info(
            chat_with_name, user_id
        )

        return chat_info