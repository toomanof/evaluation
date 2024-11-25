import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Collection, Optional, TypeVar, Generic

from dateutil.relativedelta import relativedelta
from pydantic import ValidationError

from core.project.types import URLParameterSchema
from core.apps.basic.request_urls.wildberries import (
    URL_GET_ORDERS_WILDBERRIES_V3,
    URL_GET_ORDERS_WILDBERRIES_V1,
    URL_GET_ORDERS_STATUS_WILDBERRIES_V3,
    URL_GET_NEW_ORDERS_WILDBERRIES_V3,
    URL_GET_BARCODE_ORDERS_WILDBERRIES_V3,
)
from core.apps.basic.services.handlers.sales import SalesHandler
from core.apps.basic.services.requesters.goods import NomenclatureRequest
from core.apps.basic.types import (
    WBRequestBodyFBOOrders,
    WBResponse,
    WBRequestBodyFBSOrders,
    WBFBSOrder,
    WBFBOOrder,
    WBRequestBodyOrdersStatus,
    WBOrdersStickersQueryParams,
    WBRequestBodyOrdersWithParamsStickers,
)
from core.apps.constants import (
    COUNT_ITEMS_ONE_ITERATION_CREATE_OR_UPDATE_CARDS_V2,
)
from core.project.constants import DATETIME_TEMPLATE_MSC
from core.project.services.requesters import AppRequester
from core.project.utils import datetime2int_timestamp

logger_error = logging.getLogger("errors")
logger_info = logging.getLogger("info")

T = TypeVar("T")


class MixinAddNomenclature(NomenclatureRequest):
    async def add_nomenclature(self, fbs_orders: Collection[WBFBSOrder | WBFBOOrder]):
        if not fbs_orders:
            return
        nomenclatures = await self.fetch_nomenclature()
        for nomenclature in nomenclatures:
            orders = list(filter(lambda x: x.nmId == nomenclature.nmID, fbs_orders))
            for order in orders:
                order.nomenclature = nomenclature.title


class FBSNewOrderRequester(MixinAddNomenclature, AppRequester):
    async def fetch(self):
        response = await self.make_single_api_request(urls_and_params=(self.url_schema, None))
        if not response:
            return []
        result = response.orders
        # await self.add_nomenclature(result)  # Временно отключено. Пока нет необходимости в этом.
        return result


class FBSOrderRequester(MixinAddNomenclature, AppRequester):
    @staticmethod
    def clear_double(fbs_orders: list[WBFBSOrder]):
        result = []
        id_orders = []
        for item in fbs_orders:
            if item.id_order in id_orders:
                continue
            result.append(item)
            id_orders.append(item.id_order)
        return result

    async def fetch(self):
        orders = await self.fetch_orders()
        statuses = await self.fetch_statuses_orders(orders)
        orders = self.merge_orders_and_status(orders, statuses)
        # await self.add_nomenclature(orders)  # Временно отключено. Пока нет необходимости в этом.
        return orders

    async def fetch_orders(self):
        result = await self.fetch_old_orders()
        new_orders = await self.fetch_new_orders()
        if new_orders:
            result.extend(new_orders)
        cleaned_result = self.clear_double(result)
        return cleaned_result

    async def fetch_old_orders(self) -> list[WBFBSOrder]:
        until_days = 5
        date_to = datetime.now()
        result = []
        date_from = date_to - timedelta(days=until_days)
        result_per_day = await self.fetch_per_day(
            datetime2int_timestamp(date_from),
            datetime2int_timestamp(date_to),
        )
        result.extend(result_per_day)
        return result

    async def fetch_per_day(
        self,
        date_from: int,
        date_to: int,
    ) -> list[WBFBSOrder]:
        result = []
        is_next_page = True
        next_page = 0
        while is_next_page:
            params = WBRequestBodyFBSOrders(
                limit=1000,
                next=next_page,
                dateTo=date_to,
                dateFrom=date_from,
            )
            response = await self.make_single_api_request(
                urls_and_params=(self.url_schema, params.model_dump(exclude_none=True, exclude_unset=True))
            )
            if not response:
                break
            next_page = response.next
            is_next_page = next_page > 0
            result.extend(response.orders)
        return result

    async def fetch_statuses_orders(self, orders: list[WBFBSOrder]):
        result = []
        requester = StatusOrderRequester(
            app=self.app,
            semaphore=self.semaphore,
            session=self.session,
            request_body=self.request_body,
            url_schema=URL_GET_ORDERS_STATUS_WILDBERRIES_V3,
            ids_orders=[order.id_order for order in orders],
        )
        response = await requester.fetch()
        for item in response:
            result.extend(item.orders)

        return result

    async def fetch_orders_stickers(self, orders: list[WBFBSOrder]):
        # Формируем структуру для запроса для получения стикеров
        orders_ids = [order.id_order for order in orders]
        data = WBRequestBodyOrdersWithParamsStickers(orders=orders_ids)

        request_body = self.request_body.model_copy(update={"data": data})
        requester = OrdersStickersRequester(
            app=self.app, request_body=request_body, semaphore=self.semaphore, session=self.session
        )
        return await requester.fetch_stickers()

    async def fetch_new_orders(self) -> list[WBFBSOrder]:
        requester = FBSNewOrderRequester(
            app=self.app,
            semaphore=self.semaphore,
            session=self.session,
            request_body=self.request_body,
            url_schema=URL_GET_NEW_ORDERS_WILDBERRIES_V3,
        )
        return await requester.fetch()

    @staticmethod
    def merge_orders_and_status(orders: list[WBFBSOrder], status_orders: list) -> list[WBFBSOrder]:
        statuses_dict = {
            status.get("id"): {
                "wbStatus": status.get("wbStatus"),
                "supplierStatus": status.get("supplierStatus"),
            }
            for status in status_orders
        }

        for order in orders:
            single_status = statuses_dict.get(order.id_order)
            if not single_status:
                continue
            order.wbStatus = single_status.get("wbStatus")
            order.supplierStatus = single_status.get("supplierStatus")

        return orders


class FBOOrderRequester(MixinAddNomenclature, AppRequester):
    async def fetch(self):
        # Изменяем период, если приходит как дополнительная информация
        period = 4
        if self.request_body.add_info and self.request_body.add_info.get("period"):
            period = self.request_body.add_info.get("period")

        date_from = (datetime.today() + relativedelta(days=-period)).strftime(DATETIME_TEMPLATE_MSC)
        params = WBRequestBodyFBOOrders(dateFrom=date_from, flag=0).model_dump(exclude_none=True, exclude_unset=True)
        response = await self.make_single_api_request(urls_and_params=(self.url_schema, params))
        if not response:
            return []
        result = await self.merge_orders_and_status(response.root)
        return result

    async def merge_orders_and_status(self, orders: list[WBFBOOrder]):
        handler = SalesHandler(app=self.app, body=self.request_body)
        result = await handler.execute()
        if not result.data:
            return []

        sales = result.data
        statuses_dict = {
            single_sales.get("srid"): {
                "wbStatus": "sold" if single_sales.get("saleID", "").startswith("S") else "declined_by_client",
                "supplierStatus": "",
            }
            for single_sales in sales
        }

        for order in orders:
            if order.isCancel:
                order.wbStatus = "canceled"
                continue

            single_status = statuses_dict.get(order.srid)
            if not single_status:
                continue
            order.wbStatus = single_status.get("wbStatus")
            order.supplierStatus = single_status.get("supplierStatus")
        return orders


@dataclass
class StatusOrderRequester(AppRequester):
    ids_orders: Optional[Collection[int]] = field(default_factory=list)

    @staticmethod
    def prepare_params_for_request_statuses(
        items: Collection[int],
        start_index: int,
        stop_index: int,
        errors: list[dict],
        **additional_params,
    ):
        items_single_iteration = list(filter(lambda x: bool(x), items[start_index:stop_index]))
        try:
            result = WBRequestBodyOrdersStatus(orders=items_single_iteration).model_dump(
                exclude_unset=True, exclude_none=True
            )
        except ValidationError as err:
            errors.append(WBResponse(error=True, errorText=str(err)).model_dump())
            logger_error.error(err, exc_info=True, stack_info=True)
            raise err
        return result

    async def fetch(self):
        if not self.ids_orders:
            return []
        tasks = self._prepare_tasks_for_cycle_request(
            items=self.ids_orders,
            count_items_one_iteration=COUNT_ITEMS_ONE_ITERATION_CREATE_OR_UPDATE_CARDS_V2,
            func_prepare_params=self.prepare_params_for_request_statuses,
            url_schema=self.url_schema,
        )
        result = await self.execute_and_process_api_tasks(api_request_tasks=tasks)
        return result


class OrderRequester(AppRequester):
    @staticmethod
    def clear_duplicate_fbs_from_statistic_orders(
        fbs_orders: Collection[WBFBSOrder], statistic_orders: Collection[WBFBOOrder]
    ) -> list[WBFBOOrder]:
        rids = set(fbs_order.rid for fbs_order in fbs_orders)
        return list(filter(lambda order: order.srid not in rids, statistic_orders))

    async def fetch_orders_any_type(self, class_requester: Generic[T], url_params: URLParameterSchema, **kwargs):
        requester = class_requester(
            app=self.app,
            semaphore=self.semaphore,
            session=self.session,
            request_body=self.request_body,
            url_schema=url_params,
            **kwargs,
        )
        return await requester.fetch()

    async def fetch_fbs_orders(self) -> list[WBFBSOrder]:
        return await self.fetch_orders_any_type(FBSOrderRequester, URL_GET_ORDERS_WILDBERRIES_V3)

    async def fetch_orders_from_statistic_method(self) -> list[WBFBOOrder]:
        return await self.fetch_orders_any_type(FBOOrderRequester, URL_GET_ORDERS_WILDBERRIES_V1)

    async def fetch(self, *args, **kwargs):
        fbs_orders = await self.fetch_fbs_orders()
        orders_from_statistic_method = await self.fetch_orders_from_statistic_method()
        self.substitute_data_into_fbs_from_fbo_orders(fbs_orders, orders_from_statistic_method)
        fbo_orders = self.clear_duplicate_fbs_from_statistic_orders(fbs_orders, orders_from_statistic_method)
        result = []
        result.extend(fbs_orders)
        result.extend(fbo_orders)
        return result

    @staticmethod
    def substitute_data_into_fbs_from_fbo_orders(
        fbs_orders: Collection[WBFBSOrder], fbo_orders: Collection[WBFBOOrder]
    ) -> tuple[int, int]:
        number_fbs_orders_changed = 0
        rids = set(fbs_order.rid for fbs_order in fbs_orders)
        target_orders = list(filter(lambda item: item.srid in rids, fbo_orders))
        for fbo_order in target_orders:
            for fbs_order in fbs_orders:
                if fbo_order.srid == fbs_order.rid:
                    fbs_order.discountPercent = fbo_order.discountPercent
                    fbs_order.spp = fbo_order.spp
                    fbs_order.finishedPrice = fbo_order.finishedPrice
                    fbs_order.priceWithDisc = fbo_order.priceWithDisc
                    fbs_order.statistics = fbo_order.model_dump()
                    number_fbs_orders_changed += 1
        return len(target_orders), number_fbs_orders_changed


class OrdersStickersRequester(AppRequester):
    async def fetch_stickers(self, **kwargs):
        query_params = self._get_query_params_from_request_body(pydantic_schema=WBOrdersStickersQueryParams)
        requester = AppRequester(
            app=self.app,
            semaphore=self.semaphore,
            session=self.session,
            request_body=self.request_body,
            url_schema=URL_GET_BARCODE_ORDERS_WILDBERRIES_V3,
            **kwargs,
        )
        return await requester.make_single_api_request(
            urls_and_params=(URL_GET_BARCODE_ORDERS_WILDBERRIES_V3, query_params)
        )

    # async def fetch(self, *args, **kwargs):
    #     result = await self.fetch_stickers()
    #     return result
