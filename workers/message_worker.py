import asyncio
import json
import aio_pika
import logging

from datetime import datetime, timezone

from logging import getLogger

from app.core.config import settings
from app.db.repository.chat_repository import ChatRepository
from app.db.repository.message_repository import MessageRepository
from app.db.repository.scheduled_message_repository import \
    ScheduledMessageRepository
from app.db.repository.user_repository import UserRepository
from app.db.session import AsyncSessionFactory
from app.models import User, Chat, Message
from app.models.scheduled_message import ScheduledMessage, \
    ScheduledMessageStatus
from app.schemas.message import MessageCreate
from app.services.message_service import MessageService

RABBITMQ_HOST = settings.RABBITMQ_HOST
RABBITMQ_PORT = settings.RABBITMQ_PORT
RABBITMQ_DEFAULT_USER = settings.RABBITMQ_DEFAULT_USER
RABBITMQ_DEFAULT_PASS = settings.RABBITMQ_DEFAULT_PASS
WAITING_QUEUE_NAME = settings.RABBITMQ_WAITING_QUEUE
PROCESSING_QUEUE_NAME = settings.RABBITMQ_PROCESSING_QUEUE

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = getLogger(__name__)


async def _set_message_status_to_failed(
        scheduled_message_db_id: int,
        error_message: str
):
    if not scheduled_message_db_id:
        logger.error('No scheduled message id')
        return
    try:
        async with AsyncSessionFactory() as db_fail_session:
            scheduled_message_repository = ScheduledMessageRepository(
                db_fail_session, ScheduledMessage
            )
            scheduled_message_to_update = await (
                scheduled_message_repository.get_by_id(scheduled_message_db_id)
            )
            if scheduled_message_to_update:
                if scheduled_message_to_update.status not in [
                    ScheduledMessageStatus.SENT,
                    ScheduledMessageStatus.FAILED,
                    ScheduledMessageStatus.CANCELED
                ]:
                    scheduled_message_to_update.status = (
                        ScheduledMessageStatus.FAILED
                    )
                    scheduled_message_to_update.error_message = error_message
                    await db_fail_session.commit()
                    logger.info(f"Scheduled message {scheduled_message_db_id} "
                                f"set to failed")
                else:
                    logger.info(f"Scheduled message {scheduled_message_db_id} "
                                f"is already set to"
                                f"{scheduled_message_to_update.status}"
                                f"no set failed"
                                )
            else:
                logger.error(f"Scheduled message {scheduled_message_db_id} not "
                             f"found to set to failed")
    except Exception as e_db_update:
        logger.error(
            f"CRITICAL: failed to update status to FAILED for "
            f"scheduled_message_id {scheduled_message_db_id}, error: "
            f"{e_db_update}", exc_info=True
        )


async def process_message_logic(raw_message_body: bytes):
    scheduled_message_db_id: int | None = None
    try:
        try:
            message_data = json.loads(raw_message_body.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode message body: "
                         f"{raw_message_body}, error: {e}",
                         exc_info=True
                         )
            raise
        scheduled_message_db_id = message_data.get('scheduled_message_db_id')
        chat_id = message_data.get('chat_id')
        content = message_data.get('content')
        user_id = message_data.get('user_id')

        if not all([chat_id, content, user_id, scheduled_message_db_id]):
            logger.error(f"Invalid message payload: {message_data}")
            raise ValueError(
                "Invalid message payload: missing required fields"
            )

        async with AsyncSessionFactory() as db:
            scheduled_message_repository = ScheduledMessageRepository(
                db, ScheduledMessage
            )
            scheduled_message_in_db: ScheduledMessage | None = await (
                scheduled_message_repository.get_by_id(scheduled_message_db_id)
            )
            if (scheduled_message_in_db.status ==
                    ScheduledMessageStatus.CANCELED):
                logger.info(
                    f"Scheduled message '{scheduled_message_db_id}' canceled"
                )
                return

            if (scheduled_message_in_db.status ==
                    ScheduledMessageStatus.PENDING):
                scheduled_message_in_db.status = (
                    ScheduledMessageStatus.PROCESSING
                )
                await db.commit()

            user_repository = UserRepository(db, User)
            user: User | None = await user_repository.get_by_id(user_id)
            if not user:
                logger.error(
                    f"User with id {user_id} not found. "
                    f"Cannot process message."
                )
                raise ValueError(f"User with id {user_id} not found")

            chat_repository = ChatRepository(db, Chat)
            message_repository = MessageRepository(db, Message)

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

            scheduled_message_in_db.status = ScheduledMessageStatus.SENT

            created_message = await message_service.create_message(
                message_in_schema
            )
            logger.info(f"Message created by worker: "
                        f"{created_message.message_id}")
    except Exception as e:
        logger.error(
            f"Error processing message in worker: {e}",
            exc_info=True
        )
        if scheduled_message_db_id:
            await _set_message_status_to_failed(
                scheduled_message_db_id, str(e)
            )
        else:
            logger.error('Failed to update message status to FAILED'
                         'due to unknown scheduled message id')
        raise


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


async def main():
    connection = None
    logger.info('[*] Worker starting...')

    rabbitmq_url = (f"amqp://{RABBITMQ_DEFAULT_USER}:{RABBITMQ_DEFAULT_PASS}@"
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
