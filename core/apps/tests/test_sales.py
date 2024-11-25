import pytest
from aiohttp import web

from core.apps.basic.services.handlers.sales import SalesHandler, SalesReportHandler
from core.project.conf import settings
from core.project.utils import time_of_completion


@pytest.mark.asyncio
@time_of_completion
async def test_positive_import_sales(app, body_request_import_orders) -> None:
    runner = web.AppRunner(app)
    await runner.setup()
    pool = app[settings.DEFAULT_DATABASE]
    await pool.execute("TRUNCATE sales, settings;")
    handler = SalesHandler(app=app, body=body_request_import_orders)
    result = await handler.execute()
    assert len(result.data) > 0
    assert len(result.errors) == 0
    await runner.cleanup()
    print(len(result.data))
    await runner.cleanup()


@pytest.mark.asyncio
@time_of_completion
async def test_positive_import_sales_report(app, body_request_import_orders) -> None:
    runner = web.AppRunner(app)
    await runner.setup()
    pool = app[settings.DEFAULT_DATABASE]
    await pool.execute("TRUNCATE sales, settings;")
    handler = SalesReportHandler(app=app, body=body_request_import_orders)
    result = await handler.execute()
    assert len(result.data) > 0
    assert len(result.errors) == 0
    await runner.cleanup()
    print(len(result.data))
    await runner.cleanup()


# NOTE: тесты на view неактуальны, тк не api МС используется

# @pytest.mark.skip("Не работает с остальными")
# @pytest.mark.asyncio
# @time_of_completion
# async def test_view_sales(aiohttp_client):
#     # result = [
#     #     {"a": "b"},
#     # ]
#     app = web.Application()
#     app.on_startup.append(create_test_database_pool)
#     app.on_startup.append(create_tables)
#     app.on_cleanup.append(destroy_database_pool)
#     app.add_routes(settings.ROUTES)
#     runner = web.AppRunner(app)
#     await runner.setup()
#     assert runner._server
#
#     client = await aiohttp_client(app)
#     resp = await client.get("/v1/23/5/sales")
#     assert resp.status == 200
#     response = await resp.json()
#     assert len(response.get("result")) > 0
