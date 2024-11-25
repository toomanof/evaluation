import pytest

from core.project.types import URLParameterSchema
from core.project.enums.common import RequestMethod

from core.apps.tests.test_fetcher_component.response_for_fetcher import ResponseExampleSchema
from core.project.conf import settings


@pytest.fixture(scope="module")
def max_count_repeat_requests():
    return settings.MAX_COUNT_REPEAT_REQUESTS


@pytest.fixture()
def base_url_params() -> URLParameterSchema:
    base_url_params = URLParameterSchema(
        method=RequestMethod.GET,
        url="",
        url_api_point="http://localhost:8083",
        has_cache=False,
        response_schema=ResponseExampleSchema,
        error_schema=None,
        title="Базовая схема для запросов на тестовый api сервер",
        positive_response_code=200,
    )
    return base_url_params
