import asyncio
import json
import aio_pika
from datetime import datetime

from logging import getLogger

from app.core.config import settings
from app.db.repository.chat_repository import ChatRepository
from app.db.repository.message_repository import MessageRepository
from app.db.repository.user_repository import UserRepository
from app.db.session import AsyncSessionFactory
from app.models import User, Chat, Message
from app.schemas.message import MessageCreate
from app.services.message_service import MessageService

RABBITMQ_HOST = settings.RABBITMQ_HOST
RABBITMQ_PORT = settings.RABBITMQ_PORT
RABBITMQ_DEFAULT_USER = settings.RABBITMQ_DEFAULT_USER
RABBITMQ_DEFAULT_PASS = settings.RABBITMQ_DEFAULT_PASS
WAITING_QUEUE_NAME = settings.WAITING_QUEUE_NAME
PROCESSING_QUEUE_NAME = settings.PROCESSING_QUEUE_NAME

logger = getLogger(__name__)


async def process_message_logic(raw_message_body: bytes):
    try:
        message_data = json.loads(raw_message_body.decode('utf-8'))
        chat_id = message_data.get('chat_id')
        content = message_data.get('content')
        user_id = message_data.get('user_id')

        if not all([chat_id, content, user_id]):
            logger.error(f"Invalid message payload: {message_data}")
            raise ValueError(
                "Invalid message payload: missing required fields"
            )

        async with AsyncSessionFactory() as db:
            user_repository = UserRepository(db, User)
            chat_repository = ChatRepository(db, Chat)
            message_repository = MessageRepository(db, Message)

            user: User | None = await user_repository.get_by_id(user_id)
            if not user:
                logger.error(
                    f"User with id {user_id} not found. "
                    f"Cannot process message."
                )
                raise ValueError(f"User with id {user_id} not found")

            message_service = MessageService(
                db,
                current_user=user,
                chat_repository=chat_repository,
                message_repository=message_repository,
            )

            message_in_schema = MessageCreate(
                chat_id=chat_id,
                content=content,
            )

            created_message = await message_service.create_message(
                message_in_schema
            )
            logger.info(f"Message created by worker: "
                        f"{created_message.message_id}")

    except json.JSONDecodeError:
        logger.error(f"Failed to decode message body: {raw_message_body}")
        raise
    except Exception as e:
        logger.error(
            f"Error processing message in worker: {e}",
            exc_info=True
        )
        raise


async def on_message(message: aio_pika.IncomingMessage):
    logger.info(f"Received message at {datetime.now().isoformat()}"
                f" (delivery_tag={message.delivery_tag})")

    async with message.process(ignore_processed=True):
        try:
            await process_message_logic(message.body)
            logger.info(f"Message processed successfully"
                        f" (delivery_tag={message.delivery_tag})")
        except Exception:
            logger.warning(f"Message processing failed "
                           f"(delivery_tag={message.delivery_tag})")


async def main():
    connection = None
    logger.info('[*] Worker starting...')

    rabbitmq_url = (f"ampq://{RABBITMQ_DEFAULT_USER}:{RABBITMQ_DEFAULT_PASS}@"
                    f"{RABBITMQ_HOST}:{RABBITMQ_PORT}")
    logger.info(
        f"[*] Connecting to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}"
    )

    while True:
        try:
            connection = await aio_pika.connect_robust(
                rabbitmq_url,
                timeout=10
            )
            logger.info('[*] Connected to RabbitMQ')

            async with connection:
                channel = await connection.channel()
                logger.info("[*] Channel created")

                await channel.set_qos(prefetch_count=1)
                logger.info("[*] QoS set to prefetch_count=1.")

                processing_queue = await channel.declare_queue(
                    PROCESSING_QUEUE_NAME,
                    durable=True
                )
                logger.info(f"[*] Queue '{PROCESSING_QUEUE_NAME}' created")

                logger.info('[*] Starting consumer. Waiting for messages. '
                            'To exit press CTRL+C')

                await processing_queue.consume(on_message)

                await asyncio.Future()

        except (
                aio_pika.exceptions.AMQPConnectionError,
                ConnectionRefusedError,
                asyncio.TimeoutError
        ) as conn_err:
            logger.error(f" [!] Connection/Channel error: {conn_err}. "
                         f"Retrying in 10 seconds...")
            if connection and not connection.is_closed:
                await connection.close()
            await asyncio.sleep(10)
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


if __name__ == '__main__':
    asyncio.run(main())
