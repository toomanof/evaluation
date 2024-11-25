from core.apps.basic.services.database_workers.orders import OrderDBHandler
from core.project.views import DBHandlerView


class OrdersView(DBHandlerView):
    db_handler = OrderDBHandler
