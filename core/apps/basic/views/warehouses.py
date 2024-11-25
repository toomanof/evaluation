from core.apps.basic.services.database_workers.warehouses import WarehouseDBHandler
from core.project.views import DBHandlerView


class WarehousesView(DBHandlerView):
    db_handler = WarehouseDBHandler
