from asyncio import get_running_loop
from tenacity import retry, stop_after_attempt, wait_fixed

import aio_pika

from app.core.config import settings

from logging import getLogger

from app.infrastructure.exceptions.exceptions import MessagingConnectionError

logger = getLogger(__name__)

RABBITMQ_HOST = settings.RABBITMQ_HOST
RABBITMQ_PORT = settings.RABBITMQ_PORT
RABBITMQ_DEFAULT_USER = settings.RABBITMQ_DEFAULT_USER
RABBITMQ_DEFAULT_PASS = settings.RABBITMQ_DEFAULT_PASS


class RabbitMQConnectionProvider:
    def __init__(self):
        self._url = (
            f"amqp://{RABBITMQ_DEFAULT_USER}:"
            f"{RABBITMQ_DEFAULT_PASS}@"
            f"{RABBITMQ_HOST}:{RABBITMQ_PORT}"
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        reraise=True
    )
    async def get_connection(self):
        connection = None
        try:
            logger.info(f"Attempting RabbitMQ connection to {self._url}")
            loop = get_running_loop()
            logger.info("RabbitMQ connection successful")
            connection = await aio_pika.connect_robust(self._url, loop=loop)
            return connection
        except aio_pika.exceptions.AMQPConnectionError as connection_error:
            if connection and not connection.is_closed:
                await connection.close()
            logger.error(
                f" [x] Error connecting to RabbitMQ at {self._url}")
            raise MessagingConnectionError(str(connection_error))
