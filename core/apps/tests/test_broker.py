from core.project.utils import time_of_completion
import pytest
import aio_pika

from core.apps.basic.utils import send_message_to_stocks_microservice
from core.project.services.broker.schemas import ConsumerParams
from core.project.services.broker import main_broker
from core.project.services.broker.utils import convert_pydantic_message_to_aio_pika


@pytest.mark.skip(reason="для локально проверки. Для CI на данный момент не актуален")
@pytest.mark.asyncio
@time_of_completion
async def test_stocks_rabbit_broker_publish(random_pydantic_model_message):
    """Тестируем возможность RabbitMQBroker отправить сообщение в очередь stock microservice при помощи метода send_message_to_stocks_microservice."""

    async def test_callback(message: aio_pika.abc.AbstractIncomingMessage):
        assert message.body_size > 0

    consumer_params = ConsumerParams(callback=test_callback)

    await main_broker.get_connection()
    await main_broker.add_consumer("test_stock_publishing", "stock_test", params=consumer_params)
    await main_broker.add_publisher("stock_publisher", "stock_test")
    # Отправить любой рандомный pydantic объект
    await send_message_to_stocks_microservice(random_pydantic_model_message)

    # Закрыть соединение с брокером
    await main_broker.close_rabbitmq()


@pytest.mark.skip(reason="для локально проверки. Для CI на данный момент не актуален")
@pytest.mark.asyncio
@time_of_completion
async def test_run_many_consumers(random_pydantic_model_message):
    """Тестируем возможность RabbitMQBroker запустить несколько консьюмеров."""

    async def test_callback(message: aio_pika.abc.AbstractIncomingMessage):
        print("message", message)
        print(message.body)
        assert message.body_size > 0

    consumer_params = ConsumerParams(callback=test_callback)
    aio_pika_message = convert_pydantic_message_to_aio_pika(random_pydantic_model_message)
    await main_broker.get_connection()
    await main_broker.add_consumer("consumer_1", "test_queue_1", params=consumer_params)
    await main_broker.add_consumer("consumer_2", "test_queue_2", params=consumer_params)

    await main_broker.add_publisher("publisher_1", "test_queue_1")
    await main_broker.add_publisher("publisher_2", "test_queue_2")

    await main_broker.publish("publisher_1", aio_pika_message)
    await main_broker.publish("publisher_2", aio_pika_message)
    await main_broker.close_rabbitmq()
