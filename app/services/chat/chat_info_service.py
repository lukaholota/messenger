from app.schemas.chat import ChatInfo, ChatWithName
from app.schemas.user import UserRead
from app.services.chat.chat_query_service import ChatQueryService


class ChatInfoService:
    def __init__(self, chat_query_service: ChatQueryService):
        self.chat_query_service = chat_query_service

    async def get_chat_info(self, chat_id, user_id):
        data = await self.chat_query_service.get_chat_with_chat_participants(
            chat_id
        )
        chat = data['chat']
        participants = data['participants']
        users = data['users']

        participant_count = len(participants)

        user_chat_name = await self.get_user_chat_name(participants, user_id)

        return ChatInfo(
            chat_id=chat.chat_id,
            chat_name=user_chat_name,
            participant_count=participant_count,
            is_group=chat.is_group,
            participants=[
                UserRead.model_validate(user)
                for user in users
            ]
        )

    async def get_user_chat_name(self, participants, user_id):
        participant_map = {
            participant.user_id: participant
            for participant in participants
        }
        return participant_map[user_id].chat_name

    async def construct_chat_info(
            self, chat_with_name: ChatWithName, user_id: int
    ) -> ChatInfo:
        chat = chat_with_name.chat
        participants = chat.participants

        return ChatInfo(
            chat_id=chat.chat_id,
            chat_name=chat_with_name.chat_name,
            participant_count=len(participants),
            is_group=chat.is_group,
            participants=[
                UserRead.model_validate(user)
                for user in participants
            ]
        )