from collections import defaultdict
from typing import Collection

from icecream import ic

from core.apps.basic.services.requesters.stocks import StockRequester

from core.apps.basic.types import WBResponseListWarehouse, WBNomenclature, WBResponseWBStockFBO
from core.apps.basic.types.from_platform import (
    RelationProduct,
    ResponseRelationProduct,
    ResponseWarehousesFBO,
    WarehouseFBO,
)
from core.apps.basic.types.to_platform import ResponseToPlatformStockFBO
from core.project.conf import settings
from core.project.services.handlers.common import RequestHandler
from core.project.types import MsgResponseToPlatform
from core.project.utils import fetch_collection_from_platform, post_collection_from_ms


class ImportStockHandler(RequestHandler):
    async def execute(self) -> MsgResponseToPlatform:
        warehouse_ids, barcodes = await self.get_params_for_request_stock()
        stock, errors = await self.fetch_stock(warehouse_ids, barcodes.keys())

        for item in stock:
            item.good_id_mp = barcodes[item.sku]
        return MsgResponseToPlatform(data=stock, errors=errors)

    async def get_params_for_request_stock(self) -> tuple[Collection[str], dict]:
        warehouses = await self.fetch_warehouses()
        goods = await self.fetch_goods()
        warehouse_ids = tuple(x.id for x in warehouses)
        barcodes = {}
        for item in goods:
            for size in item.sizes:
                for sku in size.skus:
                    barcodes[sku] = item.nmID
        return warehouse_ids, barcodes

    async def fetch_stock(self, warehouse_ids: Collection[str], barcodes: Collection[str]):
        requester = StockRequester(
            app=self.app, session=self.app["session"], semaphore=self.semaphore, request_body=self.body, test=self.test
        )
        items = await requester.fetch(warehouse_ids=warehouse_ids, barcodes=barcodes)

        errors = requester.errors if requester else []
        return items, errors

    async def fetch_stock_fbo(self) -> MsgResponseToPlatform:
        requester = StockRequester(
            app=self.app, session=self.app["session"], semaphore=self.semaphore, request_body=self.body, test=self.test
        )
        result = await requester.fetch_stock_fbo()
        errors = requester.errors if requester else []
        products_from_platform = await self.fetch_relation_products()
        if result and result.root:
            dict_stock_to_platform = self.group_result_stock_fbo(result)
            result = self.matching_products_from_platform_with_stock_fbo(
                dict_stock_to_platform, products_from_platform
            )
        return MsgResponseToPlatform(data=result, errors=errors)

    async def fetch_goods(self) -> list[WBNomenclature]:
        from core.apps.basic.services.requesters.goods import NomenclatureRequest

        requester = NomenclatureRequest(
            app=self.app, session=self.app["session"], semaphore=self.semaphore, request_body=self.body, test=self.test
        )
        return await requester.fetch_nomenclature()

    async def fetch_warehouses(self) -> WBResponseListWarehouse:
        from core.apps.basic.services.handlers import WarehousesHandler

        data = await WarehousesHandler(app=self.app, body=self.body, test=self.test).fetch_warehouses()
        return WBResponseListWarehouse.model_validate(data.data)

    async def fetch_relation_products(self) -> Collection[RelationProduct]:
        relation_products: list[dict] = []
        try:
            if isinstance(self.body.add_info, dict):
                relation_products = self.body.add_info.get("relation_products")

            if relation_products:
                return [RelationProduct(**item) for item in relation_products]
        except Exception:
            pass

        return await self.fetch_product_from_platform()

    async def fetch_product_from_platform(self) -> Collection[RelationProduct]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.body.token}",
        }
        url = settings.PLATFORM.get("url_relations_products") % self.body.marketplace_id
        return await fetch_collection_from_platform(url, headers, ResponseRelationProduct)

    async def fetch_warehouses_fbo_from_platform(self) -> Collection[WarehouseFBO]:
        """Получаем список складов маркетплейса сохраненных в платформе."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.body.token}",
        }
        url = settings.PLATFORM.get("url_warehouses_fbo") % self.body.marketplace_id
        return await fetch_collection_from_platform(url, headers, ResponseWarehousesFBO)

    async def create_warehouses_fbo_in_platform(self, data) -> Collection[WarehouseFBO]:
        """Передаем список складов маркетплейса которых нет в платформе."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.body.token}",
        }
        url = settings.PLATFORM.get("url_warehouses_fbo") % self.body.marketplace_id
        return await post_collection_from_ms(url, headers, WarehouseFBO, body=data)

    @staticmethod
    def group_result_stock_fbo(stock: WBResponseWBStockFBO) -> dict[str, ResponseToPlatformStockFBO]:
        dict_product_in_stock = defaultdict(ResponseToPlatformStockFBO)
        for item in stock.root:
            if str(item.nmId) not in dict_product_in_stock.keys():
                dict_product_in_stock[str(item.nmId)] = ResponseToPlatformStockFBO(
                    nmId=item.nmId,
                    quantity=item.quantity,
                    warehouseName=item.warehouseName,
                )
            else:
                dict_product_in_stock[str(item.nmId)].quantity += item.quantity

        return dict(dict_product_in_stock)

    @staticmethod
    def matching_products_from_platform_with_stock_fbo(
        stock: dict[str, ResponseToPlatformStockFBO], items_products: Collection[RelationProduct]
    ) -> list[ResponseToPlatformStockFBO]:
        result = []
        for product_from_platform in items_products:
            find_record = stock.get(product_from_platform.idMp)
            if not find_record:
                continue

            find_record.id_platform = product_from_platform.product
            find_record.name_platform = product_from_platform.name
            result.append(find_record)

        ic(len(result))
        return result

    @staticmethod
    def prepare_fbo_report(
        stocks_fbo: WBResponseWBStockFBO,
        items_products: Collection[RelationProduct],
        warehouses_fbo: Collection[WarehouseFBO],
    ):
        # ) -> (Dict, List[str]):
        result = defaultdict(lambda: {"product_id": None, "warehouses": []})
        errors = []

        # Создадим словари для быстрого доступа
        items_products_dict = {item.article: item for item in items_products}
        warehouses_fbo_dict = {item.name: item for item in warehouses_fbo}
        for stock in stocks_fbo.root:
            item = items_products_dict.get(stock.supplierArticle)

            if item:
                warehouse = None
                # Заполняем результат с использованием setdefault
                if warehouses_fbo_dict.get(stock.warehouseName):
                    warehouse = {"id": warehouses_fbo_dict.get(stock.warehouseName).id, "quantity": stock.quantity}
                else:
                    print(f"в платформе отсутствует склад маркетплейса {stock.warehouseName}.")
                    errors.append(
                        f"в платформе отсутствует склад маркетплейса {stock.warehouseName}. "
                        f"Начался процесс обновления, пожалуйста повторите операцию."
                    )

                product_data = result[item.product]
                if product_data["product_id"] is None:
                    product_data["product_id"] = item.product
                if warehouse:
                    product_data["warehouses"].append(warehouse)
            else:
                errors.append(f"нет товара с артикулом {stock.supplierArticle}")

        return dict(result), errors

    async def _warehouses_get_or_create_on_platform(self, stocks_fbo) -> Collection[WarehouseFBO]:
        # Склады которые уже есть на платформе
        warehouses_fbo = await self.fetch_warehouses_fbo_from_platform()
        # Конвертируем в словарь для быстрого поиска
        warehouses_fbo_dict = {item.name: item for item in warehouses_fbo}

        # Собираю склады из отчета получено и складываю в set
        warehouses_stocks_fbo_set = set()
        for item in stocks_fbo.root:
            warehouses_stocks_fbo_set.add(item.warehouseName)

        # Собираю список для создания складов в платформе
        list_for_create = list()
        for item in warehouses_stocks_fbo_set:
            if item not in warehouses_fbo_dict:
                list_for_create.append({"name": item})

        # Если объекты на создание есть, то делаем запрос на платформу
        if list_for_create:
            new_data: Collection[WarehouseFBO] = await self.create_warehouses_fbo_in_platform(data=list_for_create)
            # Расширяем список складов
            warehouses_fbo.extend(new_data)
        return warehouses_fbo

    async def fetch_fbo_report(
        self,
    ) -> MsgResponseToPlatform:
        """Собираем полноценный Отчет "Остатки по товарам" FBO. Разбитый по складам."""
        result = []
        errors = []
        stocks_fbo, fbo_errors = await self.fetch_stock_fbo_for_report()
        errors.extend(fbo_errors)

        products = await self.fetch_relation_products()

        warehouses_fbo = await self._warehouses_get_or_create_on_platform(stocks_fbo)
        if not errors:
            result, prepare_error = self.prepare_fbo_report(stocks_fbo, products, warehouses_fbo)
            errors.extend(prepare_error)
        return MsgResponseToPlatform(data=result, errors=errors)

    async def fetch_stock_fbo_for_report(self):
        requester = StockRequester(
            app=self.app, session=self.app["session"], semaphore=self.semaphore, request_body=self.body, test=self.test
        )
        stocks_fbo: WBResponseWBStockFBO = await requester.fetch_stock_fbo()
        errors: list = requester.errors if requester else []

        return stocks_fbo, errors


class ExportStockHandler(RequestHandler):
    async def execute(self) -> MsgResponseToPlatform:
        requester = StockRequester(
            app=self.app,
            session=self.app["session"],
            semaphore=self.semaphore,
            request_body=self.body,
        )
        result = await requester.export()
        return MsgResponseToPlatform(data=result, errors=requester.errors)
