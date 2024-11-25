from core.project.services.broker.rabbit import RabbitMQBroker
from core.project.conf import settings
from aiohttp.abc import Application


main_broker = RabbitMQBroker(
    url=settings.RABBIT_MQ.get("url"),
)


async def run_main_broker(app: Application):
    connection = await main_broker.get_connection(app)
    async with connection:
        # Добавляем паблишера для микросервиса "отслеживание остатков"
        await main_broker.add_publisher("stock_publisher", settings.STOCK_QUEUE_PUBLISHER)
