from core.apps.basic.services.database_workers.statistics import StatisticDBHandler
from core.project.views import DBHandlerView


class StatisticsView(DBHandlerView):
    db_handler = StatisticDBHandler
