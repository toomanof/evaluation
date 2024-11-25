# from typing import Any
# from unittest import mock
#
# from aiohttp import web
# from aiohttp.test_utils import make_mocked_coro
# from icecream import ic
#
# from core.apps.conftest import stopper
#
#
# def test_run_app_http(app, patched_loop: Any) -> None:
#     startup_handler = make_mocked_coro()
#     app.on_startup.append(startup_handler)
#     cleanup_handler = make_mocked_coro()
#     app.on_cleanup.append(cleanup_handler)
#
#     web.run_app(app, print=stopper(patched_loop), loop=patched_loop)
#
#     patched_loop.create_server.assert_called_with(
#         mock.ANY, None, 8080, ssl=None, backlog=128, reuse_address=None, reuse_port=None
#     )
#     startup_handler.assert_called_once_with(app)
#     cleanup_handler.assert_called_once_with(app)
#
#
# async def test_run_app_close_loop(app, patched_loop: Any) -> None:
#     web.run_app(app, print=stopper(patched_loop), loop=patched_loop)
#
#     patched_loop.create_server.assert_called_with(
#         mock.ANY, None, 8080, ssl=None, backlog=128, reuse_address=None, reuse_port=None
#     )
#     assert patched_loop.is_closed()
from icecream import ic


def test_paging():
    o_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
    w_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
    y_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
    last_after = [0, 0, 0]
    size_page_front = 10
    list_ms = [o_ids, w_ids, y_ids]
    qnt_ms = len(list_ms)
    response = []
    size_response = len(response)
    first = size_page_front // qnt_ms

    while size_response < size_page_front:
        ic(first, last_after)
        tmp_list_ms = []
        # Эмуляция запросов на м-с
        for index, ms in enumerate(list_ms):
            response_ms = ms[last_after[index] : last_after[index] + first]
            response.extend(response_ms)
            if response_ms:
                last_after[index] = response_ms[-1]
                tmp_list_ms.append(ms)
        size_response = len(response)
        list_ms = tmp_list_ms
        qnt_ms = len(list_ms)
        diff_response = size_page_front - size_response
        first = diff_response // qnt_ms
        if first == 0:
            list_ms = list_ms[0:1]
            first = diff_response

    ic(response)
