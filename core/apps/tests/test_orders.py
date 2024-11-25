import pytest
from asyncio import Semaphore
from typing import Any
from collections import Counter
from pytest_postgresql.janitor import DatabaseJanitor

from core.apps.basic.request_urls.wildberries import (
    URL_GET_ORDERS_WILDBERRIES_V1,
    URL_GET_ORDERS_WILDBERRIES_V3,
)
from core.apps.basic.services.database_workers.orders import OrderDBHandler
from core.apps.basic.services.handlers import CommonHandler, OrdersHandler
from core.apps.basic.services.requesters.orders import (
    FBSOrderRequester,
    FBOOrderRequester,
    OrderRequester,
)
from core.apps.basic.sql_commands.orders import (
    SQL_INSERT_ORDERS,
    SQL_INSERT_ORDER_LINES,
)
from core.project.types import MsgResponseToPlatform
from core.project.conf import settings
from core.project.utils import time_of_completion
from core.apps.basic.types.types import ItemMoveStock
from core.apps.basic.services.database_workers.stocks import collect_stock_info_from_orders_db


# @pytest.mark.asyncio
# @time_of_completion
# async def test_request_orders_new_fbs(app, body_request_import_orders):
#     requester = FBSOrderRequester(
#         app=app,
#         semaphore=Semaphore(4),
#         session=ClientSession(),
#         request_body=body_request_import_orders,
#         url_schema=URL_GET_ORDERS_WILDBERRIES_V3,
#     )
#     result = await requester.fetch_new_orders()
#     assert len(result) > 0


@pytest.mark.asyncio
@time_of_completion
async def test_request_status_orders(loop, fake_server, app, body_request_import_orders, test_client_session):
    requester = FBSOrderRequester(
        app=app,
        semaphore=Semaphore(4),
        session=test_client_session,
        request_body=body_request_import_orders,
        url_schema=URL_GET_ORDERS_WILDBERRIES_V3,
        # test=True,
    )
    fbs_orders = await requester.fetch_orders()
    statuses = await requester.fetch_statuses_orders(fbs_orders)
    assert len(statuses) > 0
    assert len(fbs_orders) == len(statuses)


@pytest.mark.asyncio
@time_of_completion
async def test_request_double_orders_fbs(running_app, fake_server, body_request_import_orders, test_client_session):
    requester = FBSOrderRequester(
        app=running_app,
        semaphore=Semaphore(4),
        session=test_client_session,
        request_body=body_request_import_orders,
        url_schema=URL_GET_ORDERS_WILDBERRIES_V3,
    )
    result = await requester.fetch()
    rids = list(fbs_order.rid for fbs_order in result)
    counter_double_orders = Counter(rids)
    double_orders = [(elem, cnt) for elem, cnt in counter_double_orders.items() if cnt > 1]
    assert len(double_orders) == 0


@pytest.mark.asyncio
@time_of_completion
async def test_request_orders_fbs(loop, fake_server, app, body_request_import_orders, test_client_session):
    requester = FBSOrderRequester(
        app=app,
        semaphore=Semaphore(4),
        session=test_client_session,
        request_body=body_request_import_orders,
        url_schema=URL_GET_ORDERS_WILDBERRIES_V3,
    )
    result = await requester.fetch()
    assert len(result) > 0


@pytest.mark.asyncio
@time_of_completion
async def test_request_orders_fbo(loop, fake_server, app, body_request_import_orders_fbo, test_client_session):
    pool = app[settings.DEFAULT_DATABASE]

    await pool.execute(
        "TRUNCATE orders, orders_line, settings; "
        "ALTER SEQUENCE orders_id_seq RESTART WITH 1; "
        "ALTER SEQUENCE orders_line_id_seq RESTART WITH 1"
    )
    requester = FBOOrderRequester(
        app=app,
        semaphore=Semaphore(4),
        session=test_client_session,
        request_body=body_request_import_orders_fbo,
        url_schema=URL_GET_ORDERS_WILDBERRIES_V1,
    )
    result = await requester.fetch()
    assert len(result) > 0


@pytest.mark.asyncio
@time_of_completion
async def test_request_orders_fbo_500_status_code(
    loop, fake_server, app, body_request_import_orders_fbo, initiate_500_status_headers, test_client_session
):
    pool = app[settings.DEFAULT_DATABASE]
    await pool.execute(
        "TRUNCATE orders, orders_line, settings; "
        "ALTER SEQUENCE orders_id_seq RESTART WITH 1; "
        "ALTER SEQUENCE orders_line_id_seq RESTART WITH 1"
    )
    body = body_request_import_orders_fbo.copy()
    body.headers = initiate_500_status_headers
    url_schema = URL_GET_ORDERS_WILDBERRIES_V1

    url_schema.timeout = 1
    requester = FBOOrderRequester(
        app=app, semaphore=Semaphore(4), session=test_client_session, request_body=body, url_schema=url_schema
    )
    result = await requester.fetch()
    assert result == []


@pytest.mark.asyncio
@time_of_completion
async def test_request_double_orders_fbo(loop, fake_server, app, body_request_import_orders_fbo, test_client_session):
    requester = FBOOrderRequester(
        app=app,
        semaphore=Semaphore(4),
        session=test_client_session,
        request_body=body_request_import_orders_fbo,
        url_schema=URL_GET_ORDERS_WILDBERRIES_V1,
    )
    result = await requester.fetch()
    assert len(result) > 0

    srids = list(order.srid for order in result)
    print(len(srids))
    counter_double_orders = Counter(srids)
    double_orders = [(elem, cnt) for elem, cnt in counter_double_orders.items() if cnt > 1]
    print(len(double_orders))
    assert len(double_orders) == 0


@pytest.mark.asyncio
@time_of_completion
async def test_clear_duplicate_fbs_from_statistic_orders(
    loop, fake_server, app, body_request_import_orders, test_client_session
):
    requester = OrderRequester(
        app=app,
        semaphore=Semaphore(4),
        session=test_client_session,
        request_body=body_request_import_orders,
    )
    fbs_orders = await requester.fetch_fbs_orders()
    orders_from_statistic_method = await requester.fetch_orders_from_statistic_method()
    orders_from_statistic_method = requester.clear_duplicate_fbs_from_statistic_orders(
        fbs_orders, orders_from_statistic_method
    )
    srids = set()
    rids = set()
    for order in orders_from_statistic_method:
        if hasattr(order, "rid"):
            rids.add(order.rid)
        if hasattr(order, "srid"):
            srids.add(order.srid)
    r = set(rids) & set(srids)
    assert not bool(r)


@pytest.mark.asyncio
@time_of_completion
async def test_clear_duplicate_orders(loop, fake_server, app, body_request_import_orders, test_client_session):
    requester = OrderRequester(
        app=app,
        semaphore=Semaphore(4),
        session=test_client_session,
        request_body=body_request_import_orders,
    )
    orders = await requester.fetch()
    handler = OrdersHandler(app=app, body=body_request_import_orders)
    orders = handler.clear_duplicate_orders(orders)

    ids = set()
    for order in orders:
        if hasattr(order, "rid"):
            ids.add(order.rid)
        if hasattr(order, "srid"):
            ids.add(order.srid)
    count_ids = sum(Counter(ids).values())
    assert len(ids) == count_ids


@pytest.mark.asyncio
@time_of_completion
async def test_clear_fbo_from_fbs_orders_with_fbs_requester_500(
    loop, fake_server, app, body_request_import_orders, initiate_500_status_headers, test_client_session
):
    body_500 = body_request_import_orders.copy()
    body_500.headers = initiate_500_status_headers

    requester = OrderRequester(
        app=app,
        semaphore=Semaphore(4),
        session=test_client_session,
        request_body=body_request_import_orders,
    )
    fbs_requester = OrderRequester(
        app=app,
        semaphore=Semaphore(4),
        session=test_client_session,
        request_body=body_500,
    )
    fbs_orders = await fbs_requester.fetch_fbs_orders()
    fbo_orders = await requester.fetch_orders_from_statistic_method()
    result = requester.clear_duplicate_fbs_from_statistic_orders(fbs_orders, fbo_orders)
    rids = set(fbs_order.rid for fbs_order in fbs_orders)
    srids = set(fbo_order.srid for fbo_order in result)
    r = rids & srids
    assert not bool(r)


def test_substitute_data_into_fbs_from_fbo_orders(
    app,
    event_loop,
    test_client_session,
    body_request_import_orders,
    fbs_orders_for_substitute_data,
    fbo_orders_for_substitute_data,
):
    requester = OrderRequester(
        app=app,
        semaphore=Semaphore(4),
        session=test_client_session,
        request_body=body_request_import_orders,
    )
    number_fbs_orders_in_fbo, number_fbs_orders_changed = requester.substitute_data_into_fbs_from_fbo_orders(
        fbs_orders=fbs_orders_for_substitute_data, fbo_orders=fbo_orders_for_substitute_data
    )
    assert number_fbs_orders_in_fbo == number_fbs_orders_changed

    positive_result = sum(
        bool(fbs_order.statistics) and bool(fbs_order.priceWithDisc) for fbs_order in fbs_orders_for_substitute_data
    )
    assert positive_result != 0


@pytest.mark.skip(reason="текущая логика МС не записывает заказы в БД")
@pytest.mark.asyncio
@time_of_completion
async def test_fetch_all_orders(
    postgresql_fixture: DatabaseJanitor,
    app,
    db_order_handler,
    values_for_insert_orders,
    values_for_insert_order_lines,
):
    pool = app[settings.DEFAULT_DATABASE]
    async with pool.acquire() as connection:
        await connection.executemany(SQL_INSERT_ORDERS, values_for_insert_orders)
        await connection.executemany(SQL_INSERT_ORDER_LINES, values_for_insert_order_lines)
    await db_order_handler.all()
    await pool.execute(
        "TRUNCATE orders, orders_line, settings; "
        "ALTER SEQUENCE orders_id_seq RESTART WITH 1; "
        "ALTER SEQUENCE orders_line_id_seq RESTART WITH 1"
    )


@pytest.mark.skip(reason="текущая логика МС не записывает заказы в БД")
@pytest.mark.asyncio
@time_of_completion
async def test_write_orders_to_db(
    app, db_order_handler: OrderDBHandler, body_request_import_orders, test_client_session
):
    requester = OrderRequester(
        app=app,
        semaphore=Semaphore(4),
        session=test_client_session,
        request_body=body_request_import_orders,
    )
    fetch_orders = await requester.fetch()

    pool = app[settings.DEFAULT_DATABASE]
    await pool.execute(
        "TRUNCATE orders, orders_line, settings; "
        "ALTER SEQUENCE orders_id_seq RESTART WITH 1; "
        "ALTER SEQUENCE orders_line_id_seq RESTART WITH 1"
    )
    await db_order_handler.insert_or_update(fetch_orders)
    orders = await db_order_handler.all()

    assert len(fetch_orders) == len(orders)
    await pool.execute(
        "TRUNCATE orders, orders_line, settings; "
        "ALTER SEQUENCE orders_id_seq RESTART WITH 1; "
        "ALTER SEQUENCE orders_line_id_seq RESTART WITH 1"
    )


def check_statuses_orders(orders):
    fbs_orders = tuple(filter(lambda order: order.get("deliveryType") in ["fbs", "dbs", "wbgo"], orders))
    empty_wb_status = tuple(filter(lambda order: not order.get("wbStatus"), fbs_orders))
    empty_supplier_status = tuple(filter(lambda order: not order.get("supplierStatus"), fbs_orders))
    assert len(empty_wb_status) == 0
    assert len(empty_supplier_status) == 0


@pytest.mark.asyncio
@time_of_completion
async def test_import_orders(running_app, body_request_import_orders):
    handler = CommonHandler(app=running_app, body=body_request_import_orders)
    result = await handler.import_orders()
    check_statuses_orders(result.data)
    assert len(result.data) > 0
    assert len(result.errors) == 0


@pytest.mark.skip(reason="текущая логика МС не записывает заказы в БД")
@pytest.mark.asyncio
@time_of_completion
async def test_read_orders_from_db(orders_lines_data: Any, db_order_handler: OrderDBHandler):
    orders = await db_order_handler.all()
    assert len(orders) > 0


async def test_import_orders_external_500(
    loop, fake_server, app, body_request_import_orders, initiate_500_status_headers
):
    # pool = app[settings.DEFAULT_DATABASE]
    body = body_request_import_orders.copy()
    body.headers = initiate_500_status_headers
    handler = CommonHandler(app=app, body=body)
    result = await handler.import_orders()
    check_statuses_orders(result.data)
    assert isinstance(result, MsgResponseToPlatform)
    # assert len(result.data) == 0


@pytest.mark.asyncio
@time_of_completion
async def test_import_orders_401_status_code(loop, fake_server, app, body_request_import_orders, auth_none_headers):
    body = body_request_import_orders.copy()
    body.headers = auth_none_headers
    # pool = app[settings.DEFAULT_DATABASE]
    handler = CommonHandler(app=app, body=body)
    result = await handler.import_orders()
    assert isinstance(result, MsgResponseToPlatform)
    # assert result.data is None

    # TODO: должен возвращать ошибки?
    # assert result.errors is not None


@pytest.mark.asyncio
@time_of_completion
async def test_import_orders_50x_status_code(
    loop, fake_server, app, body_request_import_orders, initiate_500_status_headers
):
    body = body_request_import_orders.copy()
    body.headers = initiate_500_status_headers
    # pool = app[settings.DEFAULT_DATABASE]
    handler = CommonHandler(app=app, body=body)
    result = await handler.import_orders()
    assert isinstance(result, MsgResponseToPlatform)
    # assert result.data == []

    # TODO: должен возвращать ошибки?
    # assert result.errors is not None


@pytest.mark.skip(reason="текущая логика МС не записывает заказы в БД")
@pytest.mark.asyncio
@time_of_completion
async def test_read_orders_movement_data_db(app, db_order_handler: OrderDBHandler):
    data = await db_order_handler.sql_select_movement_data()
    # Перед этим выполнить остальные тесты. чтобы заполнилась БД
    assert len(data) > 0


@pytest.mark.asyncio
@time_of_completion
async def test_collect_stock_info_from_orders_db(app, db_order_handler: OrderDBHandler):
    """Тест для проверки метода collect_stock_info_from_orders_db, который должен вернуть преобразованные данные в ItemMoveStock"""
    data = await collect_stock_info_from_orders_db(db_order_handler)
    if data:
        assert isinstance(data[0], ItemMoveStock)


@pytest.mark.asyncio
@time_of_completion
async def test_checking_order_statuses(running_app, body_request_checking_order_statuses):
    # NOTE: на данный момент тест не проверяем сам маппинг и смену статуса заказов
    # NOTE: тест проверяет общую работоспособность обработчика
    handler = CommonHandler(app=running_app, body=body_request_checking_order_statuses)
    result = await handler.checking_order_statuses()
    assert isinstance(result, MsgResponseToPlatform)
    assert len(result.data) > 0
    assert len(result.errors) == 0


@pytest.mark.asyncio
@time_of_completion
async def test_checking_order_statuses_errors(running_app, body_request_checking_order_statuses):
    """
    Имитируем ошибку, передавая некорректные данные в поле data в теле запроса
    """
    handler = CommonHandler(app=running_app, body=body_request_checking_order_statuses)
    body_request_checking_order_statuses.data = None
    result = await handler.checking_order_statuses()
    assert isinstance(result, MsgResponseToPlatform)
    assert result.data == []
    assert len(result.errors) > 0

    body_request_checking_order_statuses.data = "Invalid data type"

    result = await handler.checking_order_statuses()
    assert isinstance(result, MsgResponseToPlatform)
    assert result.data == []
    assert len(result.errors) > 0

    body_request_checking_order_statuses.data = {"orders": "invalid data schema"}

    result = await handler.checking_order_statuses()
    assert isinstance(result, MsgResponseToPlatform)
    assert result.data == []
    assert len(result.errors) > 0
