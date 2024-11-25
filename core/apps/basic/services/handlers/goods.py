from core.apps.basic.services.requesters.goods import ProductRequester, SizeGoodsRequester
from core.project.services.handlers.common import RequestHandler
from core.project.types import MsgResponseToPlatform


class ProductsHandler(RequestHandler):
    async def _execute(self, method: str) -> MsgResponseToPlatform:
        requester = ProductRequester(
            app=self.app,
            session=self.app["session"],
            semaphore=self.semaphore,
            request_body=self.body,
        )
        result = await getattr(requester, method)()
        # TODO: костыль. Переделать так, чтобы методы отдавали результат в едином интерфейсе
        if isinstance(result, MsgResponseToPlatform):
            return result
        errors = requester.errors if requester.errors else []
        return MsgResponseToPlatform(data=result, errors=errors)

    async def export_prices(self) -> MsgResponseToPlatform:
        return await self._execute("export_prices_v2")

    async def export_products(self) -> MsgResponseToPlatform:
        return await self._execute("export_products")

    async def import_goods_list(self) -> MsgResponseToPlatform:
        return await self._execute("import_goods_list_by_filter")


class SizeGoodsHandler(RequestHandler):
    async def export_size_prices(self) -> MsgResponseToPlatform:
        return await self._execute("export_size_goods_price")

    async def import_size_info_for_nm(self) -> MsgResponseToPlatform:
        return await self._execute("import_goods_size_for_nm")

    async def _execute(self, method: str) -> MsgResponseToPlatform:
        requester = SizeGoodsRequester(
            app=self.app,
            session=self.app["session"],
            semaphore=self.semaphore,
            request_body=self.body,
        )
        result = await getattr(requester, method)()
        errors = requester.errors if requester.errors else []
        return MsgResponseToPlatform(data=result, errors=errors)
