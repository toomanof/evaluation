import asyncio
from dataclasses import asdict
from aiohttp.web_app import Application
import aio_pika
from aio_pika.abc import AbstractExchange, AbstractRobustChannel, AbstractRobustConnection
from aio_pika import ExchangeType, Message, RobustConnection, Queue
import aiormq
from yarl import URL
from typing import (
    Optional,
    Union,
)
import logging
from core.project.services.broker.schemas import Publisher, Consumer, ConsumerParams

logger = logging.getLogger(__name__)


class RabbitMQBroker:
    """Универсальный класс для брокера RabbitMQ.

     Работает в двух режимах.
     - publisher
     - consumer

    Можно добавить множество консьмеров и паблишеров при помощи методов add_publisher, add_consumer

     URL string might contain ssl parameters e.g.
    `amqps://user:pass@host//?ca_certs=ca.pem&certfile=crt.pem&keyfile=key.pem`
    """

    def __init__(
        self,
        url: Union[str, URL, None],
        *,
        host: str = "localhost",
        port: int = 5672,
        login: str = "guest",
        password: str = "guest",
        virtualhost: str = "/",
    ):
        self.url = url
        self._connection: Optional[RobustConnection] = None
        self.publishers: dict = {}
        self.consumers: dict = {}
        # ** kwargs: Any,

    async def get_connection(self, app: Optional[Application] = None) -> AbstractRobustConnection:
        """Метод, который создает подключение к брокеру.

        Для интеграции с aiohttp нужно добавить в список "on_startup"
        default_broker_object = RabbitMQBroker(url=url, *args, **kwargs)
        app.on_startup.append(default_broker_object.get_connection)
        """
        try:
            self._connection = await aio_pika.connect_robust(
                self.url,
            )
        except (ConnectionError, aiormq.exceptions.IncompatibleProtocolError) as e:
            logger.error(f"action=setup_rabbitmq, status=fail, retry=10s, {e}")
            await asyncio.sleep(10)
            await self.get_connection()
        except Exception as e:
            print(e)

        if app:
            app[self.url] = self._connection
        return self._connection

    async def add_publisher(
        self,
        handler_name: str,
        queue_name: str,
        exchange_name: Optional[str] = None,
    ):
        """Добавить паблишер в брокера.

        handler_name -- название паблишера, должно быть уникальным
        queue_name  -- название очереди
        exchange_name  -- название обменника, опционально, в случае если не указать, будет дефолтный
        """
        channel = await self._create_channel()
        queue = await self._declare_queue(channel, queue_name)
        exchange = await self._declare_exchange(channel, exchange_name)
        if not self.publishers.get(handler_name):
            self.publishers[handler_name] = Publisher(
                channel=channel,
                queue=queue,
                exchange=exchange,
            )
            print(f"ADDED PUBLISHER channel={channel}, queue={queue}, exchange={exchange}")
        else:
            raise Exception(f"publisher with name {handler_name} exists")

    async def add_consumer(
        self, handler_name, queue_name, params: ConsumerParams, exchange_name: Optional[str] = None
    ):
        """
        Добавить консьюмер в брокера.

        Args:
            handler_name: название консьюмера, должно быть уникальным
            queue_name: название очереди, которую нужно слушать
            params: объект класса ConsumerParams из from core.project.services.broker.schemas
            exchange_name: название обменника, опционально, в случае если не указать, будет дефолтный

        Returns:


        Пример:
        from core.project.services.broker.schemas import ConsumerParams
        consumer_params = ConsumerParams(callback=test_callback)

        await main_broker.add_consumer("consumer_1", "test_queue_1", params=consumer_params)
        """
        channel = await self._create_channel()
        queue = await self._declare_queue(channel, queue_name)
        exchange = await self._declare_exchange(channel, exchange_name)
        if not params.callback:
            raise Exception(f"add callback for {handler_name} consumer")
        if not self.consumers.get(handler_name):
            self.consumers[handler_name] = Consumer(channel=channel, queue=queue, exchange=exchange, params=params)
        else:
            raise Exception(f"consumer with name {handler_name} exists")

            # # Запускаем всех консьюмеров
        await self._run_consumer(self.consumers[handler_name])

    async def _create_channel(self):
        """Создать уникальный канал."""
        channel = await self._connection.channel()
        return channel

    @staticmethod
    async def _declare_queue(channel: Optional[AbstractRobustChannel], queue_name: str, **kwargs):
        # Declaring queue
        queue = None
        if queue_name:
            queue = await channel.declare_queue(queue_name, **kwargs)
        return queue

    async def _get_consumer(
        self,
        handler_name: str,
    ) -> Consumer:
        consumer = self.consumers.get(handler_name)
        if not consumer:
            raise Exception("Consumer doesn't exists")
        return consumer

    async def _get_publisher(self, handler_name: str) -> Publisher:
        publisher = self.publishers.get(handler_name)
        if not publisher:
            raise Exception("Publisher doesn't exists")
        return publisher

    # TODO:  добавить интерфейс настройки обменника в методах, которые вызывают _declare_exchange
    @staticmethod
    async def _declare_exchange(
        channel: Optional[AbstractRobustChannel],
        name: str,
        type: Union[ExchangeType, str] = ExchangeType.DIRECT,
        **kwargs,
    ) -> AbstractExchange:
        if name:
            exchange = await channel.declare_exchange(
                name,
                type,
                durable=True,
            )

            return exchange

    async def _run_consumer(self, consumer):
        """Старт зарегистрированного консьюмера"""
        await self.consume(consumer.queue, consumer.params)

    async def publish(self, handler_name: str, message: Message):
        """Паблишер для заранее определенной очереди.

        from core.project.services.broker.utils import convert_pydantic_message_to_aio_pika

        утилита которая может конвертировать pydantic модель в объект Message
        """
        try:
            publisher = await self._get_publisher(handler_name)
            if publisher.exchange:
                await publisher.exchange.publish(
                    message,
                    publisher.exchange.name,
                )
            else:
                await publisher.channel.default_exchange.publish(message, publisher.queue.name)
        except Exception as e:
            logger.error(f"Ошибка во время отправки сообщения. \n {e}")
            print(f"Ошибка во время отправки сообщения. \n {e}")

    async def consume(self, queue: Queue, params: ConsumerParams):
        """Дублер основного метода consume из библиотеки aio_pika. Нужен, чтобы запустить консьюмера для определенной очереди.

        handler_name -- имя консьюмера указанное при добавлении в брокера

        Start to consuming the :class:`Queue`.

        :param timeout: :class:`asyncio.TimeoutError` will be raises when the
                        Future was not finished after this time.
        :param callback: Consuming callback. Should be a coroutine function.
        :param no_ack:
            if :class:`True` you don't need to call
            :func:`aio_pika.message.IncomingMessage.ack`
        :param exclusive:
            Makes this queue exclusive. Exclusive queues may only
            be accessed by the current connection, and are deleted
            when that connection closes. Passive declaration of an
            exclusive queue by other connections are not allowed.
        :param arguments: additional arguments
        :param consumer_tag: optional consumer tag

        :raises asyncio.TimeoutError:
            when the consuming timeout period has elapsed.
        :return str: consumer tag :class:`str`

        """
        try:
            await queue.consume(**asdict(params))
            print(f"Consumer Started on {self.url}: listening queue {queue.name}")
            logger.info(f"Consumer Started on {self.url}: listening queue {queue.name}")
            # await asyncio.Future()
        except Exception as e:
            logger.error(f"Ошибка во время получения сообщения. \n {e}")
            print(f"Ошибка во время получения сообщения. \n {e}")

    async def close_rabbitmq(self, app: Optional[Application] = None) -> None:
        await self._connection.close()
        logger.info("action=close_rabbitmq, status=success")
        print("action=close_rabbitmq, status=success")
