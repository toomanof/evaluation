from pydantic import BaseModel, ConfigDict

from core.apps.basic.types import WBResponseError


class ResponseExampleSchema(BaseModel):
    result: dict = {"key1": "val1"}

    model_config = ConfigDict(extra="forbid")


def _get_error(code: int, msg: str) -> dict:
    error = WBResponseError(code=str(code), message=msg)
    return error.model_dump()


error_500 = _get_error(code=500, msg="Внутренняя ошибка сервера Маркета")

error_429 = _get_error(code=429, msg="Превышено допустимое кол-во запросов в единицу времени")

error_409 = _get_error(code=409, msg="Конфликт запроса")

error_404 = _get_error(code=404, msg="Ответ не найден")

error_403 = _get_error(code=403, msg="Доступ запрещен")

error_401 = _get_error(code=401, msg="В запросе не указан авторизационный токен")

error_400 = _get_error(code=400, msg="Неверный параметр")

ROUTE_PAYLOAD_RESPONSE_MAPPER = {
    "/get_200_json": {
        "payload": ResponseExampleSchema().model_dump(),
        "expected_response": ResponseExampleSchema,
    },
    "/get_200_text": {
        "payload": ResponseExampleSchema().model_dump_json(),
        "expected_response": ResponseExampleSchema,
    },
    "/get_500": {
        "payload": error_500,
        "expected_response": [
            error_500,
            error_500,
            {"Данные не получены": "Превышено количество допустимых попыток запроса"},
        ],
    },
    "/get_429": {
        "payload": error_429,
        "expected_response": [
            error_429,
            error_429,
            {"Данные не получены": "Превышено количество допустимых попыток запроса"},
        ],
    },
    "/get_400": {"payload": error_400, "expected_response": [error_400]},
    "/get_401": {"payload": error_401, "expected_response": [error_401]},
    "/get_403": {"payload": error_403, "expected_response": [error_403]},
    "/get_404": {"payload": error_404, "expected_response": [error_404]},
    "/get_409": {"payload": error_409, "expected_response": [error_409]},
}


def get_positive_cases() -> list[tuple]:
    positive_response_paths = ["/get_200_json", "/get_200_text"]
    cases = []
    for path in positive_response_paths:
        case = (path, ROUTE_PAYLOAD_RESPONSE_MAPPER.get(path)["expected_response"])
        cases.append(case)
    return cases


def get_error_for_repeat_cases() -> list[tuple]:
    error_response_paths_for_repeat = ["/get_500", "/get_429"]
    cases = []
    for path in error_response_paths_for_repeat:
        case = (path, ROUTE_PAYLOAD_RESPONSE_MAPPER.get(path)["expected_response"])
        cases.append(case)
    return cases


def get_error_cases() -> list[tuple]:
    error_response_paths = ["/get_400", "/get_401", "/get_403", "/get_404", "/get_409"]
    cases = []
    for path in error_response_paths:
        case = (path, ROUTE_PAYLOAD_RESPONSE_MAPPER.get(path)["expected_response"])
        cases.append(case)
    return cases
