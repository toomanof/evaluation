import pytest
from asyncio import Semaphore
from core.project.utils import time_of_completion
from core.project.services.requesters.fetcher import FetchResponse

from pydantic import BaseModel

from core.apps.tests.test_fetcher_component.response_for_fetcher import (
    get_positive_cases,
    get_error_for_repeat_cases,
    get_error_cases,
)


class InvalidResponseSchema(BaseModel):
    some_field: list[dict]


@pytest.mark.asyncio
@pytest.mark.parametrize("url , schema", get_positive_cases())
@time_of_completion
async def test_fetcher_positive_response(
    fake_server,
    test_client_session,
    fetcher,
    base_url_params,
    # params
    url,
    schema,
):
    url_params = base_url_params
    url_params.url = url

    request_result = await fetcher(
        semaphore=Semaphore(4),
        session=test_client_session,
        url_params=url_params,
        params=None,
        headers={},
        valid_type_positive=url_params.response_schema,
    )
    assert isinstance(request_result, FetchResponse)
    assert request_result.fetch_errors == []
    assert isinstance(request_result.fetch_result, schema)


@pytest.mark.asyncio
@time_of_completion
async def test_fetcher_no_response_schema_defined(
    fake_server,
    test_client_session,
    fetcher,
    base_url_params,
):
    """
    Если не задана схема валидации ответа api(valid_type_positive=None),
    то это ошибка в работе микросервиса.
    Нельзя обрабатывать не провалидированный ответ от api.
    """
    url_params = base_url_params
    url_params.response_schema = None
    request_result = await fetcher(
        semaphore=Semaphore(4),
        session=test_client_session,
        url_params=url_params,
        params=None,
        headers={},
        valid_type_positive=None,
    )
    assert isinstance(request_result, FetchResponse)
    assert request_result.fetch_result is None
    assert request_result.fetch_errors != []


@pytest.mark.asyncio
@time_of_completion
async def test_fetcher_validation_errors(fake_server, test_client_session, fetcher, base_url_params):
    """
    Проверяем запись ошибок валидации pydantic. Либо задана не та схема
    для валидации ответа api, либо структура ответа api по endpoint была
    изменена и необходимо актуализировать схему валидации и,
    возможно, логику дальнейшей обработки
    """
    url_params = base_url_params
    url_params.url = "/get_200_json"

    request_result = await fetcher(
        semaphore=Semaphore(4),
        session=test_client_session,
        url_params=url_params,
        params=None,
        headers={},
        valid_type_positive=InvalidResponseSchema,
    )
    assert isinstance(request_result, FetchResponse)
    assert request_result.fetch_result is None
    assert request_result.fetch_errors != []


@pytest.mark.asyncio
@pytest.mark.parametrize("url , expected_response", get_error_for_repeat_cases())
@time_of_completion
async def test_fetcher_errors_with_retrying(
    fake_server,
    test_client_session,
    fetcher,
    base_url_params,
    max_count_repeat_requests,
    # params
    url,
    expected_response,
):
    base_url_params.url = url
    request_result = await fetcher(
        semaphore=Semaphore(4),
        session=test_client_session,
        url_params=base_url_params,
        params=None,
        headers={},
        valid_type_positive=None,
        valid_type_negative=None,
    )
    assert isinstance(request_result, FetchResponse)
    assert request_result.fetch_result is None
    assert (
        len(request_result.fetch_errors) == max_count_repeat_requests + 1
    )  # 3 ошибки запросов с повторами + ошибки о превышении количества попыток
    assert request_result.fetch_errors == expected_response


@pytest.mark.asyncio
@pytest.mark.parametrize("url , expected_response", get_error_cases())
@time_of_completion
async def test_fetcher_errors_no_retrying(
    fake_server,
    test_client_session,
    fetcher,
    base_url_params,
    # params
    url,
    expected_response,
):
    base_url_params.url = url
    request_result = await fetcher(
        semaphore=Semaphore(4),
        session=test_client_session,
        url_params=base_url_params,
        params=None,
        headers={},
        valid_type_positive=None,
        valid_type_negative=None,
    )
    assert isinstance(request_result, FetchResponse)
    assert request_result.fetch_result is None
    assert request_result.fetch_errors != []


@pytest.mark.asyncio
@time_of_completion
async def test_fetcher_no_data_from_request(fake_server, test_client_session, fetcher, base_url_params):
    base_url_params.url = "/get_no_data"
    request_result = await fetcher(
        semaphore=Semaphore(4),
        session=test_client_session,
        url_params=base_url_params,
        headers={},
    )
    assert isinstance(request_result, FetchResponse)
    assert request_result.fetch_result is None
    assert request_result.fetch_errors == []


@pytest.mark.asyncio
@time_of_completion
async def test_fetcher_clientsession_error(test_client_session, fetcher, base_url_params):
    """
    Эмулируем ошибку сети, делая запрос по некорректно составленному url (не указываем протокол).
    Данный кейс выбран для упрощения, тк fake_server запускается по умолчанию
    один раз со scope=session, что менее накладно, чем стартовать тестовый сервер для
    каждого теста.
    В дальнейшем можно будет прописать логику остановки тестового сервера.
    """
    base_url_params.url_api_point = "localhost:7777"

    request_result = await fetcher(
        semaphore=Semaphore(4),
        session=test_client_session,
        url_params=base_url_params,
        headers={},
    )
    assert isinstance(request_result, FetchResponse)
    assert request_result.fetch_result is None
    assert (
        len(request_result.fetch_errors) == 3
    )  # 3 ошибки запросов с повторами + ошибки о превышении количества попыток
    assert request_result.fetch_errors[-1] == {"Данные не получены": "Превышено количество допустимых попыток запроса"}
