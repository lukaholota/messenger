from app.services.chat.chat_query_service import ChatQueryService


class ChatInfoService:
    def __init__(self, chat_query_service: ChatQueryService):
        self.chat_query_se