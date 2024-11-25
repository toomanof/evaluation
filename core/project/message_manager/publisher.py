import json
import logging

import aio_pika
from aiohttp.abc import Application

from core.project.conf import settings

logger = logging.getLogger("errors")


class Publisher:
    app: Application

    async def __call__(self, app: Application, *args, **kwargs):
        self.app = app
        app[settings.CODE_PUBLISHER] = self
        self.connection = await aio_pika.connect_robust(settings.RABBIT_MQ.get("url"))
        queue_name = settings.RABBIT_MQ.get("queue", "ms_marketplaces")
        self.channel = await self.connection.channel()
        self.queue = await self.channel.declare_queue(queue_name, auto_delete=True)
        yield

    async def publish(self, routing_key: str, msg: dict):
        if not hasattr(self, "connection"):
            return
        channel = await self.connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(body=str.encode(json.dumps(msg, indent=4))),
            routing_key=routing_key,
        )


main_publisher = Publisher()
