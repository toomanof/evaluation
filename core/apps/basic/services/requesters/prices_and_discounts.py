import logging

from core.apps.basic.request_urls.wildberries import URL_EXPORT_PRICES_AND_DISCOUNTS
from core.apps.basic.types import (
    WBRequestItemSetPriceAndDiscount,
    WBRequestParamsExportPricesAndDiscounts,
)
from core.project.services.requesters import AppRequester, SingleRequester
from core.project.types import URLParameterSchema
from core.project.utils import count_iterations_from_total, start_stop_index_in_iteration

logger_error = logging.getLogger("errors")
logger_info = logging.getLogger("info")


class PricesAndDiscountsRequester(AppRequester):
    @staticmethod
    def _prepare_data_single_request(
        number_iteration: int, params_list: list[WBRequestItemSetPriceAndDiscount]
    ) -> tuple[URLParameterSchema, dict]:
        start_index, stop_index = start_stop_index_in_iteration(number_iteration, 1000)
        data = WBRequestParamsExportPricesAndDiscounts(data=params_list[start_index:stop_index])
        return URL_EXPORT_PRICES_AND_DISCOUNTS, data.model_dump()

    async def _set_prices_and_discounts(self, params_list: list[WBRequestItemSetPriceAndDiscount]):
        count_iterations = count_iterations_from_total(len(params_list), 1000)
        urls_and_params = [
            self._prepare_data_single_request(iteration, params_list) for iteration in range(count_iterations)
        ]
        return await self.fetch(urls_and_params)

    def clean_input_data(self):
        return WBRequestParamsExportPricesAndDiscounts.model_validate(self.request_body.data)

    async def execute(self):
        input_data = self.clean_input_data()
        result = await self._set_prices_and_discounts(input_data.data)
        return result.model_dump()


class DownloadProcessedStatusRequester(SingleRequester):
    pass


class ProcessedLoadDetailsRequester(SingleRequester):
    pass


class RawLoadDetailsRequester(SingleRequester):
    pass


class RawLoadProgressRequester(SingleRequester):
    pass
