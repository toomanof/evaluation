from aiohttp.abc import Application
from icecream import ic

from core.apps.basic.services.handlers.goods import ProductsHandler, SizeGoodsHandler
from core.apps.basic.services.handlers.orders import OrdersHandler, CheckingOrderStatuses
from core.apps.basic.services.handlers.statistics import StatisticHandler  # noqa

# from core.apps.basic.services.orders import collect_stock_info_from_orders_db
from core.apps.basic.services.handlers.stocks import (
    ImportStockHandler,
    ExportStockHandler,
)
from core.apps.basic.services.handlers.warehouses import WarehousesHandler
from core.project.types import MsgSendStartEventInMSMarketplace, MsgResponseToPlatform
# from core.apps.basic.services.broker_publishers import send_message_to_stocks_microservice


class CommonHandler:
    def __init__(self, app: Application, body: MsgSendStartEventInMSMarketplace):
        self.app = app
        self.body = body

    async def checking_order_statuses(self) -> MsgResponseToPlatform:
        handler = CheckingOrderStatuses(app=self.app, body=self.body)
        return await handler.execute()

    async def export_prices(self) -> MsgResponseToPlatform:
        handler = ProductsHandler(app=self.app, body=self.body)
        return await handler.export_prices()

    async def export_products(self) -> MsgResponseToPlatform:
        handler = ProductsHandler(app=self.app, body=self.body)
        return await handler.export_products()

    async def export_stock(self) -> MsgResponseToPlatform:
        ic("export_stock")
        handler = ExportStockHandler(app=self.app, body=self.body)
        return await handler.execute()

    async def export_size_goods_price(self) -> MsgResponseToPlatform:
        handler = SizeGoodsHandler(app=self.app, body=self.body)
        return await handler.export_size_prices()

    async def import_stock(self) -> MsgResponseToPlatform:
        ic("import_stock")
        handler = ImportStockHandler(app=self.app, body=self.body)
        return await handler.execute()

    async def import_stock_fbo(self) -> MsgResponseToPlatform:
        ic("import_stock fbo")
        handler = ImportStockHandler(app=self.app, body=self.body)
        return await handler.fetch_stock_fbo()

    async def import_warehouses(self) -> MsgResponseToPlatform:
        handler = WarehousesHandler(app=self.app, body=self.body)
        return await handler.execute()

    async def import_warehouses_fbo(self) -> MsgResponseToPlatform:
        handler = WarehousesHandler(app=self.app, body=self.body)
        data = await handler.fetch_warehouses_fbo()
        return data

    async def import_orders(self) -> MsgResponseToPlatform:
        handler = OrdersHandler(app=self.app, body=self.body)
        return await handler.execute()

    async def import_report_fbo(self) -> MsgResponseToPlatform:
        handler = ImportStockHandler(app=self.app, body=self.body)
        return await handler.fetch_fbo_report()

    async def import_goods_size_for_nm(self) -> MsgResponseToPlatform:
        handler = SizeGoodsHandler(app=self.app, body=self.body)
        return await handler.import_size_info_for_nm()

    async def import_goods_list(self) -> MsgResponseToPlatform:
        handler = ProductsHandler(app=self.app, body=self.body)
        return await handler.import_goods_list()
