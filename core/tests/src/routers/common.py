import os

from aiohttp import web
from core.tests.src.exceptions import TooManyRetries


routes = web.RouteTableDef()

global_counter = 1


@routes.get("/common/check_429_status_code")
async def check_429_status_code_error_handler(request):
    """Метод возвращает 429 ошибку ((MAX_COUNT_REPEAT_REQUESTS - 1) раз).

    Для проверки attempt_fetch метода в классе Fetch.
    """
    global global_counter
    MAX_COUNT_REPEAT_REQUESTS = int(os.environ.get("MAX_COUNT_REPEAT_REQUESTS", 3))
    if global_counter < MAX_COUNT_REPEAT_REQUESTS:
        global_counter += 1
        raise TooManyRetries

    return web.json_response(status=200)
