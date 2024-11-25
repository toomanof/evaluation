import pytest
from core.apps.conftest import SandBoxPricesApiClient

"""
{
  "headers": {
    "Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjQwMjI2djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTcyNjc4MjI0MiwiaWQiOiJiYmRlYjBkNC0xNTJlLTQwZjgtYjg0MS00NTBkOGJlOWY0MzMiLCJpaWQiOjE0MDgwNjMwNywib2lkIjozMzMyMCwicyI6MCwic2lkIjoiYTRiNjYzZjItYWI0MC01ZTdjLThhZWEtNjJkOWFlYmFhMmFmIiwidCI6dHJ1ZSwidWlkIjoxNDA4MDYzMDd9.d-Hi3Vvp8AoipI5vZqXiJDt6rZ86X2c5aPNlzkzL3hIXt0-HGkHlYqIqXMqUBjCchaamANyIv2G0UTO34-KwUw"
  },
  "company_id": 1,
  "marketplace_id": 1,
  "event": "export_size_goods_price",
  "data": {
    "data": [
      {
        "nmID": 253,
        "sizeID": 252,
        "price": 1000
      }
    ]
  },
  "callback": "result_export_size_goods_price",
  "event_id": "1",
  "task_id": 1
}
"""


@pytest.mark.skip
@pytest.mark.asyncio
async def test_upload_task_size_post_schema():
    """Тест для проверки актуальности полей. Используется песочница(ВБ) с заранее созданными объектами."""

    client = SandBoxPricesApiClient()
    data = {"data": [{"nmID": 253, "sizeID": 252, "price": 1000}]}
    request = await client.post("/api/v2/upload/task/size", data=data)
    assert request.status == 200


"""
{
  "headers": {
    "Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjQwMjI2djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTcyNjc4MjI0MiwiaWQiOiJiYmRlYjBkNC0xNTJlLTQwZjgtYjg0MS00NTBkOGJlOWY0MzMiLCJpaWQiOjE0MDgwNjMwNywib2lkIjozMzMyMCwicyI6MCwic2lkIjoiYTRiNjYzZjItYWI0MC01ZTdjLThhZWEtNjJkOWFlYmFhMmFmIiwidCI6dHJ1ZSwidWlkIjoxNDA4MDYzMDd9.d-Hi3Vvp8AoipI5vZqXiJDt6rZ86X2c5aPNlzkzL3hIXt0-HGkHlYqIqXMqUBjCchaamANyIv2G0UTO34-KwUw"
  },
  "company_id": 1,
  "marketplace_id": 1,
  "event": "import_goods_size_for_nm",
  "data": {
    "query_params":
      {
          "limit": 10,
          "offset": 0,
          "nmID": 253
      }

  },
  "callback": "result_import_goods_size_for_nm",
  "event_id": "1",
  "task_id": 1
}
"""


@pytest.mark.skip
async def test_get_list_goods_size():
    """Smoke test. Тест для проверки работоспособности эндпоинта"""
    client = SandBoxPricesApiClient()
    # Товар уже существует в песочнице(nmID=253)
    # Получить информацию о размерах для nmID=253(лимит 1)
    request = await client.get("/api/v2/list/goods/size/nm?limit=1&nmID=253")
    assert request.status == 200


@pytest.mark.skip
async def test_get_list_goods_filter():
    """Smoke test. Тест для проверки работоспособности эндпоинта(получение списка товаров)"""
    client = SandBoxPricesApiClient()
    # Товар уже существует в песочнице(nmID=253)
    # Получить информацию о размерах для nmID=253(лимит 1)
    request = await client.get("/api/v2/list/goods/filter?limit=10&offset=0&filterNmID=253")
    assert request.status == 200
