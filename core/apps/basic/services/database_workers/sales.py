from core.apps.basic.sql_commands.sales import (
    SQL_SELECT_SALES,
    SQL_SELECT_IDS_SALES,
    SQL_INSERT_SALES,
    SQL_UPDATE_SALES,
)
from core.project.enums.common import SettingsInDataBase
from core.project.services.database_workers import DBHandler


class SalesDBHandler(DBHandler):
    code_settings: str = SettingsInDataBase.LAST_FETCH_WAREHOUSES.value
    sql_select: str = SQL_SELECT_SALES
    sql_select_ids: str = SQL_SELECT_IDS_SALES
    sql_insert: str = SQL_INSERT_SALES
    sql_update: str = SQL_UPDATE_SALES
    table = "sales"
