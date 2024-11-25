import uuid
from aiohttp import web
import json

from core.apps.basic.request_urls.wildberries import URL_GET_ORDERS_WILDBERRIES_V1, URL_REALIZATION_SALES_REPORT
from core.tests.src.factories.statistics.responses import WBFBOOrderFactory, WBSalesFactory, WBSalesReportFactory
from core.tests.src.utils import check_auth_suppliers_api, raise_exception_controller

routes = web.RouteTableDef()

supplier_orders_data = dict()


@routes.get(path=URL_GET_ORDERS_WILDBERRIES_V1.url)
async def get_supplier_orders_handler(request):
    raise_exception_controller(request.headers)
    check_auth_suppliers_api(request.headers)
    orders = WBFBOOrderFactory.batch(size=10)

    result = list()
    for item in orders:
        item.srid = str(uuid.uuid4())
        result.append(json.loads(item.model_dump_json()))

    # print("FAKE SERVER RESPONSE DATA: ", result)
    return web.json_response(result)


@routes.get("/api/v1/supplier/sales")
async def get_supplier_sales_handler(request):
    raise_exception_controller(request.headers)
    check_auth_suppliers_api(request.headers)
    sales = WBSalesFactory.batch(size=30)

    result = [json.loads(item.model_dump_json(exclude_none=True)) for item in sales]
    # print("FAKE SERVER RESPONSE DATA: ", result)
    return web.json_response(result)


@routes.get(URL_REALIZATION_SALES_REPORT.url)
async def get_sales_report_handler(request):
    raise_exception_controller(request.headers)
    check_auth_suppliers_api(request.headers)
    sales_report = WBSalesReportFactory.batch(size=30)
    result = [json.loads(item.model_dump_json(exclude_none=True)) for item in sales_report]
    return web.json_response(result)
