import json
import random
from aiohttp import web

from apps.basic.request_urls.wildberries import (
    URL_LIST_NOMENCLATURES_WILDBERRIES_V2,
    URL_LIST_ERROR_NOMENCLATURES_WILDBERRIES,
    URL_UPDATE_CARDS_PRODUCTS_WILDBERRIES_V3,
)
from apps.basic.types import WBResponse
from core.tests.src.factories.content.responses import WBNomenclatureFactory, WBErrorNomenclatureFactory
from core.tests.src.utils import check_auth_suppliers_api, raise_exception_controller
from core.apps.constants import COUNT_ITEMS_ONE_ITERATION_FILTER_CARDS

routes = web.RouteTableDef()


@routes.post(path=URL_LIST_NOMENCLATURES_WILDBERRIES_V2.url)
async def cards_list_handler(request):
    raise_exception_controller(request.headers)
    check_auth_suppliers_api(request.headers)
    # check_request_body_schema_suppliers_api()
    # NOTE: условием остановки пагинации является возврат карточек в количестве меньше лимита запроса
    # п.4 https://openapi.wildberries.ru/content/api/ru/#tag/Prosmotr/paths/~1content~1v2~1get~1cards~1list/post
    cards_quantity_for_generate: int = random.randint(
        COUNT_ITEMS_ONE_ITERATION_FILTER_CARDS - 2, COUNT_ITEMS_ONE_ITERATION_FILTER_CARDS + 2
    )
    cards = WBNomenclatureFactory.batch(size=cards_quantity_for_generate)
    result = [json.loads(item.model_dump_json(exclude_none=True)) for item in cards]

    response = {
        "cards": result,
        "cursor": {"updatedAt": "2023-12-06T11:17:00.96577Z", "nmID": random.randint(0, 2), "total": len(cards)},
    }
    # print("FAKE SERVER RESPONSE DATA: ", response)
    return web.json_response(response)


@routes.post(path=URL_UPDATE_CARDS_PRODUCTS_WILDBERRIES_V3.url)
async def cards_update_handler(request):
    raise_exception_controller(request.headers)
    check_auth_suppliers_api(request.headers)

    response = WBResponse().model_dump()

    return web.json_response(response)


@routes.get(path=URL_LIST_ERROR_NOMENCLATURES_WILDBERRIES.url)
async def cards_error_list_handler(request):
    raise_exception_controller(request.headers)
    check_auth_suppliers_api(request.headers)
    cards = WBErrorNomenclatureFactory.batch(size=10)
    result = [json.loads(item.model_dump_json(exclude_none=True)) for item in cards]
    response = {"data": result, "error": False, "errorText": "", "additionalErrors": ""}
    # print("FAKE SERVER RESPONSE DATA: ", response)
    return web.json_response(response)
