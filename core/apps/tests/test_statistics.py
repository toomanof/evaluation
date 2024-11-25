# NOTE: тест на методы StatisticHandler требуют восстановления в случае запуска логики

# @pytest.mark.skip("Вроде бы устарел, не нашел эту ручку у ВБ!")
# @pytest.mark.asyncio
# async def test_positive_import_stock(app, body_request_import_stock) -> None:
#     runner = web.AppRunner(app)
#     await runner.setup()
#     assert runner._server
#     handler = StatisticHandler(app=app, body=body_request_import_stock, test=True)
#     result = await handler.execute()
#     assert len(result.data) > 0
#     assert len(result.errors) == 0
#     await runner.cleanup()

# NOTE: тесты на view неактуальны, тк не api МС используется

# @pytest.mark.skip("Не работает с остальными")
# @pytest.mark.asyncio
# async def test_view_statistics(aiohttp_client, mocker):
#     result = [
#         {"a": "b"},
#     ]
#     app = web.Application()
#     app.on_startup.append(create_test_database_pool)
#     app.on_startup.append(create_tables)
#     app.on_cleanup.append(destroy_database_pool)
#     app.add_routes(settings.ROUTES)
#     runner = web.AppRunner(app)
#     await runner.setup()
#     assert runner._server
#
#     mocker.patch(
#         "core.apps.basic.services.database_workers.statistics.StatisticDBHandler.all",
#         return_value=result,
#     )
#     client = await aiohttp_client(app)
#     resp = await client.get("/v1/23/5/statistics")
#     assert resp.status == 200
#     response = await resp.json()
#     assert result == response.get("result")
#     await runner.cleanup()
