import asyncio

from datetime import datetime
from typing import Any, List, Tuple
from unittest import mock
from unittest.mock import Mock

from aiohttp import web, ClientSession
from aiohttp.web_app import Application
from aiohttp.test_utils import make_mocked_coro
from icecream import ic
from pytest_asyncio import fixture
from pytest_postgresql.janitor import DatabaseJanitor, Connection

from core.apps.basic.types.from_platform import RelationProduct
from core.apps.basic.services.database_workers.orders import OrderDBHandler
from core.apps.basic.types import (
    WBFBSOrder,
    WBFBOOrder,
    WBRequestListOfObjects,
    WBRequestObjectCharacteristics,
)
from core.project.conf import settings
from core.project.db.connect import destroy_database_pool, create_test_database_pool
from core.project.db.execute_migrations import create_tables
from core.project.services.requesters.fetcher import Fetcher
from core.project.types import MsgSendStartEventInMSMarketplace, ParamsView
from core.apps.basic.sql_commands.orders import (
    SQL_INSERT_ORDERS,
    SQL_INSERT_ORDER_LINES,
)
from core.apps.utils import BaseExternalClient
from core.tests.test_server import app as test_app
from core.tests.src.factories.suppliers.responses import (
    RelationProductFactory,
    DataExportStockFactory,
    ResponseChangeStatusOrderFromMsFactory,
)
from core.tests.src.factories import TEST_PRODUCTS_IDS_RANGE
from core.tests.src.factories.content.responses import WBNomenclatureFactory

_headers = {
    "Content-Type": "application/json",
    "Authorization": f"{settings.TEST_API_KEY}",
}


@fixture(scope="session")
def platform_relation_products():
    platform_relation_products: list[RelationProduct] = RelationProductFactory.batch(size=len(TEST_PRODUCTS_IDS_RANGE))
    platform_relation_products_dumped: list[dict] = [row.model_dump() for row in platform_relation_products]
    return platform_relation_products_dumped


@fixture(scope="session")
def orders_for_checking_orders_statuses():
    payload = ResponseChangeStatusOrderFromMsFactory.batch(10)
    return [row.model_dump() for row in payload]


@fixture
def auth_none_headers():
    return {"Content-Type": "application/json", "Authorization": "not valid key"}


@fixture
def initiate_500_status_headers():
    headers: dict = _headers.copy()
    headers.update({"RAISE_500": "true"})
    return headers


class SandBoxPricesApiClient(BaseExternalClient):
    def __init__(self):
        """
        Function to initialise the Prices API Class
        """
        self.headers = _headers
        self.base_url = settings.SANDBOX_API_PRICES_URL


class MockResponse:
    def __init__(self, text, status):
        self._text = text
        self.status = status

    async def text(self):
        return self._text

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        return self


@fixture(autouse=True, scope="session")
async def fake_server():
    runner = web.AppRunner(test_app)
    await runner.setup()
    site = web.TCPSite(runner, "localhost", 8083)

    await site.start()
    print("Fake server is running at http://localhost:8083")

    yield

    await runner.cleanup()


@fixture
def patched_loop(loop: Any):
    server = mock.Mock()
    server.wait_closed = make_mocked_coro(None)
    loop.create_server = make_mocked_coro(server)
    unix_server = mock.Mock()
    unix_server.wait_closed = make_mocked_coro(None)
    loop.create_unix_server = make_mocked_coro(unix_server)
    try:
        asyncio.set_event_loop(loop)
    except Exception as err:
        ic(err)
    return loop


def stopper(loop: Any):
    def raiser():
        raise KeyboardInterrupt

    def f(*args):
        loop.call_soon(raiser)

    return f


async def _client_session(app: Application):
    """
    Создание глобальной ClientSession
    """
    print("Создается ClientSession")
    session = ClientSession()
    app["session"] = session
    yield
    print("Закрывается ClientSession")
    await session.close()


@fixture(scope="session")
async def app():
    app = web.Application()
    app.on_startup.append(create_test_database_pool)
    app.on_startup.append(create_tables)
    app.cleanup_ctx.append(_client_session)
    app.on_cleanup.append(destroy_database_pool)
    runner = web.AppRunner(app)
    await runner.setup()
    return app


@fixture(scope="module")
async def running_app():
    app = web.Application()
    app.on_startup.append(create_test_database_pool)
    app.on_startup.append(create_tables)
    app.on_cleanup.append(destroy_database_pool)
    app.cleanup_ctx.append(_client_session)
    runner = web.AppRunner(app)
    await runner.setup()
    print("Запускается тестовое приложение app")
    yield app
    print("\nОстанавливается тестовое приложение app")
    await runner.cleanup()


@fixture(scope="session")
def fetcher():
    return Fetcher()


@fixture(scope="session", autouse=True)
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@fixture
async def test_client_session():
    print("Создается ClientSession")
    session = ClientSession()
    yield session
    print("Закрывается ClientSession")
    # await session.close()


@fixture
def auth_headers():
    headers1 = {
        "Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjMxMjI1djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTcyMTc2NzMzOCwiaWQiOiIyYTk2YTA3MC0yMTY5LTRlNjYtYTk1OC0yYzM2YTQzN2QyZDUiLCJpaWQiOjIwMzEzMzIwLCJvaWQiOjMzMzIwLCJzIjo1MTAsInNpZCI6ImE0YjY2M2YyLWFiNDAtNWU3Yy04YWVhLTYyZDlhZWJhYTJhZiIsInQiOmZhbHNlLCJ1aWQiOjIwMzEzMzIwfQ.lhHWpGDEq7WxpSa-Kd9z3ozK7PqP_dJJCYwwVJc8lXLhlJLcBbMEczLVVmvNjIQzi9VzUyOwmqyew7QnCCgc3A"
    }
    headers2 = {
        "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NJRCI6IjcxOWRkNTM3LTliMDktNDdkNC05YTQ4LTZlNDZjYjZmNThkNSJ9.SeUy9mR1aqKyAVKoi85b3bnlO68DkNbKVxvCDSfHE3k"
    }
    return headers1, headers2


@fixture
def auth_headers_for_statistics():
    headers1 = {
        "Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjMxMDI1djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTcxNTk4OTc3OCwiaWQiOiI1NWVlMjYwOC1kZTk1LTQ5Y2UtYjZmYy1mNjU0NTdmZDVlMjciLCJpaWQiOjIwMzEzMzIwLCJvaWQiOjMzMzIwLCJzIjo1MTAsInNpZCI6ImE0YjY2M2YyLWFiNDAtNWU3Yy04YWVhLTYyZDlhZWJhYTJhZiIsInVpZCI6MjAzMTMzMjB9.UcLczcZiAEbgT3C4wQgdP69Z0bCNW1-QFnWzR1zbnkrFrMYPNa_UHJl4fRyrUCnzso2gG1N8UzRXR2ydD-zX3g"
    }
    headers2 = {
        "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NJRCI6IjNlNGIyZjFiLTkzNDktNDAzMi04NGNhLWY1ZmRjNDk4ZDYwMiJ9.pzSWaX7DsTxM8bP6uvto-A2kxio7nEkks60Nxu3Q6i8"
    }
    return headers1, headers2


@fixture
def wb_products_in_platform():
    nomenclature: list = WBNomenclatureFactory.batch(10)
    data = {"items": [item.model_dump() for item in nomenclature]}
    return data


@fixture
def body_request_import_stock(auth_headers):
    headers, _ = auth_headers
    return MsgSendStartEventInMSMarketplace(
        headers=_headers,
        task_id=122343,
        marketplace_id=5,
        company_id=23,
        event_id="21323421412sdfgwer",
        event="import_stock",
        callback="result_import_stocks",
        token="23413qewrfsdfqsdf2342",
    )


@fixture
def body_request_import_stock_fbo(auth_headers, platform_relation_products):
    headers, _ = auth_headers
    return MsgSendStartEventInMSMarketplace(
        headers=_headers,
        task_id=122343,
        marketplace_id=5,
        company_id=23,
        event_id="21323421412sdfgwer",
        event="import_stock",
        callback="result_import_stocks_fbo",
        token="23413qewrfsdfqsdf2342",
        add_info={"relation_products": platform_relation_products},
    )


@fixture
def body_request_export_stock(auth_headers):
    headers, _ = auth_headers
    return MsgSendStartEventInMSMarketplace(
        headers=_headers,
        task_id=122343,
        marketplace_id=5,
        company_id=23,
        event_id="21323421412sdfgwer",
        event="export_stock",
        callback="result_export_stocks",
        token="23413qewrfsdfqsdf2342",
        data=DataExportStockFactory.build().model_dump(),
    )


@fixture
def body_request_import_warehouses(auth_headers):
    headers, _ = auth_headers
    return MsgSendStartEventInMSMarketplace(
        headers=_headers,
        task_id=122343,
        marketplace_id=5,
        company_id=23,
        event_id="21323421412sdfgwer",
        event="import_warehouses",
        callback="result_import_warehouses",
    )


@fixture
def body_request_import_orders(auth_headers, platform_relation_products):
    headers, _ = auth_headers
    return MsgSendStartEventInMSMarketplace(
        headers=_headers,
        task_id=122343,
        marketplace_id=5,
        company_id=23,
        event_id="21323421412sdfgwer",
        event="import_orders",
        callback="result_import_orders",
        add_info={"relation_products": platform_relation_products},
    )


@fixture
def body_request_checking_order_statuses(auth_headers, orders_for_checking_orders_statuses):
    headers, _ = auth_headers
    return MsgSendStartEventInMSMarketplace(
        headers=_headers,
        task_id=122343,
        marketplace_id=5,
        company_id=23,
        event_id="21323421412sdfgwer",
        event="checking_order_statuses",
        callback="result_checking_order_statuses",
        data={"orders": orders_for_checking_orders_statuses},
    )


@fixture
def body_request_import_orders_fbo(auth_headers_for_statistics):
    headers, _ = auth_headers_for_statistics
    return MsgSendStartEventInMSMarketplace(
        headers=_headers,
        task_id=122343,
        marketplace_id=5,
        company_id=23,
        event_id="21323421412sdfgwer",
        event="import_orders",
        callback="result_import_orders",
    )


@fixture
def mock_fetch():
    mock_ = Mock()
    mock_.fetch_method.return_value = MockResponse(text="OK", status=429)
    return mock_


@fixture
def customer_id_and_marketplace_id():
    return 23, 56


@fixture
def values_for_insert_orders(customer_id_and_marketplace_id):
    company_id, marketplace_id = customer_id_and_marketplace_id
    return [
        (
            "234234",
            "2023-03-16",
            "34563532",
            company_id,
            marketplace_id,
            34522,
            None,
            None,
            "progress",
            "RUB",
            1000,
            None,
            "FBO",
        ),
        (
            "234234546",
            "2023-03-17",
            "345633465532",
            company_id,
            marketplace_id,
            34522,
            None,
            None,
            "progress",
            "RUB",
            1400,
            None,
            "FBS",
        ),
    ]


@fixture
def values_for_insert_order_lines():
    return [
        ("234234", 2332443, 1, 1000, None),
        ("234234546", 567322, 1, 1400, None),
    ]


@fixture
async def db_order_handler(
    app,
    patched_loop,
    customer_id_and_marketplace_id,
):
    runner = web.AppRunner(app)
    await runner.setup()
    pool = app[settings.DEFAULT_DATABASE]
    company_id, marketplace_id = customer_id_and_marketplace_id
    return OrderDBHandler(
        pool=pool,
        params=ParamsView(company_id=company_id, marketplace_id=marketplace_id),
    )


@fixture
def fix_wb_order():
    return [
        WBFBSOrder(
            id=1263414902,
            rid="29474179585952017.0.0",
            createdAt="2023-12-07T11:34:45Z",
            warehouseId=581000,
            supplyId="WB-GI-67639767",
            offices=["Ростов-на-Дону"],
            address=None,
            user=None,
            skus=["4607177452845"],
            price=32600,
            convertedPrice=326,
            currencyCode=643,
            convertedCurrencyCode=643,
            orderUid="40948359_29474179585952017",
            deliveryType="fbs",
            nmId=50393865,
            chrtId=95889770,
            article="46071774528454607177452845geo",
            isLargeCargo=None,
            supplierStatus=None,
            wbStatus=None,
            nomenclature="Игра-ходилка. Животный мир Земли.",
        ),
        WBFBOOrder(
            gNumber="9407846642480231815",
            date=datetime(2023, 12, 7, 14, 9),
            lastChangeDate=datetime(2023, 12, 7, 14, 22, 4),
            supplierArticle="4660136226833",
            techSize="0",
            barcode="4660136226833",
            totalPrice=999.0,
            discountPercent=41,
            warehouseName="Коледино",
            oblast=None,
            incomeID=0,
            odid=None,
            nmId=169103447,
            subject="Настольные игры",
            category="Игрушки",
            brand="ГЕОДОМ",
            isCancel=False,
            cancel_dt=None,
            sticker="16384493813",
            srid="19851927085951269.1.0",
            orderType="Клиентский",
            nomenclature="Мафия 2077. Карточная игра для компании",
        ),
    ]


@fixture
def body_request_create_card_product(auth_headers):
    headers, _ = auth_headers
    return MsgSendStartEventInMSMarketplace(
        headers=headers,
        task_id=122343,
        marketplace_id=5,
        company_id=23,
        event_id="21323421412sdfgwer",
        event="create_product",
        callback="result_create_product",
    )


@fixture
def body_request_create_card_product_local():
    return MsgSendStartEventInMSMarketplace(
        headers=_headers,
        task_id=122343,
        marketplace_id=5,
        company_id=23,
        event_id="21323421412sdfgwer",
        event="create_product",
        callback="result_create_product",
    )


@fixture
def request_params_list_of_objects():
    return WBRequestListOfObjects(parentID=7, limit=10)


@fixture
def request_params_object_characteristics():
    return WBRequestObjectCharacteristics(subjectId=7, locale="ru")


@fixture
def body_request_export_price_and_discounts(auth_headers):
    # headers, _ = auth_headers
    return MsgSendStartEventInMSMarketplace(
        headers=_headers,
        task_id=122343,
        marketplace_id=5,
        company_id=23,
        event_id="21323421412sdfgwer",
        event="export_price_and_discounts",
        callback="result_export_price_and_discounts",
        data={"data": [{"nmID": 12323, "price": 100, "discount": 15}]},
    )


@fixture
def body_request_download_processed_status(auth_headers):
    # headers, _ = auth_headers
    return MsgSendStartEventInMSMarketplace(
        headers=_headers,
        task_id=122343,
        marketplace_id=5,
        company_id=23,
        event_id="21323421412sdfgwer",
        event="download_processed_status",
        callback="result_download_processed_status",
        data={"uploadID": 146567},
    )


@fixture
def body_request_processed_load_details(auth_headers):
    # headers, _ = auth_headers
    return MsgSendStartEventInMSMarketplace(
        headers=_headers,
        task_id=122343,
        marketplace_id=5,
        company_id=23,
        event_id="21323421412sdfgwer",
        event="download_processed_status",
        callback="result_download_processed_status",
        data={"limit": 10, "offset": 0, "uploadID": 146567},
    )


@fixture
def body_request_load_progress(auth_headers):
    # headers, _ = auth_headers
    return MsgSendStartEventInMSMarketplace(
        headers=_headers,
        task_id=122343,
        marketplace_id=5,
        company_id=23,
        event_id="21323421412sdfgwer",
        event="raw_load_progress",
        callback="result_raw_load_progress",
        data={"uploadID": 146567},
    )


@fixture
def body_request_set_size_goods_price():
    return MsgSendStartEventInMSMarketplace(
        headers=_headers,
        task_id=122343,
        marketplace_id=5,
        company_id=23,
        event_id="21323421412sdfgwer",
        event="export_size_goods_price",
        callback="result_export_size_goods_price",
        data={"data": [{"nmID": 253, "sizeID": 252, "price": 1000}]},
    )


@fixture
def body_request_import_goods_size_for_nm():
    return MsgSendStartEventInMSMarketplace(
        headers=_headers,
        task_id=122343,
        marketplace_id=5,
        company_id=23,
        event_id="21323421412sdfgwer",
        event="import_goods_size_for_nm",
        callback="result_import_goods_size_for_nm",
        data={"limit": 10, "offset": 0, "nmID": 253},
    )


@fixture
def body_request_import_goods_list_by_filter():
    return MsgSendStartEventInMSMarketplace(
        headers=_headers,
        task_id=122343,
        marketplace_id=5,
        company_id=23,
        event_id="21323421412sdfgwer",
        event="import_goods_list_by_filter",
        callback="result_import_goods_list_by_filter",
        data={"limit": 10, "offset": 0, "filterNmID": 253, "test": 123},
    )


@fixture
def body_request_export_prices():
    return MsgSendStartEventInMSMarketplace(
        headers=_headers,
        task_id=122343,
        marketplace_id=5,
        company_id=23,
        event_id="21323421412sdfgwer",
        event="export_prices",
        callback="result_export_prices",
        data={"data": [{"nmID": 253, "discount": 12, "price": 1000}]},
    )


@fixture
def body_request_export_products(auth_headers, wb_products_in_platform):
    return MsgSendStartEventInMSMarketplace(
        headers=_headers,
        task_id=122343,
        marketplace_id=5,
        company_id=23,
        event_id="21323421412sdfgwer",
        event="export_products",
        callback="result_export_products",
        data=wb_products_in_platform,
    )


@fixture
def postgresql_fixture(postgresql: Connection):
    database_configuration = settings.DATABASES.get(settings.TEST_DATABASE, {}) or None
    assert database_configuration is not None
    janitor = DatabaseJanitor(
        user=database_configuration.get("user"),
        host=database_configuration.get("host"),
        port=database_configuration.get("port"),
        dbname=database_configuration.get("database"),
        password=database_configuration.get("password"),
        version=postgresql.info.server_version,
    )
    try:
        janitor.init()
    except (Exception,):
        pass
    yield janitor
    janitor.drop()


@fixture
async def orders_lines_data(
    postgresql_fixture: DatabaseJanitor,
    app: web.Application,
    values_for_insert_order_lines: List[Tuple],
    values_for_insert_orders: List[Tuple],
):
    runner = web.AppRunner(app=app)
    await runner.setup()
    # TODO: prepare pool from postgresql_fixture
    pool = app.get(settings.DEFAULT_DATABASE)
    assert pool is not None
    async with pool.acquire() as connection:
        await connection.executemany(
            command=SQL_INSERT_ORDERS,
            args=values_for_insert_orders,
        )
        await connection.executemany(
            command=SQL_INSERT_ORDER_LINES,
            args=values_for_insert_order_lines,
        )


@fixture
def random_pydantic_model_message():
    return MsgSendStartEventInMSMarketplace(
        headers=_headers,
        task_id=122343,
        marketplace_id=5,
        company_id=23,
        event_id="21323421412sdfgwer",
        event="export_prices",
        callback="result_export_prices",
        data={"data": [{"nmID": 253, "discount": 12, "price": 1000}]},
    )


@fixture
def fbs_orders_for_substitute_data():
    return [
        WBFBSOrder(
            id=1,
            id_order="dwqerqr34",
            rid="1234",
            createdAt="12.03.2004",
            warehouseId=124,
            skus=["1", "2"],
            nmId=1,
            chrtId=1,
        ),
        WBFBSOrder(
            id=2,
            id_order="dwqerq",
            rid="19851927085951269.1.0",
            createdAt="12.03.2004",
            warehouseId=124,
            skus=["1", "2"],
            nmId=1,
            chrtId=1,
        ),
    ]


@fixture
def fbo_orders_for_substitute_data():
    return [
        WBFBOOrder(
            gNumber="9407846642480231815",
            date=datetime(2023, 12, 7, 14, 9),
            lastChangeDate=datetime(2023, 12, 7, 14, 22, 4),
            supplierArticle="4660136226833",
            techSize="0",
            barcode="4660136226833",
            totalPrice=999.0,
            discountPercent=41,
            spp=300.0,
            finishedPrice=699.0,
            priceWithDisc=599.0,
            warehouseName="Коледино",
            incomeID=0,
            nmId=169103447,
            subject="Настольные игры",
            category="Игрушки",
            brand="ГЕОДОМ",
            isCancel=False,
            sticker="16384493813",
            srid="19851927085951269.1.0",
            orderType="Клиентский",
            nomenclature="Мафия 2077. Карточная игра для компании",
            isSupply=False,
            isRealization=False,
        ),
        WBFBOOrder(
            gNumber="9407846642480231815",
            date=datetime(2023, 12, 7, 14, 9),
            lastChangeDate=datetime(2023, 12, 7, 14, 22, 4),
            supplierArticle="4660136226833",
            techSize="0",
            barcode="4660136226833",
            totalPrice=999.0,
            discountPercent=41,
            spp=300.0,
            finishedPrice=699.0,
            priceWithDisc=599.0,
            warehouseName="Коледино",
            incomeID=0,
            nmId=169103447,
            subject="Настольные игры",
            category="Игрушки",
            brand="ГЕОДОМ",
            sticker="16384493813",
            srid="169.1.0",
            orderType="Клиентский",
            nomenclature="Мафия 2077. Карточная игра для компании",
            isSupply=False,
            isRealization=False,
            isCancel=False,
        ),
    ]
