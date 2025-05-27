from app.infrastructure.message_queue.rabbitmq_client import RabbitMQClient


class MessageWebSocketHandler:
    def __init__(self, mq_client: RabbitMQClient):
        self.mq_client = mq_client

    async def send_to_mq(self, user_id, message_in):
        data = {
            "user_id": user_id,
            "chat_id": message_in.chat_id,
            "content": message_in.content,
        }
        await self.mq_client.publish(data)
