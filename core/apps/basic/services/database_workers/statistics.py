from datetime import date
from typing import Collection


from core.apps.basic.sql_commands.statistics import (
    SQL_SELECT_STATISTICS,
    SQL_UPDATE_STATISTICS,
    SQL_INSERT_STATISTICS,
    SQL_SELECT_IDS_STATISTICS,
    SQL_SELECT_DATES_STATICS,
    SQL_SELECT_STATISTICS_FOR_DATE,
)
from core.project.constants import DATE_TEMPLATE_Ymd
from core.project.enums.common import SettingsInDataBase
from core.project.services.database_workers import DBHandler


class StatisticDBHandler(DBHandler):
    code_settings: str = SettingsInDataBase.LAST_FETCH_STATISTICS.value
    sql_select: str = SQL_SELECT_STATISTICS
    sql_select_ids: str = SQL_SELECT_IDS_STATISTICS
    sql_insert: str = SQL_INSERT_STATISTICS
    sql_update: str = SQL_UPDATE_STATISTICS
    table = "statistics"

    @staticmethod
    def distribution_to_insert_and_update_lists(records, items) -> tuple[list, list]:
        list_for_insert = list(
            filter(
                lambda item: tuple((item.nmID, item.date_reg)) not in records,
                items,
            )
        )
        list_for_update = list(
            filter(
                lambda item: tuple((item.nmID, item.date_reg)) in records,
                items,
            )
        )
        return list_for_insert, list_for_update

    async def get_list_of_registered_dates(self, date_reg: date) -> set[dict]:
        records = await self.pool.fetch(
            SQL_SELECT_DATES_STATICS,
            self.params.company_id,
            self.params.marketplace_id,
            date_reg,
        )
        return {item["date_reg"] for item in (map(dict, records))}

    async def get_records_for_comparison(self):
        records = await self.pool.fetch(self.sql_select_ids, self.params.company_id, self.params.marketplace_id)
        return tuple((item["id_mp"], item["date_reg"].strftime(DATE_TEMPLATE_Ymd)) for item in map(dict, records))

    async def get_records_for_date(self, date_reg: date) -> Collection[dict]:
        if not date_reg:
            return []

        records = await self.pool.fetch(
            SQL_SELECT_STATISTICS_FOR_DATE,
            self.params.company_id,
            self.params.marketplace_id,
            date_reg,
        )
        return list(map(dict, records))
