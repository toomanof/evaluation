import logging
import aio_pika
import traceback
import json
from aiohttp.abc import Application
from aiormq import ChannelInvalidStateError
from icecream import ic

from core.project.conf import settings
from core.project.types import MsgSendStartEventInMSMarketplace, MsgResponseToPlatform
from core.project.utils import send_response_to_platform, call_event, prepare_response

logger = logging.getLogger("errors")


class Consumer:
    app: Application

    async def __call__(self, app: Application, *args, **kwargs):
        self.app = app
        app[settings.CODE_CONSUMER] = self
        await self._connect_to_rabbitmq()
        yield

    async def _connect_to_rabbitmq(self):
        connection = await aio_pika.connect_robust(settings.RABBIT_MQ.get("url"))
        queue_name = settings.RABBIT_MQ.get("queue", "ms_marketplaces")
        channel = await connection.channel()
        queue = await channel.declare_queue(queue_name, auto_delete=True)
        await queue.consume(self.process_message)

    async def process_message(self, message: aio_pika.abc.AbstractIncomingMessage) -> None:
        async with message.process():
            response = MsgResponseToPlatform()
            response_body = MsgSendStartEventInMSMarketplace(**json.loads(message.body))
            try:
                response = await call_event(app=self.app, body=response_body)()
                assert isinstance(response, MsgResponseToPlatform), "The response should be type MsgResponseToPlatform"

            except ChannelInvalidStateError as err:
                response.traceback = traceback.format_exc()
                response.errors = str(err)
                logger.error(f"{err}\n {response.traceback}")
                ic(f"{err}\n {response.traceback}")
                await self._connect_to_rabbitmq()

            except Exception as err:
                response.traceback = traceback.format_exc()
                response.errors = str(err)
                logger.error(f"{err}\n {response.traceback}")
                ic(f"{err}\n {response.traceback}")
            await self.push_response(response_body, response)

    async def push_response(
        self,
        request_body: MsgSendStartEventInMSMarketplace,
        response_body: MsgResponseToPlatform,
    ):
        if not request_body.callback:
            return
        if request_body.queue:
            return await self.push_response_to_queue(request_body.queue, request_body, response_body)
        return await send_response_to_platform(request_body, response_body)

    async def push_response_to_queue(
        self,
        queue: str,
        request_body: MsgSendStartEventInMSMarketplace,
        response_body: MsgResponseToPlatform,
    ):
        if not response_body.data:
            return
        msg = prepare_response(request_body, response_body)
        publisher = self.app[settings.CODE_PUBLISHER]
        await publisher.publish(queue, msg)


main_consumer = Consumer()
