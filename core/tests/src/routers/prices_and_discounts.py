from aiohttp import web
from core.tests.src.factories.prices_and_discounts.responses import (
    WBResponseObjectHistoryGoodsFactory,
    WBFilterGoodsObjectFactory,
    WBGoodsSizeObjectFactory,
    SupplierTaskMetadataBufferFactory,
)
from apps.basic.types.requests import (
    WBRequestBodySizeGoodsPriceUpdate,
    WBRequestParamsExportPricesAndDiscounts,
    WBRequestParamsDownloadProcessedStatus,
    WBRequestParamsLoadDetails,
)
from apps.basic.types.query_params import WBFilterGoodsQueryParams, WBGoodsSizeQueryParams, WBLoadProgressQueryParams

from core.tests.src.utils import (
    check_request_body_schema_prices_api,
    check_query_params_prices_api,
    check_auth_prices_api,
    raise_exception_controller,
)

tasks_data = dict()

routes = web.RouteTableDef()


@routes.post("/api/v2/upload/task")
async def upload_task_handler(request):
    raise_exception_controller(request.headers, api_name="prices")
    check_auth_prices_api(request.headers)
    check_request_body_schema_prices_api(WBRequestParamsExportPricesAndDiscounts, await request.json())

    data = {"data": {"id": 1, "alreadyExists": False}, "error": False, "errorText": ""}

    status_code = 200

    # NOTE: закомментировано, тк при общем запуске не работает отдельный тест(тк идет повторное обращение к апи)
    # NOTE: для обработки ошибочных ответов апи необходимо продумать отдельный сценарий
    # global tasks_data
    # if tasks_data.get("1"):
    #     status_code = 208
    #     data = {"data": {"id": 1, "alreadyExists": True}, "error": False, "errorText": "Task already exists"}
    #     del tasks_data["1"]
    # else:
    #     tasks_data["1"] = {"data": {"id": 1, "alreadyExists": False}, "error": False, "errorText": ""}
    print("FAKE SERVER RESPONSE DATA: ", data)
    return web.json_response(data, status=status_code)


@routes.post("/api/v2/upload/task/size")
async def upload_goods_tasks_handler(request):
    raise_exception_controller(request.headers, api_name="prices")
    check_auth_prices_api(request.headers)
    check_request_body_schema_prices_api(WBRequestBodySizeGoodsPriceUpdate, await request.json())

    data = {"data": {"id": 2, "alreadyExists": False}, "error": False, "errorText": ""}
    status_code = 200
    global tasks_data
    if tasks_data.get("2"):
        status_code = 208
        data = {"data": {"id": 2, "alreadyExists": True}, "error": False, "errorText": "Task already exists"}
        del tasks_data["2"]
    else:
        tasks_data["2"] = {"data": {"id": 2, "alreadyExists": False}, "error": False, "errorText": ""}
    print("FAKE SERVER RESPONSE DATA: ", data)
    return web.json_response(data, status=status_code)


@routes.get("/api/v2/history/tasks")
async def history_tasks_handler(request):
    raise_exception_controller(request.headers, api_name="prices")
    check_auth_prices_api(request.headers)
    check_query_params_prices_api(WBRequestParamsDownloadProcessedStatus, dict(request.rel_url.query))
    # Фабрика
    # response = WBResponseRawLoadProgressFactory.build()
    # response.data.status = 3
    # response.data.uploadID = 1
    # response.data.error = False
    #
    # print(response.dict())
    data = {
        "data": {
            "uploadID": 1,
            "status": 3,
            "uploadDate": "2022-08-21T22:00:13+02:00",
            "activationDate": "2022-08-21T22:00:13+02:00",
            "overAllGoodsNumber": 1,
            "successGoodsNumber": 1,
        },
        "error": False,
        "errorText": "The product is in quarantine",
    }
    print("FAKE SERVER RESPONSE DATA: ", data)
    return web.json_response(data)


@routes.get("/api/v2/history/goods/task")
async def history_goods_tasks_handler(request):
    raise_exception_controller(request.headers, api_name="prices")
    check_auth_prices_api(request.headers)
    check_query_params_prices_api(WBRequestParamsLoadDetails, dict(request.rel_url.query))
    goods = WBResponseObjectHistoryGoodsFactory.batch(size=10)
    goods_dict = [item.model_dump() for item in goods]

    data = {
        "data": {
            "uploadID": 1,
            "historyGoods": goods_dict,
        }
    }
    print("FAKE SERVER RESPONSE DATA: ", data)
    return web.json_response(data)


@routes.get("/api/v2/list/goods/filter")
async def goods_filter_handler(request):
    raise_exception_controller(request.headers, api_name="prices")
    check_auth_prices_api(request.headers)
    check_query_params_prices_api(WBFilterGoodsQueryParams, dict(request.rel_url.query))
    goods = WBFilterGoodsObjectFactory.batch(size=10)
    goods_dict = [item.model_dump() for item in goods]
    data = {
        "data": {
            "listGoods": goods_dict,
        }
    }
    print("FAKE SERVER RESPONSE DATA: ", data)
    return web.json_response(data)


@routes.get("/api/v2/list/goods/size/nm")
async def goods_size_nm_handler(request):
    """Получить размеры товаров."""
    raise_exception_controller(request.headers, api_name="prices")
    check_auth_prices_api(request.headers)
    check_query_params_prices_api(WBGoodsSizeQueryParams, dict(request.rel_url.query))
    goods = WBGoodsSizeObjectFactory.batch(size=10)
    goods_dict = [item.model_dump() for item in goods]
    data = {
        "data": {
            "listGoods": goods_dict,
        },
        "error": False,
        "errorText": "string",
    }
    print("FAKE SERVER RESPONSE DATA: ", data)
    return web.json_response(data)


@routes.get("/api/v2/buffer/tasks")
async def buffer_tasks_handler(request):
    """Состояние необработанной загрузки."""
    raise_exception_controller(request.headers, api_name="prices")
    check_auth_prices_api(request.headers)
    check_query_params_prices_api(WBLoadProgressQueryParams, dict(request.rel_url.query))
    obj = SupplierTaskMetadataBufferFactory.build()
    response = {"data": obj.dict(), "error": False, "errorText": ""}
    print("FAKE SERVER RESPONSE DATA: ", response)
    return web.json_response(response)


@routes.get("/api/v2/buffer/goods/task")
async def buffer_goods_tasks_handler(request):
    """Детализация необработанной загрузки."""
    raise_exception_controller(request.headers, api_name="prices")
    check_auth_prices_api(request.headers)
    check_query_params_prices_api(WBRequestParamsLoadDetails, dict(request.rel_url.query))
    goods = WBResponseObjectHistoryGoodsFactory.batch(size=10)
    goods_dict = [item.model_dump() for item in goods]

    data = {
        "data": {
            "uploadID": 1,
            "bufferGoods": goods_dict,
        },
        "error": False,
        "errorText": "",
    }
    print("FAKE SERVER RESPONSE DATA: ", data)
    return web.json_response(data)
