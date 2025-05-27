import json
from datetime import timedelta
from logging import getLogger

import aio_pika

from app.core.config import settings
from app.infrastructure.exceptions.exceptions import MessagingConnectionError, InvalidMessageDataError, \
    MessagePublishError
from app.infrastructure.message_queue.rabbitmq_connection_provider import \
    RabbitMQConnectionProvider

RABBITMQ_HOST = settings.RABBITMQ_HOST
RABBITMQ_PORT = settings.RABBITMQ_PORT
RABBITMQ_DEFAULT_USER = settings.RABBITMQ_DEFAULT_USER
RABBITMQ_DEFAULT_PASS = settings.RABBITMQ_DEFAULT_PASS
WAITING_QUEUE_NAME = settings.RABBITMQ_WAITING_QUEUE
PROCESSING_QUEUE_NAME = settings.RABBITMQ_PROCESSING_QUEUE
DLX_NAME = settings.RABBITMQ_DLX_NAME
REGULAR_MESSAGE_QUEUE_NAME = settings.RABBITMQ_REGULAR_MESSAGE_QUEUE


logger = getLogger(__name__)


class RabbitMQClient:
    def __init__(
            self,
            connection_provider = RabbitMQConnectionProvider()
    ):
        self.connection_provider = connection_provider

    async def publish_delayed(self, message_data: dict, delay_seconds: int):
        connection = await self.connection_provider.get_connection()

        try:
            async with connection.channel() as channel:
                dlx_exchange = await channel.declare_exchange(
                    DLX_NAME, aio_pika.ExchangeType.DIRECT, durable=True
                )
                processing_queue = await channel.declare_queue(
                    PROCESSING_QUEUE_NAME, durable=True
                )
                await processing_queue.bind(
                    dlx_exchange,
                    routing_key=WAITING_QUEUE_NAME
                )

                await channel.declare_queue(
                    WAITING_QUEUE_NAME,
                    durable=True,
                    arguments={
                        'x-dead-letter-exchange': DLX_NAME,
                        'x-dead-letter-routing-key': WAITING_QUEUE_NAME
                    }
                )

                message_body = json.dumps(message_data).encode('utf-8')
                delay_ms = int(delay_seconds * 1000)

                if delay_ms < 0:
                    raise ValueError("Delay must be greater than 0")

                message = aio_pika.Message(
                    body=message_body,
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    expiration=timedelta(milliseconds=delay_ms)
                )

                await channel.default_exchange.publish(
                    message,
                    routing_key=WAITING_QUEUE_NAME
                )
                logger.info(f" [x] ASYNC Sent delayed message to queue "
                            f"'{WAITING_QUEUE_NAME}': {message_data} "
                            f"with delay {delay_seconds}s")

        except InvalidMessageDataError as value_error:
            logger.error(f" [x] ASYNC Invalid value for publishing: "
                         f"{value_error}")
            raise MessagingConnectionError(str(value_error))
        except Exception as e:
            logger.error(f" [x] ASYNC Error publishing message: {e}")
            raise MessagePublishError(str(e))
        finally:
            if connection and not connection.is_closed:
                await connection.close()

    async def publish(self, message_data: dict):
        connection = await self.connection_provider.get_connection()
        try:
            async with connection.channel() as channel:
                await channel.declare_queue(
                    REGULAR_MESSAGE_QUEUE_NAME,
                    durable=True
                )

                message = aio_pika.Message(
                    body=json.dumps(message_data).encode('utf-8'),
                )

                await channel.default_exchange.publish(
                    message,
                    routing_key=REGULAR_MESSAGE_QUEUE_NAME
                )
                logger.info(f'message {message_data} sent to mq')
        except InvalidMessageDataError as value_error:
            logger.error(f" [x] ASYNC Invalid value for publishing: "
                         f"{value_error}")
            raise MessagingConnectionError(str(value_error))
        except Exception as e:
            logger.error(f" [x] ASYNC Error publishing message: {e}")
            raise MessagePublishError(str(e))
        finally:
            if connection and not connection.is_closed:
                await connection.close()
