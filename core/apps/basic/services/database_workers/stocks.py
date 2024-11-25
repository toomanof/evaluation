from typing import List

from core.apps.basic.services.database_workers.orders import OrderDBHandler
from core.apps.basic.types import ItemMoveStock
from core.project.services.database_workers import DBHandler


class StockDBHandler(DBHandler):
    pass


async def collect_stock_info_from_orders_db(db_order_handler: OrderDBHandler) -> List[ItemMoveStock]:
    """Собираем данные из БД."""
    result = list()

    # TODO: когда будет доп поле, можно будет добавить обработку по дате, на данный момент достаем все!
    data = await db_order_handler.sql_select_movement_data()

    for item in data:
        result.append(ItemMoveStock(**dict(item)))

    return result
