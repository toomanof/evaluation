# import asyncio
# from asyncio import Semaphore
# from datetime import datetime, timedelta, time
#
# from aiohttp import ClientSession
# from icecream import ic
#
# from core.apps.basic.request_urls.common import URLParameterSchema
# from core.apps.basic.request_urls.wildberries import (
#     URL_STATISTICS_FOR_SELECTED_PERIOD,
#     URL_SALES_WILDBERRIES_V1,
#     URL_STOCKS_WILDBERRIES_V3,
# )
# from core.apps.basic.types import (
#     WBSelectedPeriod,
#     WBRequestParamsStatisticsForSelectedPeriod,
# )
# from core.apps.conftest import MockResponse
# from core.project.services.requesters.fetcher import Fetcher
#
#
# async def execute_fetch_with_two_headers(
#     fetcher: Fetcher,
#     count_requests: int,
#     auth_headers: tuple[dict, dict],
#     url_params: URLParameterSchema,
#     params: dict,
#     semaphore: Semaphore,
# ) -> int:
#     count_positive_request = 0
#     start = datetime.now()
#     tasks = []
#     headers1, headers2 = auth_headers
#     async with (ClientSession() as session):
#         for i in range(count_requests):
#             headers = headers1 if i % 2 else headers1
#             tasks.append(
#                 asyncio.create_task(
#                     fetcher(
#                         session=session,
#                         semaphore=semaphore,
#                         url_params=url_params,
#                         headers=headers,
#                         params=params,
#                     )
#                 )
#             )
#         done_tasks, pending_tasks = await asyncio.wait(tasks)
#         print(f"Число завершившихся задач: {len(done_tasks)}")
#         print(f"Число ожидающих задач: {len(pending_tasks)}")
#
#         for task in done_tasks:
#             if task.exception() is None:
#                 status, item = task.result()
#                 if status == 200:
#                     count_positive_request += 1
#                 else:
#                     ic(task, status, item)
#     end = datetime.now()
#     print(f"Выполнение запросов завершено за {end - start} с")
#     return count_requests
#
#
# async def test_limit_request_statistics(auth_headers, fetcher):
#     count_requests = 2
#     yesterday: datetime = datetime.today() - timedelta(days=1)
#     period = WBSelectedPeriod(
#         begin=datetime.combine(yesterday, time(0, 0, 1)).strftime("%Y-%m-%d %H:%M:%S"),
#         end=datetime.combine(yesterday, time(23, 59, 59)).strftime("%Y-%m-%d %H:%M:%S"),
#     )
#     params = WBRequestParamsStatisticsForSelectedPeriod(
#         page=1, period=period
#     ).model_dump(exclude_none=True, exclude_unset=True)
#
#     count_positive_request = await execute_fetch_with_two_headers(
#         fetcher=fetcher,
#         count_requests=count_requests,
#         auth_headers=auth_headers,
#         params=params,
#         url_params=URL_STATISTICS_FOR_SELECTED_PERIOD,
#         semaphore=Semaphore(4),
#     )
#     assert count_requests == count_positive_request
#
#
# async def test_limit_request_sales(auth_headers_for_statistics, fetcher):
#     count_requests = 4
#     yesterday: datetime = datetime.today() - timedelta(days=1)
#     params = {
#         "flag": 1,
#         "dateFrom": yesterday.strftime("%Y-%m-%d"),
#     }
#     count_positive_request = await execute_fetch_with_two_headers(
#         fetcher=fetcher,
#         count_requests=count_requests,
#         auth_headers=auth_headers_for_statistics,
#         params=params,
#         url_params=URL_SALES_WILDBERRIES_V1,
#         semaphore=Semaphore(4),
#     )
#     assert count_requests == count_positive_request
#
#
# async def test_429(mocker, auth_headers):
#     fetcher = Fetcher()
#     resp = MockResponse("429", 429)
#     mocker.patch(
#         "core.project.services.requesters.fetcher.Fetcher.fetch_method",
#         return_value=resp,
#     )
#     async with (ClientSession() as session):
#         await fetcher(
#             session=session,
#             semaphore=Semaphore(4),
#             url_params=URL_STOCKS_WILDBERRIES_V3,
#             headers=auth_headers[0],
#             params={},
#         )
