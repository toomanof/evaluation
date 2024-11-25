import logging
from datetime import datetime, time, date

from core.apps.basic.request_urls.wildberries import URL_STATISTICS_FOR_SELECTED_PERIOD
from core.apps.basic.types import (
    WBSelectedPeriod,
    WBRequestParamsStatisticsForSelectedPeriod,
)
from core.project.services.requesters import AppRequester
from core.project.utils import full_url


logger_error = logging.getLogger("errors")
logger_info = logging.getLogger("info")


class StatisticRequester(AppRequester):
    async def fetch(self, date_reg: date):
        result = []
        period = WBSelectedPeriod(
            begin=datetime.combine(date_reg, time(0, 0, 1)).strftime("%Y-%m-%d %H:%M:%S"),
            end=datetime.combine(date_reg, time(23, 59, 59)).strftime("%Y-%m-%d %H:%M:%S"),
        )
        is_next_page = True
        page = 1
        while is_next_page:
            params = WBRequestParamsStatisticsForSelectedPeriod(page=page, period=period).model_dump(
                exclude_none=True, exclude_unset=True
            )
            logger_info.info(
                f"Направлен запрос на WB"
                f"\n\t-company_id{self.request_body.company_id}"
                f"\n\t-url: {full_url(URL_STATISTICS_FOR_SELECTED_PERIOD.url)}"
                f"\n\t-параметры: {params}"
            )
            response = await self.make_single_api_request(urls_and_params=(URL_STATISTICS_FOR_SELECTED_PERIOD, params))

            if not response:
                break
            is_next_page = response.data.isNextPage
            result.extend(response.data.cards)

            page += 1

        return {f"{date_reg:%Y-%m-%d}": result}
