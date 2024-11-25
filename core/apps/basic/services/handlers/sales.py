from datetime import datetime, timedelta

from core.apps.basic.request_urls.wildberries import URL_SALES_WILDBERRIES_V1, URL_REALIZATION_SALES_REPORT
from core.apps.basic.services.database_workers.sales import SalesDBHandler
from core.apps.basic.services.requesters.sales import SalesRequester, SalesReportRequester
from core.apps.basic.types import WBResponseSales
from core.project.services.handlers.common import RequestHandler
from core.project.types import MsgResponseToPlatform


class SalesHandler(RequestHandler):
    async def execute(self) -> MsgResponseToPlatform:
        return await self.fetch_sales()

    async def fetch_sales(self):
        date_from = datetime.now() - timedelta(days=30)
        return await self.__fetch__(
            class_requester=SalesRequester,
            class_db_handler=SalesDBHandler,
            url_schema=URL_SALES_WILDBERRIES_V1,
            urls_and_params=[
                (
                    URL_SALES_WILDBERRIES_V1,
                    {"flag": 0, "dateFrom": f"{date_from:%Y-%m-%d}"},
                ),
            ],
        )

    def get_data_from_response_data(self, data: WBResponseSales):
        return data


class SalesReportHandler(RequestHandler):
    async def execute(self) -> MsgResponseToPlatform:
        return await self.fetch_report()

    async def fetch_report(self):
        now = datetime.now()
        date_from = now - timedelta(days=30)
        return await self.__fetch__(
            class_requester=SalesReportRequester,
            url_schema=URL_REALIZATION_SALES_REPORT,
            urls_and_params=[
                (
                    URL_REALIZATION_SALES_REPORT,
                    {"dateFrom": f"{date_from:%Y-%m-%d}", "dateTo": f"{now:%Y-%m-%d}"},
                ),
            ],
        )

    def get_data_from_response_data(self, data: WBResponseSales):
        return data
