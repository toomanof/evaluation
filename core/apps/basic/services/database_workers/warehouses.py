from core.apps.basic.sql_commands.warehouses import (
    SQL_INSERT_WAREHOUSES,
    SQL_SELECT_IDS_WAREHOUSE,
    SQL_SELECT_WAREHOUSES,
    SQL_UPDATE_WAREHOUSES,
)
from core.project.enums.common import SettingsInDataBase
from core.project.services.database_workers import DBHandler


class WarehouseDBHandler(DBHandler):
    code_settings: str = SettingsInDataBase.LAST_FETCH_WAREHOUSES.value
    sql_select: str = SQL_SELECT_WAREHOUSES
    sql_select_ids: str = SQL_SELECT_IDS_WAREHOUSE
    sql_insert: str = SQL_INSERT_WAREHOUSES
    sql_update: str = SQL_UPDATE_WAREHOUSES
    table = "warehouse"
