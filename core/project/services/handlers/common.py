import asyncio
import logging
import traceback
from abc import ABC
from typing import Type, Any, Collection
from aiohttp import ClientSession
from aiohttp.abc import Application
from asyncio import Semaphore
from datetime import datetime
from icecream import ic
from pydantic import BaseModel


from core.apps.basic.types.from_platform import MarketplaceWithHeader, EventInMSMarketplace
from core.project.conf import settings
from core.project.constants import FORMAT_DATE, SECONDS_IN_DAY
from core.project.services.database_workers import DBHandler
from core.project.services.requesters import AppRequester
from core.project.types import (
    MsgSendStartEventInMSMarketplace,
    MsgResponseToPlatform,
    ParamsView,
    URLParameterSchema,
)
from core.project.utils import (
    deserialize,
    get_random_text,
    fetch_companies_with_header,
    call_event,
    send_response_to_platform,
)

logger = logging.getLogger("errors")


class AbstractHandler(ABC):
    app: Application
    session: ClientSession
    semaphore: Semaphore
    body: MsgSendStartEventInMSMarketplace

    async def __fetch__(self, *args, **kwargs):
        raise NotImplementedError()

    async def execute(self):
        raise NotImplementedError()

    def get_data_from_response_data(self, data: Any):
        raise NotImplementedError()

    @staticmethod
    def response_data_to_dict(data: Any):
        raise NotImplementedError()


class ApplicationHandler(AbstractHandler):
    def __init__(self, app: Application, body: MsgSendStartEventInMSMarketplace, test: bool = False):
        self.semaphore = Semaphore(10)
        self.app = app
        self.body = body
        self.test = test


class RequestHandler(ApplicationHandler):
    async def __fetch__(
        self,
        class_requester: Type[AppRequester],
        url_schema: URLParameterSchema,
        class_db_handler: Type[DBHandler] = None,
        urls_and_params: Collection[tuple[URLParameterSchema, dict | None]] | None = None,
        additional_info_for_request=None,
    ):
        if class_db_handler:
            db_handler = class_db_handler(
                pool=self.app[settings.DEFAULT_DATABASE],
                params=ParamsView(
                    marketplace_id=self.body.marketplace_id,
                    company_id=self.body.company_id,
                ),
            )
        else:
            db_handler = None

        requester = class_requester(
            app=self.app,
            session=self.app["session"],
            semaphore=self.semaphore,
            request_body=self.body,
            url_schema=url_schema,
            additional_info=additional_info_for_request,
            test=self.test,
        )
        result = await self.fetch_from(
            requester=requester,
            db_handler=db_handler,
            url_schema=url_schema,
            urls_and_params=urls_and_params,
        )
        return self.prepare_data_to_response(data=result, errors=requester.errors)

    @staticmethod
    def prepare_data_to_response(data, errors):
        return MsgResponseToPlatform(data=data, errors=errors)

    async def fetch_from(
        self,
        requester: AppRequester,
        url_schema: URLParameterSchema,
        db_handler: DBHandler = None,
        urls_and_params: Collection[tuple[URLParameterSchema, dict | None]] | None = None,
    ) -> Collection[dict]:
        if (
            db_handler
            and self.body.cached
            and await self.fetch_store_cache_is_valid(db_handler, url_schema.cache_expires_in)
        ):
            items = [deserialize(item.get("json_data")) for item in await db_handler.all() if item.get("json_data")]
        else:
            items = await requester.fetch(urls_and_params)
            if not items:
                return []
            items = self.get_data_from_response_data(items)
            if db_handler:
                await db_handler.insert_or_update(items)
            items = self.response_data_to_dict(items)

        return items

    @staticmethod
    async def fetch_store_cache_is_valid(db_handler: DBHandler, cache_expires_in: int) -> bool:
        str_last_fetch = await db_handler.get_datetime_last_fetch()
        if not str_last_fetch:
            return False
        now = datetime.now()
        last_fetch = datetime.strptime(str_last_fetch, FORMAT_DATE)
        difference = now - last_fetch
        return (difference.days * SECONDS_IN_DAY + difference.seconds) <= cache_expires_in

    @staticmethod
    def response_data_to_dict(data: Any):
        return list(map(BaseModel.model_dump, data))


class AbstractBulkHandler(ABC):
    async def execute(self):
        raise NotImplementedError()


class BulkHandler(AbstractBulkHandler):
    app: Application
    event: EventInMSMarketplace
    targets: Collection[MarketplaceWithHeader]

    async def __call__(self, app: Application, *args, **kwargs):
        self.app = app
        await self.execute()

    async def create_events(self, event: EventInMSMarketplace):
        self.targets = await fetch_companies_with_header()
        return [
            MsgSendStartEventInMSMarketplace(
                headers=target.headers,
                marketplace_id=target.id,
                company_id=target.company.id,
                customer_id=target.company.owner,
                event=event.value,
                event_id=get_random_text(),
                callback=f"result_{event.value}",
                queue="wildberries",
                token="",
            )
            for target in self.targets
        ]

    async def execute(self):
        pending_tasks = []
        for response_body in await self.create_events(self.event):
            pending_tasks.append(asyncio.create_task(self.execute_single_event(response_body)))
        if not pending_tasks:
            return
        await asyncio.wait(pending_tasks)

    async def execute_single_event(self, response_body: MsgSendStartEventInMSMarketplace):
        response = MsgResponseToPlatform()
        try:
            response = await call_event(app=self.app, body=response_body)()
            assert isinstance(response, MsgResponseToPlatform), "The response should be type MsgResponseToPlatform"
        except Exception as err:
            response.traceback = traceback.format_exc()
            response.errors = str(err)
            logger.error(f"{err}\n {response.traceback}")
            ic(f"{err}\n {response.traceback}")
        await self.push_response(response_body, response)

    @staticmethod
    async def push_response(
        request_body: MsgSendStartEventInMSMarketplace,
        response_body: MsgResponseToPlatform,
    ):
        if not request_body.callback:
            return
        return await send_response_to_platform(request_body, response_body)
