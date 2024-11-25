import pytest

from core.apps.basic.services.handlers import CommonHandler

from core.project.utils import time_of_completion


@pytest.mark.asyncio
@time_of_completion
async def test_positive_import_warehouses(running_app, body_request_import_warehouses) -> None:
    handler = CommonHandler(app=running_app, body=body_request_import_warehouses)
    result = await handler.import_warehouses()
    assert len(result.data) > 0
    assert len(result.errors) == 0


# NOTE: тесты на view неактуальны, тк не api МС используется

# @pytest.mark.skip("Не работает с остальными")
# @pytest.mark.asyncio
# @time_of_completion
# async def test_view_warehouses(aiohttp_client, mocker):
#     app = web.Application()
#     app.on_startup.append(create_test_database_pool)
#     app.on_startup.append(create_tables)
#     app.on_cleanup.append(destroy_database_pool)
#     app.add_routes(settings.ROUTES)
#     runner = web.AppRunner(app)
#     await runner.setup()
#     assert runner._server
#
#     # mocker.patch(
#     #     "core.apps.basic.services.database_workers.warehouses.WarehouseDBHandler.all",
#     #     return_value=result,
#     # )
#     client = await aiohttp_client(app)
#     resp = await client.get("/v1/23/5/warehouses")
#     response = await resp.json()
#     if response:
#         ic(response)
#     assert resp.status == 200
#     assert isinstance(response, dict)
