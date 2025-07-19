import asyncio
import json
import aio_pika
import logging

from datetime import datetime, timezone

from logging import getLogger

from app.core.config import settings
from app.db.repository.chat_repository import ChatRepository
from app.db.repository.message_delivery_repository import \
    MessageDeliveryRepository
from app.db.repository.message_repository import MessageRepository
from app.db.repository.user_repository import UserRepository

from app.db.session import AsyncSessionFactory
from app.infrastructure.cache.connection import get_redis_client
from app.infrastructure.cache.redis_pubsub import RedisPubSub
from app.infrastructure.message_queue.rabbitmq_connection_provider import \
    RabbitMQConnectionProvider
from app.models import Chat, Message, MessageDelivery, User

from app.schemas.message import MessageCreate, ChatMessage
from app.services.message_delivery_service import MessageDeliveryService
from app.services.message.message_service import MessageService

RABBITMQ_HOST = settings.RABBITMQ_HOST
RABBITMQ_PORT = settings.RABBITMQ_PORT
RABBITMQ_DEFAULT_USER = settings.RABBITMQ_DEFAULT_USER
RABBITMQ_DEFAULT_PASS = settings.RABBITMQ_DEFAULT_PASS
REGULAR_MESSAGE_QUEUE_NAME = settings.RABBITMQ_REGULAR_MESSAGE_QUEUE


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = getLogger(__name__)

redis_pubsub: RedisPubSub | None = None


async def main():
    global redis_pubsub
    redis_pubsub = await get_redis_pubsub()
    logger.info('[*] Worker starting...')
    connection = await RabbitMQConnectionProvider().get_connection()
    while True:
        try:
            async with connection:
                channel = await connection.channel()
                logger.info("[*] Channel created")

                await channel.set_qos(prefetch_count=1)
                logger.info("[*] QoS set to prefetch_count=1.")

                regular_message_queue = await channel.declare_queue(
                    REGULAR_MESSAGE_QUEUE_NAME,
                    durable=True
                )
                logger.info(f"[*] Queue '{REGULAR_MESSAGE_QUEUE_NAME}' "
                            f"created")

                logger.info('[*] Starting consumer. Waiting for messages. '
                            'To exit press CTRL+C')

                await regular_message_queue.consume(on_message)

                await asyncio.Future()
        except KeyboardInterrupt:
            logger.info(' [*] Interrupted by user (CTRL+C). Shutting down...')
            break
        except Exception as e:
            logger.error(f" [!] Unexpected error in main worker loop: "
                         f"{e}", exc_info=True)
            await asyncio.sleep(5)

            logger.info("Attempting to recover...")
            if connection and not connection.is_closed:
                await connection.close()
            await asyncio.sleep(10)


        finally:
            if connection and not connection.is_closed:
                await connection.close()
                logger.info('[*] RabbitMQ Connection closed.')
            logger.info(" [*] Worker loop iteration finished")

        logger.info(" [*] Worker stopped")


async def get_redis_pubsub() -> RedisPubSub:
    redis = await get_redis_client()
    return RedisPubSub(redis)


async def on_message(message: aio_pika.IncomingMessage):
    logger.info(f"Received message at {datetime.now(timezone.utc).isoformat()}"
                f" (delivery_tag={message.delivery_tag})")

    async with message.process(ignore_processed=True):
        try:
            await process_message_logic(message.body)
            logger.info(f"Message processed successfully"
                        f" (delivery_tag={message.delivery_tag})")
        except Exception:
            logger.warning(f"Message processing failed "
                           f"(delivery_tag={message.delivery_tag})")


async def process_message_logic(raw_message_body: bytes):
    global redis_pubsub
    try:
        try:
            message_data = json.loads(raw_message_body.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode message body: "
                         f"{raw_message_body}, error: {e}",
                         exc_info=True
                         )
            raise
        chat_id = message_data.get('chat_id')
        content = message_data.get('content')
        user_id = message_data.get('user_id')

        if not all([chat_id, content, user_id]):
            logger.error(f"Invalid message payload: {message_data}")
            raise ValueError(
                "Invalid message payload: missing required fields"
            )

        async with AsyncSessionFactory() as db:
            chat_repository = ChatRepository(db, Chat)
            message_repository = MessageRepository(db, Message)
            message_delivery_repository = MessageDeliveryRepository(
                db, MessageDelivery
            )
            user_repository = UserRepository(db, User)

            message_delivery_service = MessageDeliveryService(
                db=db,
                message_delivery_repository=message_delivery_repository,
            )

            message_service = MessageService(
                db,
                current_user_id=user_id,
                chat_repository=chat_repository,
                message_repository=message_repository,
                message_delivery_service=message_delivery_service
            )

            message_in = MessageCreate(
                chat_id=chat_id,
                content=content,
            )

            created_message = await message_service.create_message(
                message_in
            )
            logger.info(f"Message created by worker: "
                        f"{created_message.message_id}")

            sender = await user_repository.get_by_id(user_id)

            data = ChatMessage(
                message_id=created_message.message_id,
                user_id=created_message.user_id,
                chat_id=created_message.chat_id,
                content=created_message.content,
                sent_at=created_message.sent_at.isoformat(),
                display_name=sender.display_name
            ).model_dump(mode='json')
            print(data)

            await redis_pubsub.publish(f'chat:{chat_id}', json.dumps({
                'event': 'message_sent',
                'data': data
            }))

            logger.info(f'published message {data} to channel "chat:{chat_id}"'
                        )

    except Exception as e:
        logger.error(
            f"Error processing message in worker: {e}",
            exc_info=True
        )
        raise


if __name__ == '__main__':
    asyncio.run(main())
