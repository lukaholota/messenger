from app.db.repository.message_repository import MessageRepository


class MessageQueryService:
    def __init__(self, message_repository: MessageRepository):
        self.message_repository = message_repository

    async def get_last_messages_from_every_chat_map(
            self, chat_ids: list[int]):
        messages = await (
            self.message_repository.get_last_messages_from_every_chat(
            chat_ids=chat_ids,
        ))

        return {
            message.chat_id: message for message in messages
        }
