from aiohttp import web

from core.apps.tests.test_fetcher_component.response_for_fetcher import ROUTE_PAYLOAD_RESPONSE_MAPPER

fetcher_routes = web.RouteTableDef()


# =============ROUTES RETURN CODE 200=================


@fetcher_routes.get("/get_200_json")
async def wb_response_200_json(request):
    return web.json_response(ROUTE_PAYLOAD_RESPONSE_MAPPER.get(request.path)["payload"], status=200)


@fetcher_routes.get("/get_200_text")
async def wb_response_200_text(request):
    return web.Response(text=str(ROUTE_PAYLOAD_RESPONSE_MAPPER.get(request.path)["payload"]), status=200)


# =============ROUTES RETURN ERROR CODE AND RETRY EXPECTED=================


@fetcher_routes.get("/get_500")
async def wb_response_500(request):
    return web.json_response(ROUTE_PAYLOAD_RESPONSE_MAPPER.get(request.path)["payload"], status=500)


@fetcher_routes.get("/get_429")
async def wb_response_429(request):
    return web.json_response(ROUTE_PAYLOAD_RESPONSE_MAPPER.get(request.path)["payload"], status=429)


# =============ROUTES RETURN ERROR CODE AND NO RETRY EXPECTED=================


@fetcher_routes.get("/get_400")
async def wb_response_400(request):
    return web.json_response(ROUTE_PAYLOAD_RESPONSE_MAPPER.get(request.path)["payload"], status=400)


@fetcher_routes.get("/get_401")
async def wb_response_401(request):
    return web.json_response(ROUTE_PAYLOAD_RESPONSE_MAPPER.get(request.path)["payload"], status=401)


@fetcher_routes.get("/get_403")
async def wb_response_403(request):
    return web.json_response(ROUTE_PAYLOAD_RESPONSE_MAPPER.get(request.path)["payload"], status=403)


@fetcher_routes.get("/get_404")
async def wb_response_404(request):
    return web.json_response(ROUTE_PAYLOAD_RESPONSE_MAPPER.get(request.path)["payload"], status=404)


@fetcher_routes.get("/get_409")
async def wb_response_409(request):
    return web.json_response(ROUTE_PAYLOAD_RESPONSE_MAPPER.get(request.path)["payload"], status=409)


@fetcher_routes.get("/get_no_data")
async def wb_response_no_data(request):
    return web.json_response([], status=200)
