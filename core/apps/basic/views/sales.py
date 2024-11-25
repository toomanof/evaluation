from core.apps.basic.services.database_workers.sales import SalesDBHandler
from core.project.views import DBHandlerView


class SalesView(DBHandlerView):
    db_handler = SalesDBHandler
