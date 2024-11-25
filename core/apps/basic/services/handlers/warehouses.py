from core.project.services.handlers.common import RequestHandler
from core.project.types import MsgResponseToPlatform
from ..database_workers.warehouses import WarehouseDBHandler
from ..requesters.warehouses import WarehouseRequester
from ...request_urls.wildberries import URL_WAREHOUSES_WILDBERRIES_SELLER, URL_WAREHOUSES_FBO_WILDBERRIES_V1
from ...types import WBResponseListWarehouse


class WarehousesHandler(RequestHandler):
    async def execute(self) -> MsgResponseToPlatform:
        return await self.fetch_warehouses()

    async def fetch_campaigns(self):
        pass

    async def fetch_warehouses(self):
        return await self.__fetch__(
            class_requester=WarehouseRequester,
            class_db_handler=WarehouseDBHandler,
            url_schema=URL_WAREHOUSES_WILDBERRIES_SELLER,
            urls_and_params=[
                (URL_WAREHOUSES_WILDBERRIES_SELLER, None),
            ],
        )

    async def fetch_warehouses_fbo(self):
        return await self.__fetch__(
            class_requester=WarehouseRequester,
            # class_db_handler=WarehouseDBHandler,
            url_schema=URL_WAREHOUSES_FBO_WILDBERRIES_V1,
            urls_and_params=[
                (URL_WAREHOUSES_FBO_WILDBERRIES_V1, None),
            ],
        )

    def get_data_from_response_data(self, data: WBResponseListWarehouse):
        return data
