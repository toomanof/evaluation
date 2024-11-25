import logging
from datetime import datetime, timedelta

from core.apps.basic.request_urls.wildberries import (
    URL_STOCKS_WILDBERRIES_V3,
    URL_EXPORT_STOCKS_WILDBERRIES_V3,
    URL_STOCKS_WILDBERRIES_V1,
)
from core.apps.basic.types import (
    WBRequestBodyGetWarehouseStocks,
    DataExportStock,
    WBRequestBodyGetStocksFBO,
)
from core.project.services.requesters import AppRequester
from core.project.utils import url_with_params

logger_error = logging.getLogger("errors")
logger_info = logging.getLogger("info")


class StockRequester(AppRequester):
    async def fetch(self, *args, **kwargs):
        result = []
        warehouse_ids = kwargs.get("warehouse_ids", [])
        barcodes = kwargs.get("barcodes", [])
        params = WBRequestBodyGetWarehouseStocks(skus=barcodes).model_dump()
        for warehouse_id in warehouse_ids:
            url_params = url_with_params(URL_STOCKS_WILDBERRIES_V3, warehouse_id)

            response = await self.make_single_api_request(urls_and_params=(url_params, params))
            if response:
                for stock in response.stocks:
                    stock.warehouse_id = warehouse_id
                    stock.trader_schema = "FBS"
                result.extend(response.stocks)
        return result

    async def fetch_stock_fbo(self):
        date_from = datetime.now() - timedelta(days=30)
        params = WBRequestBodyGetStocksFBO(dateFrom=f"{date_from:%Y-%m-%dT%H:%M:%S}").model_dump()
        response = await self.make_single_api_request(urls_and_params=(URL_STOCKS_WILDBERRIES_V1, params))
        return response

    async def export(self):
        result = False
        data = DataExportStock.model_validate(self.request_body.data)
        params = data.stocks.model_dump()

        url_params = url_with_params(URL_EXPORT_STOCKS_WILDBERRIES_V3, data.warehouse_id)

        response = await self.make_single_api_request(urls_and_params=(url_params, params))

        # TODO: Расширить интерфейс результата кодом ответа от api
        if not self.errors:
            return True
        # NOTE:
        # make_single_api_request пока не пишет код ответа из Fetcher.
        # Пока исходим из того, что если запрос не вернул ошибок, то список ошибок пустой и запрос успешный
        # Позитивный код проверяется компонентом Fetcher из заданного в url_schema
        # Данную проверку сделать более явной, когда код ответа будет прокидываться из Fetcher
        # На данный момент проверка ниже закомментирована, тк она работать не будет
        # if response.response_code == 204:
        #     result = True

        return result
