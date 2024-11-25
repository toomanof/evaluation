from asyncio import Semaphore

import pytest

from core.apps.basic.services.handlers import CommonHandler
from core.apps.basic.services.requesters.goods import (
    ProductRequester,
    ExportPriceRequesterV2,
    NomenclatureRequest,
)
from core.project.utils import time_of_completion
from core.project.types import MsgResponseToPlatform
from icecream import ic


# NOTE: тесты на методы CreateProductRequester требуют восстановления после запуска логики

# @pytest.mark.asyncio
# @time_of_completion
# async def test_fetch_list_of_objects(app, body_request_create_card_product, test_client_session):
#     requester = CreateProductRequester(
#         app=app,
#         semaphore=Semaphore(4),
#         session=test_client_session,
#         request_body=body_request_create_card_product,
#     )
#     result = await requester.fetch_parent_subjects()
#     assert len(result) > 0
#
#
# @pytest.mark.asyncio
# @time_of_completion
# async def test_request_parent_subjects(
#     app, body_request_create_card_product, request_params_list_of_objects, test_client_session
# ):
#     requester = CreateProductRequester(
#         app=app,
#         semaphore=Semaphore(4),
#         session=test_client_session,
#         request_body=body_request_create_card_product,
#     )
#     result = await requester.fetch_list_of_objects(request_params_list_of_objects)
#     assert len(result) > 0
#
#
# @pytest.mark.asyncio
# @time_of_completion
# async def test_request_object_characteristics(
#     app, body_request_create_card_product, request_params_object_characteristics, test_client_session
# ):
#     requester = CreateProductRequester(
#         app=app,
#         semaphore=Semaphore(4),
#         session=test_client_session,
#         request_body=body_request_create_card_product,
#     )
#     result = await requester.fetch_object_characteristics(request_params_object_characteristics)
#     assert len(result) > 0


# @pytest.mark.asyncio
# @time_of_completion
# async def test_request_uncreated_nms_with_errors(app, body_request_create_card_product_local, test_client_session):
#     requester = CreateProductRequester(
#         app=app,
#         semaphore=Semaphore(4),
#         session=test_client_session,
#         request_body=body_request_create_card_product_local,
#     )
#     result = await requester.fetch_uncreated_nms_with_errors(WBRequestLocale(locale="ru"))
#     assert len(result) > 0


@pytest.mark.asyncio
@time_of_completion
async def test_export_size_goods_price(running_app, body_request_set_size_goods_price) -> None:
    """Тест для проверки функционала получения информации о размерах одного товара.

    Важно!!! Не запускать с продовскими переменными окружения!!!

    """
    handler = CommonHandler(app=running_app, body=body_request_set_size_goods_price)
    result = await handler.export_size_goods_price()
    assert isinstance(result, MsgResponseToPlatform) is True
    assert len(result.data) > 0
    assert len(result.errors) == 0


@pytest.mark.asyncio
@time_of_completion
async def test_request_import_goods_size_for_nm(
    fake_server, running_app, body_request_import_goods_size_for_nm
) -> None:
    """Тест для проверки функционала получения информации о размерах одного товара.

    Важно!!! Не запускать с продовскими переменными окружения!!!

    """
    handler = CommonHandler(app=running_app, body=body_request_import_goods_size_for_nm)
    result = await handler.import_goods_size_for_nm()
    assert isinstance(result, MsgResponseToPlatform) is True
    assert len(result.data) > 0
    assert len(result.errors) == 0


@pytest.mark.asyncio
@time_of_completion
async def test_request_import_goods_list_by_filter(app, body_request_import_goods_list_by_filter, test_client_session):
    """Тест для проверки функционала получения списка товаров.

    Важно!!! Не запускать с продовскими переменными окружения!!!

    """
    requester = ProductRequester(
        app=app,
        semaphore=Semaphore(4),
        session=test_client_session,
        request_body=body_request_import_goods_list_by_filter,
        # test=True,
    )
    result = await requester.import_goods_list_by_filter()
    ic(result)
    assert len(result.get("listGoods")) > 0


@pytest.mark.asyncio
@time_of_completion
async def test_import_goods_list(running_app, body_request_import_goods_list_by_filter, test_client_session):
    """Тест для проверки функционала получения списка товаров.

    Важно!!! Не запускать с продовскими переменными окружения!!!

    """
    handler = CommonHandler(app=running_app, body=body_request_import_goods_list_by_filter)
    result = await handler.import_goods_list()
    assert isinstance(result, MsgResponseToPlatform) is True
    assert len(result.data) > 0
    assert len(result.errors) == 0


@pytest.mark.asyncio
@time_of_completion
async def test_request_export_prices(loop, fake_server, app, body_request_export_prices, test_client_session):
    """Тест для проверки функционала экспорт цен.

    Важно!!! Не запускать с продовскими переменными окружения!!!

    """
    requester = ExportPriceRequesterV2(
        app=app,
        semaphore=Semaphore(4),
        session=test_client_session,
        request_body=body_request_export_prices,
        # test=True,
    )
    result = await requester.execute()
    assert not isinstance(result.data, list)
    assert len(result.data.data.historyGoods) > 0


@pytest.mark.asyncio
@time_of_completion
async def test_export_prices(running_app, fake_server, body_request_export_prices, test_client_session):
    """Тест для проверки функционала экспорт цен.

    Важно!!! Не запускать с продовскими переменными окружения!!!

    """
    handler = CommonHandler(app=running_app, body=body_request_export_prices)
    result = await handler.export_prices()
    assert isinstance(result, MsgResponseToPlatform) is True
    assert len(result.data.data.historyGoods) > 0
    assert len(result.errors) == 0


@pytest.mark.asyncio
@time_of_completion
async def test_export_products(running_app, fake_server, body_request_export_products, test_client_session):
    """Тест для проверки функционала экспорта товаров.

    Важно!!! Не запускать с продовскими переменными окружения!!!

    """
    handler = CommonHandler(app=running_app, body=body_request_export_products)
    result = await handler.export_products()
    assert isinstance(result, MsgResponseToPlatform) is True
    assert len(result.data) > 0
    assert len(result.errors) == 0


@pytest.mark.asyncio
@time_of_completion
async def test_request_export_prices_500_status(
    loop, fake_server, app, body_request_export_prices, initiate_500_status_headers, test_client_session
):
    """Тест для проверки функционала экспорт цен при неработающем внешнем АПИ.

    Важно!!! Не запускать с продовскими переменными окружения!!!

    """
    body = body_request_export_prices.copy()
    body.headers = initiate_500_status_headers
    requester = ExportPriceRequesterV2(
        app=app,
        semaphore=Semaphore(4),
        session=test_client_session,
        request_body=body,
        # test=True,
    )
    result = await requester.execute()
    assert isinstance(result, MsgResponseToPlatform)
    assert isinstance(result.data, list)


@pytest.mark.asyncio
@time_of_completion
async def test_request_import_goods_list_by_filter_500_status(
    app, body_request_import_goods_list_by_filter, initiate_500_status_headers, test_client_session
):
    """Тест для проверки функционала получения списка товаров при неработабщем внешнем АПИ.

    Важно!!! Не запускать с продовскими переменными окружения!!!

    """
    body = body_request_import_goods_list_by_filter.copy()
    body.headers = initiate_500_status_headers
    requester = ProductRequester(
        app=app,
        semaphore=Semaphore(4),
        session=test_client_session,
        request_body=body,
        # test=True,
    )
    result = await requester.import_goods_list_by_filter()
    assert isinstance(result, dict)


@pytest.mark.asyncio
@time_of_completion
async def test_request_fetch_nomenclature(
    running_app,
    body_request_import_stock,
):
    requester = NomenclatureRequest(
        app=running_app,
        session=running_app["session"],
        semaphore=Semaphore(4),
        # NOTE: фикструа импорта стока, тк именно эти данные придут из пайплайна вызовов при импорте остатков
        request_body=body_request_import_stock,
        test=True,
    )
    result = await requester.fetch_nomenclature()
    ic(len(result))
    assert len(result) > 0
