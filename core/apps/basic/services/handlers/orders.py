import asyncio
import logging
import traceback
from typing import Collection, Callable

from aiohttp.web_app import Application
from icecream import ic
from prometheus_async.aio import time
from pydantic import ValidationError
from prometheus_client import Gauge, Histogram

from core.apps.basic.services.database_workers.orders import OrderDBHandler
from core.apps.basic.services.handlers.sales import SalesHandler, SalesReportHandler
from core.apps.basic.services.requesters.orders import OrderRequester
from core.apps.basic.types import WBFBSOrder, WBFBOOrder
from core.apps.basic.types.from_platform import (
    ResponseRelationProduct,
    RelationProduct,
    ResponseChangeStatusOrderFromMs,
    StatusOrderWildberries,
    EventInMSMarketplace,
)

from core.apps.constants import MATCHING_MARKETPLACE_STATUS_ORDER
from core.project.conf import settings
from core.project.services.handlers.common import RequestHandler, BulkHandler
from core.project.types import (
    MsgResponseToPlatform,
    MsgSendStartEventInMSMarketplace,
    ParamsView,
)
from core.project.utils import fetch_collection_from_platform


logger_error = logging.getLogger("errors")
logger_info = logging.getLogger("info")


s = Gauge("ms_wb_orders", "Count orders in WB")
REQ_TIME = Histogram("ms_wb_orders_time_seconds", "Time spent in import orders.")


async def reset_metric():
    # NOTE: блочит запрос
    await asyncio.sleep(1)
    s.set_function(lambda: 0)


class OrdersHandler(RequestHandler):
    db_handler: OrderDBHandler = None
    errors: list[dict] = []

    def __init__(self, app: Application, body: MsgSendStartEventInMSMarketplace):
        super().__init__(app, body)
        self.order_requester = OrderRequester(
            app=self.app,
            semaphore=self.semaphore,
            session=self.app["session"],
            request_body=self.body,
        )

    async def __fetch__(self, *args, **kwargs):
        raise NotImplementedError()

    @staticmethod
    def _registration_metrics(count_items: int):
        s.set_function(lambda: count_items)

    @staticmethod
    def clear_duplicate_orders(orders: Collection[WBFBSOrder | WBFBOOrder]) -> Collection[WBFBSOrder | WBFBOOrder]:
        result: list[WBFBSOrder | WBFBOOrder] = []
        set_mp_ids = set()
        for order in orders:
            if hasattr(order, "rid") and order.rid not in set_mp_ids:
                set_mp_ids.add(order.rid)
                result.append(order)
            if hasattr(order, "srid") and order.srid not in set_mp_ids:
                set_mp_ids.add(order.srid)
                result.append(order)

        return result

    @time(REQ_TIME)
    async def execute(self) -> MsgResponseToPlatform:
        products_from_platform = await self.fetch_relation_products()
        ic(f"After products_from_platform {self.body.marketplace_id=} , {len(products_from_platform)=}")
        orders = await self.fetch_orders()
        ic(f"After import orders {self.body.marketplace_id=} , {len(orders)=}")
        orders = self.matching_products_from_platform_with_orders(orders, products_from_platform)
        ic(f"After matching_products_from_platform_with_orders {self.body.marketplace_id=} , {len(orders)=}")
        self._registration_metrics(len(orders))
        sales = await self.get_sales()
        ic(f"After import sales {self.body.marketplace_id=} , {len(sales)=}")
        sales_report = await self.get_sales_report()
        ic(f"After import sales_report {self.body.marketplace_id=} , {len(sales_report)=}")
        orders = self.matching_sales_with_orders(orders, sales)
        ic(f"After matching_sales_with_orders {self.body.marketplace_id=} , {len(orders)=}")
        orders = self.matching_sales_report_with_orders(orders, sales_report)
        ic(f"After matching_sales_report_with_orders {self.body.marketplace_id=} , {len(orders)=}")
        errors = self.order_requester.errors if self.order_requester else []
        ic(f"{self.body.marketplace_id=} , {len(errors)=}")
        orders = self.prepare_orders_to_platform(orders)
        await reset_metric()
        ic(f"After prepare_orders_to_platform {self.body.marketplace_id=} , {len(orders)=}")
        return MsgResponseToPlatform(data=orders, errors=errors)

    async def fetch_orders(self):
        orders = await self.order_requester.fetch()
        if not orders:
            return []
        return self.clear_duplicate_orders(orders)

    async def get_sales(self) -> list:
        try:
            handler = SalesHandler(app=self.app, body=self.body)
            result = await handler.execute()
        except Exception as err:
            logger_error.error(f"Ошибка импорта продаж.\n {err}\n {traceback.format_exc()}")
            return []
        return result.data or []

    async def get_sales_report(self) -> list:
        try:
            handler = SalesReportHandler(app=self.app, body=self.body)
            result = await handler.execute()
        except Exception as err:
            logger_error.error(f"Ошибка импорта продаж.\n {err}\n {traceback.format_exc()}")
            return []
        return result.data or []

    def prepare_orders_to_platform(self, orders: Collection[WBFBSOrder | WBFBOOrder]) -> list[dict]:
        return [order.model_to_platform(self.body.company_id, self.body.marketplace_id) for order in orders]

    def init_db_handler(self):
        self.db_handler = OrderDBHandler(
            pool=self.app[settings.DEFAULT_DATABASE],
            params=ParamsView(
                marketplace_id=self.body.marketplace_id,
                company_id=self.body.company_id,
            ),
            errors=self.errors,
        )

    async def fetch_relation_products(self) -> Collection[RelationProduct]:
        relation_products: list[dict] = []
        try:
            if isinstance(self.body.add_info, dict):
                relation_products = self.body.add_info.get("relation_products")

            if relation_products:
                return [RelationProduct(**item) for item in relation_products]
        except Exception as err:
            logger_error.error(
                f"Ошибка при получении товара с платформы.\n"
                f"{err}\n{traceback.format_exc()}\n{self.body.company_id=}\t{self.body.marketplace_id=}"
            )

        return await self.fetch_product_from_platform()

    async def fetch_product_from_platform(self) -> Collection[RelationProduct]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.body.token}",
        }
        url = settings.PLATFORM.get("url_relations_products") % self.body.marketplace_id
        return await fetch_collection_from_platform(url, headers, ResponseRelationProduct)

    @staticmethod
    def matching_sales_with_orders(orders: Collection[WBFBSOrder | WBFBOOrder], sales: Collection[dict]):
        if not sales:
            return orders
        _dict = {single_sales.get("srid"): single_sales for single_sales in sales}
        for order in orders:
            single_sales = _dict.get(order.id)
            if not single_sales:
                continue
            order.sales = single_sales
        return orders

    @staticmethod
    def matching_sales_report_with_orders(orders: Collection[WBFBSOrder | WBFBOOrder], sales: Collection[dict]):
        if not sales:
            return orders
        _dict = {item.get("srid"): item for item in sales}
        for order in orders:
            item = _dict.get(order.id)
            if not item:
                continue
            order.sales_report = item
        return orders

    def matching_products_from_platform_with_orders(
        self, orders: Collection[WBFBSOrder | WBFBOOrder], items_products: Collection[RelationProduct]
    ):
        ic(len(items_products))
        count_map_products = 0
        count_orders_products = len(orders)
        not_found = []
        for order in orders:
            find_product = next(filter(lambda x: x.idMp == str(order.nmId), items_products), None)
            if not find_product:
                not_found.append(order.nmId)
                continue

            order.id_platform = find_product.variant
            order.name_platform = find_product.name
            order.all_products_matched_to_platform = True
            count_map_products += 1

        if count_map_products != count_orders_products:
            logger_error.error(
                f"Не все товары сопоставлены с заказами.\n"
                f"{count_map_products=}\t{count_orders_products=}\n"
                f"{self.body.marketplace_id=}\t{self.body.company_id}\n"
                f"{not_found}"
            )
        return orders


class CheckingOrderStatuses(RequestHandler):
    errors: list[dict] = []
    reconciled_orders = list[ResponseChangeStatusOrderFromMs]
    funcs_marge_orders = set[Callable]

    def __init__(self, app: Application, body: MsgSendStartEventInMSMarketplace, test: bool = False):
        super().__init__(app, body, test)
        self.funcs_marge_orders = {
            self.merge_fbo_orders_and_sales,
        }

    async def execute(self) -> MsgResponseToPlatform:
        if not isinstance(self.body.data, dict) or not self.body.data.get("orders"):
            self.errors.append({"Ошибка входных данных": "не переданы данные для обработки"})
            return MsgResponseToPlatform(data=[], errors=self.errors)
        try:
            self.clean_data()
        except ValidationError:
            return MsgResponseToPlatform(data=[], errors=self.errors)

        await self.merge_orders()
        return_data = self.reconciled_orders if not self.errors else []
        return MsgResponseToPlatform(data=return_data, errors=self.errors)

    def clean_data(self):
        try:
            self.reconciled_orders = list(
                map(ResponseChangeStatusOrderFromMs.model_validate, self.body.data["orders"])
            )
        except ValidationError as err:
            self.errors.append({"Ошибка входных данных": err})
            raise

    async def get_sales(self) -> list:
        handler = SalesHandler(app=self.app, body=self.body)
        result = await handler.execute()
        return result.data or []

    async def merge_orders(self):
        for call_func in self.funcs_marge_orders:
            await call_func()

    async def merge_fbo_orders_and_sales(self):
        sales = await self.get_sales()
        statuses_dict = {
            single_sales.get("srid"): {
                "wbStatus": "sold" if single_sales.get("saleID", "").startswith("S") else "declined_by_client",
                "supplierStatus": "",
            }
            for single_sales in sales
        }

        for item in self.reconciled_orders:
            single_status = statuses_dict.get(item.order_id)
            if not single_status:
                continue
            wb_status = single_status.get("wbStatus")
            item.new_status_from_marketplace = (
                wb_status if wb_status != StatusOrderWildberries.READY_FOR_PICKUP else ""
            )
            item.new_status_platform = MATCHING_MARKETPLACE_STATUS_ORDER.get(wb_status)


class OrderBulkHandler(BulkHandler):
    event = EventInMSMarketplace.START_IMPORT_ORDERS


bulk_import_orders = OrderBulkHandler()
