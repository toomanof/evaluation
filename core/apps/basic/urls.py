from aiohttp import web

from core.apps.basic.views.common import test
from core.apps.basic.views.orders import OrdersView
from core.apps.basic.views.sales import SalesView
from core.apps.basic.views.statistics import StatisticsView
from core.apps.basic.views.warehouses import WarehousesView

urlpatterns = [
    web.get("/test", test),
    web.view("/v1/{company_id}/{marketplace_id}/warehouses", WarehousesView),
    web.view("/v1/{company_id}/{marketplace_id}/statistics", StatisticsView),
    web.view("/v1/{company_id}/{marketplace_id}/orders", OrdersView),
    web.view("/v1/{company_id}/{marketplace_id}/sales", SalesView),
]
