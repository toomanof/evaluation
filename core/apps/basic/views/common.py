from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response

from core.project.decorators import async_timed


@async_timed
async def test(request: Request) -> Response:
    return web.json_response({"result": "OK"})
