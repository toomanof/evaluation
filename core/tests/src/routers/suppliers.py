import uuid
from aiohttp import web
import json

from apps.basic.request_urls.wildberries import URL_STOCKS_WILDBERRIES_V1, URL_EXPORT_STOCKS_WILDBERRIES_V3
from core.tests.src.factories.suppliers.responses import (
    SupplyOrderFactory,
    WBResponseOrdersStatusFactory,
    WBResponseWarehouseFactory,
    WBResponseWBStockFBOFactory,
)
from core.tests.src.utils import (
    check_request_body_schema_suppliers_api,
    check_query_params_suppliers_api,
    check_auth_suppliers_api,
    raise_exception_controller,
)
from apps.basic.types.requests import (
    WBRequestBodyFBSOrders,
    WBRequestBodyOrdersStatus,
    WBRequestBodyGetWarehouseStocks,
    WBRequestBodyUpdateWarehouseStocks,
)

routes = web.RouteTableDef()

orders_data = dict()


@routes.get("/api/v3/orders/new")
async def get_new_orders_handler(request):
    raise_exception_controller(request.headers)
    check_auth_suppliers_api(request.headers)
    global orders_data
    # Фабрика
    orders = SupplyOrderFactory.batch(size=3)
    # сформировать ответ
    new_orders = list()
    for item in orders:
        item.rid = str(uuid.uuid4())
        new_orders.append(json.loads(item.model_dump_json()))
        # добавить в общий список
        orders_data[item.id] = item
    response = {"orders": new_orders}
    # print("FAKE SERVER RESPONSE DATA: ", response)
    return web.json_response(response)


@routes.get("/api/v3/orders")
async def get_orders_handler(request):
    raise_exception_controller(request.headers)
    check_auth_suppliers_api(request.headers)
    check_query_params_suppliers_api(WBRequestBodyFBSOrders, dict(request.rel_url.query))
    global orders_data
    orders_list_dump = [json.loads(item.model_dump_json()) for item in orders_data.values()]

    if not orders_data:
        orders = SupplyOrderFactory.batch(size=3)
        # orders_list_dump = [json.loads(item.model_dump_json()) for item in orders]
        # orders_data = {}

        for item in orders:
            item.rid = str(uuid.uuid4())
            orders_list_dump.append(json.loads(item.model_dump_json()))
            # добавить в общий список
            orders_data[item.id] = item

    response = {"orders": orders_list_dump}
    # print("FAKE SERVER RESPONSE DATA: ", response)
    return web.json_response(response)


@routes.post("/api/v3/orders/status")
async def get_orders_status_handler(request):
    raise_exception_controller(request.headers)
    check_auth_suppliers_api(request.headers)
    body = await request.json()
    check_request_body_schema_suppliers_api(WBRequestBodyOrdersStatus, body)

    # data = {"orders": [{"id": 5632423, "supplierStatus": "new", "wbStatus": "waiting"}]}
    input_data = body.get("orders")
    result = list()
    for item in input_data:
        # Поскольку у нас нет статусной модели, мы извлекаем ее из той что имеем)
        obj = WBResponseOrdersStatusFactory.build(id=item).orders[0]
        result.append(obj)
    response = {"orders": result}
    # print("FAKE SERVER RESPONSE DATA: ", response)
    return web.json_response(response)


@routes.get("/api/v3/warehouses")
async def get_warehouses_handler(request):
    raise_exception_controller(request.headers)
    check_auth_suppliers_api(request.headers)
    warehouses = WBResponseWarehouseFactory.batch(size=2)
    warehouses_list = [item.model_dump() for item in warehouses]
    print("FAKE SERVER RESPONSE DATA: ", warehouses_list)
    return web.json_response(warehouses_list)


@routes.post("/api/v3/stocks/{warehouseId}")
async def get_stock_handler(request):
    raise_exception_controller(request.headers)
    check_auth_suppliers_api(request.headers)
    body = await request.json()
    check_request_body_schema_suppliers_api(WBRequestBodyGetWarehouseStocks, body)

    stocks_list = list()
    for item in body.get("skus"):
        stocks_list.append({"sku": item, "amount": 10})
    response = {"stocks": stocks_list}
    print("FAKE SERVER RESPONSE DATA: ", response)
    return web.json_response(response)


@routes.get(path=URL_STOCKS_WILDBERRIES_V1.url)
async def get_fbo_tock_handler(request):
    raise_exception_controller(request.headers)
    check_auth_suppliers_api(request.headers)

    response = WBResponseWBStockFBOFactory.build()
    # NOTE: Дампим сразу в json, чтобы механизм pydantic корректно
    # NOTE: сдампил все поля datetime на всех уровнях вложенности
    return web.Response(text=response.model_dump_json(), content_type="application/json")


export_stock_path = URL_EXPORT_STOCKS_WILDBERRIES_V3.url % "{warehouseId}"


@routes.put(path=export_stock_path)
async def export_stock_handler(request):
    raise_exception_controller(request.headers)
    check_auth_suppliers_api(request.headers)

    body = await request.json()
    check_request_body_schema_suppliers_api(WBRequestBodyUpdateWarehouseStocks, body)
    return web.json_response(status=204)
