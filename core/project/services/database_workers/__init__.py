import base64
import datetime
import json
import traceback

from asyncpg import Pool, Connection
from dataclasses import dataclass, field
from typing import Callable, Any, Collection, Optional

from icecream import ic

from core.apps.basic.sql_commands import (
    SQL_SELECT_SETTING,
    UPDATE_SETTING,
    INSERT_SETTING,
)
from core.apps.basic.types import WBFBSOrder, WBFBOOrder
from core.apps.constants import get_postgresql_value
from core.project.constants import FORMAT_DATE, CONDITION_PREFIX
from core.project.types import ParamsView
from core.project.utils import serialize


@dataclass
class CommonDBHandler:
    pool: Pool
    params: ParamsView
    errors: Optional[list] = field(default_factory=list)

    async def _insert_setting(self, connection: Connection, code: str, value: str):
        return await connection.execute(
            INSERT_SETTING,
            code,
            str(value),
            self.params.company_id,
            self.params.marketplace_id,
        )

    async def _reg_action(self, connection: Connection, code: str, value: str):
        """
        Запись времени последнего получения списка
        """
        result = await self._select_setting(code)
        call = self._update_setting if result else self._insert_setting
        await call(connection=connection, code=code, value=value)

    async def _select_setting(self, code: str) -> str:
        return await self.pool.fetchval(
            SQL_SELECT_SETTING,
            code,
            self.params.company_id,
            self.params.marketplace_id,
        )

    async def _update_setting(self, connection: Connection, code: str, value: str):
        return await connection.execute(
            UPDATE_SETTING,
            code,
            str(value),
            self.params.company_id,
            self.params.marketplace_id,
        )

    async def __insert_rows__(self, call_reg_action: Callable, sql: str, args: Collection[tuple[Any]]):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                await call_reg_action(connection=connection)
                try:
                    return await connection.executemany(sql, args)
                except Exception as err:
                    ic(err, sql, args)
                    raise

    async def __update_rows__(self, call_reg_action: Callable, sql: str, args: Collection[tuple[Any]]):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                await call_reg_action(connection=connection)
                return await connection.executemany(sql, args)


class DBHandler(CommonDBHandler):
    code_settings: str
    sql_select: str
    sql_select_ids: str
    sql_insert: str
    sql_update: str
    table: str

    async def _reg_fetch(self, connection: Connection):
        """
        Запись времени последнего получения списка складов
        """
        now = datetime.datetime.now()
        await self._reg_action(connection, self.code_settings, now.strftime(FORMAT_DATE))

    async def all(self):
        records = await self.select_all_records()
        return self.prepare_records_for_response(records)

    async def for_platform(self):
        return self.all()

    def unpacking_params_cursor(self) -> dict:
        cursor = self.params.after or self.params.before
        if not cursor:
            return {"id": 0}
        try:
            result = json.loads(base64.b64decode(cursor).decode())
        except TypeError:
            result = {"id": 0}
        return result

    @staticmethod
    def get_sort_field_operation(sort_field_direction, before, after):
        operation = "<"
        sort_field_direction = sort_field_direction.lower()
        if sort_field_direction == "asc" and before:
            operation = "<"
        elif sort_field_direction == "asc" and after:
            operation = ">"
        elif sort_field_direction != "asc" and before:
            operation = ">"
        elif sort_field_direction != "asc" and after:
            operation = "<"
        return operation

    def prepare_condition_cursor(self, sort_fields, cursor, cursor_sort_direction, expression, after, before):
        if sort_fields:
            sort_field_variable, sort_field_direction = sort_fields.pop().split()
            sort_field_direction = sort_field_direction.lower()

            operation = self.get_sort_field_operation(sort_field_direction, before, after)

            sort_field_value = get_postgresql_value(value=cursor.get(sort_field_variable))

            expression += f"{sort_field_variable} {operation} {sort_field_value}"

            if not sort_fields:
                cursor_value = cursor.get("id", "(NULL, NULL)")
                cursor_field = "(id, marketplace_id)"
                cursor_operation = self.get_sort_field_operation(cursor_sort_direction, before, after)
                next_sort = f"{cursor_field} {cursor_operation} {cursor_value}" + ")"
            else:
                next_sort = (
                    self.prepare_condition_cursor(sort_fields, cursor, cursor_sort_direction, "", after, before) + ")"
                )

            expression += f" or ({sort_field_variable} = {sort_field_value} and ({next_sort})"

        return expression

    @property
    def sort_directions(self):
        cursor_sort_direction = "ASC"
        sorts = []
        for x in reversed(self.params.sorting_fields):
            sorting = x.split()
            if sorting[0] != "id":
                sorts.append(x)
            else:
                cursor_sort_direction = sorting[1]
        return sorts, cursor_sort_direction

    @property
    def condition_cursor(self):
        if not self.params.after and not self.params.before:
            return ""

        sorts, cursor_sort_direction = self.sort_directions

        condition = ""
        cursor = self.unpacking_params_cursor()

        return self.prepare_condition_cursor(
            sorts, cursor, cursor_sort_direction, condition, self.params.after, self.params.before
        )

    def prepare_sql_filter(self, has_after_or_before: bool = True):
        condition = ""
        if not self.params.filter and not (self.params.after or self.params.before):
            return condition

        for key, val in (self.params.filter or {}).items():
            operation = CONDITION_PREFIX.get(key[-3:], "=")
            key = key if operation == "=" else key[:-4]

            if isinstance(val, list):
                t_val = "','".join(val)
                condition_expression = f"{key} in ('{t_val}')"
            else:
                condition_expression = f"{key}{operation}'{val}'"

            condition += f" AND {condition_expression}"

        if has_after_or_before and (self.params.after or self.params.before):
            condition += f" AND ({self.condition_cursor})"

        return condition

    def prepare_sql_sorting(self):
        sorting_fields = self.params.sorting_fields.copy()
        sorting_expression = ", ".join(sorting_fields) or "(1)"

        row_number_direction = "ASC" if self.params.first else "DESC"
        natural_sort = f"ROW_NUMBER() OVER (ORDER BY {sorting_expression}) {row_number_direction}"

        if natural_sort:
            sorting_fields.insert(0, natural_sort)

        return sorting_fields

    def sql_select_with_params(self, sql_select: str = None, aggregate: bool = False, limit: bool = True):
        condition = self.prepare_sql_filter(has_after_or_before=limit)
        limit_params = ""
        if limit:
            limit_params = self.params.first or self.params.last
            limit_params = f"LIMIT {limit_params}" if limit_params else ""

        sql_sorting = self.prepare_sql_sorting()
        sorting = f"ORDER BY {', '.join(sql_sorting)}" if not aggregate and sql_sorting else ""
        sql_select = self.sql_select.strip(";") if not sql_select else sql_select.strip(";")
        return f"{sql_select} {condition} {sorting} {limit_params}".strip()

    async def select_all_records(self) -> list:
        records = []
        async with self.pool.acquire() as connection:
            try:
                records = await connection.fetch(
                    self.sql_select_with_params(),
                    self.params.company_id,
                    self.params.marketplace_id,
                )
            except Exception as err:
                ic(f"{err}\n{traceback.format_exc()}")
                self.errors.append(str(err))
        return records

    @staticmethod
    def prepare_records_for_response(records: list):
        result = list()
        for record in records:
            if not record:
                continue
            dict_record = dict(record)
            json_data = dict_record.get("json_data")
            if json_data and isinstance(json_data, (str, bytes)):
                dict_record["json_data"] = json.loads(json_data)
            result.append(dict_record)
        return serialize(result)

    async def total_count(self):
        sql = self.sql_select_with_params(
            f"SELECT COUNT(*) FROM {self.table} WHERE company_id=$1 AND marketplace_id=$2;",
            aggregate=True,
            limit=False,
        )
        result = await self.pool.fetchrow(
            sql,
            self.params.company_id,
            self.params.marketplace_id,
        )

        return dict(result).get("count", 0) if result else 0

    async def get_records_for_comparison(self) -> dict[str:str]:
        async with self.pool.acquire() as con:
            records = await con.fetch(self.sql_select, self.params.company_id, self.params.marketplace_id)
        return tuple(str(item["id_mp"]) for item in map(dict, records))

    async def insert_or_update(self, items: Collection[Any]):
        internal_order_data = await self.get_records_for_comparison()
        list_for_insert, list_for_update = self.distribution_to_insert_and_update_lists(internal_order_data, items)
        if list_for_insert:
            await self.insert(list_for_insert)
        # if list_for_update:
        #     await self.update(list_for_update)

    @staticmethod
    def distribution_to_insert_and_update_lists(
        internal_id_mp_orders_data: tuple[str], external_data: Collection[WBFBSOrder | WBFBOOrder]
    ) -> tuple[Collection[WBFBSOrder | WBFBOOrder], Collection[WBFBSOrder | WBFBOOrder]]:
        """
        Разбиение списка заказов на множества обновления и добавления по наличию в базе
        """
        list_for_insert = list(filter(lambda item: item.id_mp not in internal_id_mp_orders_data, external_data))
        list_for_update = list(filter(lambda item: item.id_mp in internal_id_mp_orders_data, external_data))
        return list_for_insert, list_for_update

    async def get_datetime_last_fetch(self):
        return await self._select_setting(self.code_settings)

    async def insert(self, items: Collection[WBFBSOrder | WBFBOOrder]):
        params = self.params.company_id, self.params.marketplace_id
        values = tuple(item.args_for_insert_row(*params) for item in items)
        await self.__insert_rows__(self._reg_fetch, self.sql_insert, values)

    async def update(self, items: Collection[WBFBSOrder | WBFBOOrder]):
        params = self.params.company_id, self.params.marketplace_id
        values = tuple(item.args_for_update_row(*params) for item in items)
        await self.__insert_rows__(self._reg_fetch, self.sql_update, values)
