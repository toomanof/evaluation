from typing import Collection, Any
from datetime import datetime

from asyncpg import Record

from core.apps.basic.types import WBFBSOrder, WBFBOOrder
from core.apps.basic.sql_commands.orders import (
    SQL_INSERT_ORDERS,
    SQL_SELECT_ORDERS,
    SQL_SELECT_IDS_ORDERS,
    SQL_UPDATE_ORDERS,
    SQL_SELECT_ORDERS_MOVEMENT_DATA,
)
from core.project.enums.common import SettingsInDataBase
from core.project.services.database_workers import DBHandler


class OrderDBHandler(DBHandler):
    code_settings: str = SettingsInDataBase.LAST_FETCH_ORDERS.value
    sql_select: str = SQL_SELECT_ORDERS
    sql_select_ids: str = SQL_SELECT_IDS_ORDERS
    sql_insert: str = SQL_INSERT_ORDERS
    sql_update: str = SQL_UPDATE_ORDERS
    table = "orders"

    @staticmethod
    def filter_duplicate_orders(records: list[dict]) -> list:
        result_ids = []
        result = []
        for item in records:
            if item.get("id_mp") in result_ids:
                continue
            result_ids.append(item.get("id_mp"))
            result.append(item)
        return result

    async def for_platform(self):
        records = await self.select_all_records()
        await self.delete_all()
        return self.prepare_records_for_response(records)

    async def delete_all(self):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(
                    f"DELETE FROM orders "
                    f"WHERE company_id={self.params.company_id} "
                    f"AND marketplace_id={self.params.marketplace_id};"
                )

    async def insert_or_update(self, items: Collection[WBFBSOrder | WBFBOOrder]):
        await self.update(items)

    def sql_select_with_params(self, sql_select: str = None, aggregate: bool = False, limit: bool = True):
        return "SELECT * FROM orders " "WHERE company_id=$1 AND marketplace_id=$2 "

    async def sql_select_movement_data(self, updated_at_start: datetime = None, updated_at_end=None):
        sql = SQL_SELECT_ORDERS_MOVEMENT_DATA
        # TODO: добавить поле для отслеживания даты изменения, чтобы не тянуть лишнего
        # if updated_at_start and updated_at_end:
        #     sql += f" WHERE orders.created_at BETWEEN '{updated_at_start.isoformat()}'
        #     AND  '{updated_at_end.isoformat()}'"
        async with self.pool.acquire() as connection:
            return await connection.fetch(sql)

    def prepare_records_for_response(self, records: list[Record]) -> list[dict]:
        tmp_result = super().prepare_records_for_response(records)
        return self.filter_duplicate_orders(tmp_result)

    async def update(self, items: Collection[Any]):
        params = self.params.company_id, self.params.marketplace_id
        values = tuple(item.args_for_update_row(*params) for item in items)
        await self.delete_all()
        async with self.pool.acquire() as connection:
            await connection.executemany(self.sql_insert, values)
