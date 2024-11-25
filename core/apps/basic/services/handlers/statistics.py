from aiohttp.web_app import Application
from datetime import date, datetime, timedelta


from core.apps.basic.services.database_workers.statistics import StatisticDBHandler
from core.apps.basic.services.requesters.statistics import StatisticRequester
from core.apps.basic.types import WBResponseCardStatisticsForSelectedPeriod
from core.project.conf import settings
from core.project.services.handlers.common import RequestHandler
from core.project.types import (
    MsgResponseToPlatform,
    MsgSendStartEventInMSMarketplace,
    ParamsView,
)


class StatisticHandler(RequestHandler):
    db_handler: StatisticDBHandler = None
    errors: list[dict] = []

    def __init__(self, app: Application, body: MsgSendStartEventInMSMarketplace, test: bool = False):
        super().__init__(app, body, test)
        self.init_db_handler()

    async def execute(self) -> MsgResponseToPlatform:
        return await self.fetch_statistics()

    def get_data_from_response_data(self, data: dict):
        result = []
        for _day, cards in data.items():
            for card in cards:
                card = WBResponseCardStatisticsForSelectedPeriod.model_validate(card)
                card.date_reg = _day
                result.append(card)
        return result

    def init_db_handler(self):
        self.db_handler = StatisticDBHandler(
            pool=self.app[settings.DEFAULT_DATABASE],
            params=ParamsView(
                marketplace_id=self.body.marketplace_id,
                company_id=self.body.company_id,
            ),
            errors=self.errors,
        )

    async def fetch_statistics(self):
        yesterday: datetime = datetime.today() - timedelta(days=1)
        requester = StatisticRequester(
            app=self.app, session=self.app["session"], semaphore=self.semaphore, request_body=self.body, test=self.test
        )
        items = await requester.fetch(yesterday)
        if not items:
            return MsgResponseToPlatform(data=items, errors=requester.errors)

        items = self.get_data_from_response_data(items)
        await self.db_handler.insert_or_update(items)
        items = await self.db_handler.get_records_for_date(yesterday)
        for item in items:
            item.pop("id", None)
            item.pop("json_data", None)
            item.pop("created_at", None)
            item.pop("company_id", None)
            item.pop("marketplace_id", None)
        errors = requester.errors if requester else []
        return MsgResponseToPlatform(data=items, errors=errors)

    async def get_date_for_request(self) -> date | None:
        yesterday: datetime = datetime.today() - timedelta(days=1)
        dates = await self.db_handler.get_list_of_registered_dates(yesterday)
        return yesterday if not dates else None
