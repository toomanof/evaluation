from typing import TypeVar, Generic

from core.apps.basic.request_urls.wildberries import (
    URL_EXPORT_PRICES_AND_DISCOUNTS,
    URL_DOWNLOAD_PROCESSED_STATUS,
    URL_PROCESSED_LOAD_DETAILS,
    URL_RAW_LOAD_DETAILS,
    URL_RAW_LOAD_PROGRESS,
)
from core.apps.basic.services.requesters.prices_and_discounts import (
    PricesAndDiscountsRequester,
    DownloadProcessedStatusRequester,
    ProcessedLoadDetailsRequester,
    RawLoadDetailsRequester,
    RawLoadProgressRequester,
)
from core.project.services.handlers.common import RequestHandler
from core.project.types import MsgResponseToPlatform, URLParameterSchema

T = TypeVar("T")


class PricesAndDiscountsHandler(RequestHandler):
    async def _execute_method(self, requester_cls: Generic[T], urls_params: URLParameterSchema):
        requester = requester_cls(
            app=self.app,
            session=self.app["session"],
            semaphore=self.semaphore,
            request_body=self.body,
            url_schema=urls_params,
            test=self.test,
        )
        result = await requester.execute()
        return self.prepare_data_to_response(data=result, errors=requester.errors)

    async def _execute(self, method: str, requester_cls: Generic[T]) -> MsgResponseToPlatform:
        requester = requester_cls(
            app=self.app,
            session=self.app["session"],
            semaphore=self.semaphore,
            request_body=self.body,
        )
        return await getattr(requester, method)()

    async def export_price_and_discounts(self) -> MsgResponseToPlatform:
        return await self._execute_method(PricesAndDiscountsRequester, URL_EXPORT_PRICES_AND_DISCOUNTS)

    async def download_processed_status(self) -> MsgResponseToPlatform:
        return await self._execute_method(DownloadProcessedStatusRequester, URL_DOWNLOAD_PROCESSED_STATUS)

    async def processed_load_details(self) -> MsgResponseToPlatform:
        return await self._execute_method(ProcessedLoadDetailsRequester, URL_PROCESSED_LOAD_DETAILS)

    async def raw_load_detail(self) -> MsgResponseToPlatform:
        return await self._execute_method(RawLoadDetailsRequester, URL_RAW_LOAD_DETAILS)

    async def raw_load_progress(self) -> MsgResponseToPlatform:
        return await self._execute_method(RawLoadProgressRequester, URL_RAW_LOAD_PROGRESS)
