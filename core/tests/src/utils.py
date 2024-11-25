import json
import os

from pydantic import BaseModel
from typing import TypeVar, Type
from .exceptions import (
    InvalidRequestFormatContent,
    InvalidQueryParamsContent,
    RouterIsDeprecated,
    Unauthorized,
    ServerUnavailable,
)
from pydantic_core._pydantic_core import ValidationError

T = TypeVar("T", bound=BaseModel)


# =============PRICES_AND_DISCOUNTS_API=================
def check_query_params_prices_api(pydantic_schema: Type[T], params: dict):
    error_struct = {"data": {}, "error": True, "errorText": "Invalid query params"}
    try:
        pydantic_schema.model_validate(params)
    except ValidationError:
        raise InvalidQueryParamsContent(text=json.dumps(error_struct), content_type="application/json")


def check_request_body_schema_prices_api(pydantic_schema: Type[T], body: dict):
    """Рейзит ошибку в случае, если входящие данные не соотвуствуют нужной схеме.

    pydantic_schema -- схема для проверки данных
    body -- полученные данные

    """

    error_struct = {
        "data": None,
        "error": True,
        "errorText": "Body data not valid",
    }
    try:
        pydantic_schema.model_validate(body)
    except ValidationError:
        raise InvalidRequestFormatContent(text=json.dumps(error_struct), content_type="application/json")


def make_route_deprecated(date=None):
    """Метод для вывода роута из работы.

    В качестве аргумента можно передать дату, когда роутер перестает работать
    """
    error_struct = {
        "data": None,
        "error": True,
        "errorText": "Router is DEPRECATED" if not date else f"Router is DEPRECATED ({date})",
    }
    raise RouterIsDeprecated(text=json.dumps(error_struct), content_type="application/json")


def check_auth_prices_api(headers):
    error_struct = {"data": {"type": "object", "nullable": True}, "error": True, "errorText": "Authorization error"}
    if not headers.get("Authorization", None) or headers.get("Authorization") != os.environ.get("TEST_API_KEY"):
        raise Unauthorized(text=json.dumps(error_struct), content_type="application/json")


# =============SUPPLIERS_API=================


def check_query_params_suppliers_api(pydantic_schema: Type[T], params: dict):
    error_struct = {"data": None, "code": "IncorrectParameter", "message": "Передан некорректный параметр"}
    try:
        pydantic_schema.model_validate(params)
    except ValidationError:
        raise InvalidQueryParamsContent(text=json.dumps(error_struct), content_type="application/json")


def check_request_body_schema_suppliers_api(pydantic_schema: Type[T], body: dict):
    """Рейзит ошибку в случае, если входящие данные не соотвуствуют нужной схеме.

    pydantic_schema -- схема для проверки данных
    body -- полученные данные

    """

    error_struct = {"data": None, "code": "IncorrectParameter", "message": "Передан некорректный параметр"}
    try:
        pydantic_schema.model_validate(body)
    except ValidationError:
        raise InvalidRequestFormatContent(text=json.dumps(error_struct), content_type="application/json")


def check_auth_suppliers_api(headers):
    if not headers.get("Authorization", None) or headers.get("Authorization") != os.environ.get("TEST_API_KEY"):
        raise Unauthorized(text=json.dumps({"code": 401, "message": "unauthorized"}), content_type="application/json")


def raise_exception_controller(headers, api_name=None):
    text = None
    if api_name == "prices":
        text = {"data": {}, "error": True, "errorText": "Internal server error"}
    else:
        text = {"data": None, "code": "InternalServerError", "message": "Внутренняя ошибка сервиса"}

    print(headers.get("RAISE_500"), 'headers.get("RAISE_500")')
    if headers.get("RAISE_500"):
        raise ServerUnavailable(text=json.dumps(text, ensure_ascii=False), content_type="application/json")
