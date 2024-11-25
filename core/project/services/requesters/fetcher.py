import asyncio
import hashlib
import logging
import os
import traceback

import yaml
import json

from asyncio import Semaphore
from aiohttp import ClientSession, ClientResponse, ClientError
from typing import Optional, Callable, Type, Any

from icecream import ic
from pydantic import BaseModel, Field, ValidationError
from datetime import datetime

from core.project.types import URLParameterSchema
from core.apps.basic.types import ListBaseModel
from core.project.conf import settings
from core.apps.constants import (
    HTTP_RESPONSE_CODES_FOR_REPEAT_REQUEST,
    HTTP_RESPONSE_CODES_ACCESS_DENIED,
    HTTP_RESPONSE_CODES_STOP_REQURESTS,
)
from core.project.enums.common import RequestMethod
from core.project.utils import (
    full_url,
    dict_fetch_method,
    get_cache_handler_or_none,
    get_auth_header_access_denied_set,
)

logger_error = logging.getLogger("errors")
logger_info = logging.getLogger("info")


class ValidationResult(BaseModel):
    valid_data: Optional[Type[BaseModel]] = None
    response_schema_error: bool = False


class FetchResponse(BaseModel):
    fetch_result: Optional[Type[BaseModel]] = None
    fetch_errors: Optional[list[dict]] = Field(default_factory=list)
    response_code: Optional[int] = None


class Fetcher:
    def __init__(self):
        self.requests_logs = None
        self.num_attempt_request = 0

    async def __call__(
        self,
        semaphore: Semaphore,
        session: ClientSession,
        url_params: URLParameterSchema,
        headers: dict,
        params: Optional[dict] = None,
        valid_type_positive: Optional[Type[BaseModel] | Type[str]] = None,
        valid_type_negative: Optional[Type[BaseModel]] = None,
        test: bool = False,
    ):
        self.errors: Optional[list[Any]] = []
        self.session = session
        self.semaphore = semaphore
        self.url_params = url_params
        self.headers = headers
        self.params = params
        self.valid_type_positive = valid_type_positive
        self.valid_type_negative = valid_type_negative
        self.requests_logs = self.get_yml_logs()
        self.file_log_requests = os.path.join(settings.PATH_LOGGERS, "requests.yml")
        self.auth_header = settings.API_AUTH_HEADER
        self.num_attempt_request = self.get_num_attempt_request()
        self.test = test
        return await self.make_marketplace_api_request()

    async def add_auth_header_to_access_denied_list(self):
        cache = get_cache_handler_or_none()
        set_auth_headers_access_denied = await get_auth_header_access_denied_set()
        set_auth_headers_access_denied.add(self.headers.get(self.auth_header))
        if cache:
            await cache.set("access_denied_headers", list(set_auth_headers_access_denied), ttl=3600)

    def add_headers(self):
        self.headers["Content-Type"] = "application/json"

    @staticmethod
    def add_log_info(text):
        if settings.DEBUG:
            logger_error.info(f"{datetime.now()}:\t{text}")

    @staticmethod
    def add_log_error(error):
        logger_error.error(f"{datetime.now()}:\t{error}")

    async def attempt_fetch(self) -> FetchResponse:
        def attempts_result_with_error(err: dict):
            attempts_result.fetch_errors.append(err)
            self.add_log_error(err)
            return attempts_result

        attempts_result = FetchResponse()
        if not await self.checking_can_request():
            return attempts_result_with_error({"Запрос для ключа доступа закрыт!": self.headers})

        for retry_num in range(1, int(settings.MAX_COUNT_REPEAT_REQUESTS) + 1):
            try:
                await self.checking_need_to_wait()
                self.add_log_info(
                    f"Направлен запрос: "
                    f"\n\t- метод: {self.url_params.method.value}"
                    f"\n\t- url: {self.full_url}"
                    f"\n\t- заголовки: {self.headers}"
                    f"\n\t- параметры: {self.params}"
                )
                self.write_logs_to_yml()
                # TODO Выделить логику запроса в отдельный метод
                prepared_session = self.set_http_method()
                async with prepared_session(**self.params_for_request) as response:
                    ic(response)
                    parsed_response = await self.get_parsed_response(response)
                    attempts_result.response_code = response.status
                    if response.status in HTTP_RESPONSE_CODES_ACCESS_DENIED:
                        await self.add_auth_header_to_access_denied_list()
                        return attempts_result_with_error({"Получен ответ": parsed_response})

                    if response.status in HTTP_RESPONSE_CODES_STOP_REQURESTS:
                        return attempts_result_with_error({"Получен ответ": parsed_response})

                    if response.status != self.url_params.positive_response_code:
                        attempts_result.fetch_errors.append(parsed_response)

                        self.add_log_info(f"Ошибка: {parsed_response}\n" f"Проверяю возможность повторного запроса")

                        can_repeat_request = await self.checking_can_repeat_request(response.status)
                        if can_repeat_request:
                            self.add_log_info("Выполняется повторный запрос")
                            continue
                        else:
                            self.add_log_info("Повторный запрос не предусмотрен для данной ошибки")
                            return attempts_result

                    if response.status == self.url_params.positive_response_code:
                        response_data = self.validate_response(parsed_response)
                        if response_data.response_schema_error:
                            return attempts_result_with_error(
                                {"Ответ не соответствует ожидаемой схеме": "не задана response_schema"}
                            )

                        attempts_result.fetch_result = response_data.valid_data
                        return attempts_result

            except json.JSONDecodeError as decode_err:  # Ошибка при парсинге ответа в json
                return attempts_result_with_error({"Ошибка парсинга JSON": decode_err.msg})
            except ValidationError as validation_err:  # Ошибки при валидации структуры ответа моделями pydantic
                return attempts_result_with_error({"Ответ не соответствует ожидаемой схеме": validation_err.errors()})
            except ClientError as client_err:  # Ошибки клиента aiohttp при получении ответа по сети
                attempts_result_with_error({"Ошибка сетевого обмена": client_err})
            except Exception as error:
                return attempts_result_with_error(
                    {"Ошибка обработки запроса": error, "tracback": traceback.format_exc()}
                )

            self.add_log_error(f"Ошибка.Повторный запрос через {self.url_params.timeout} с")
            await asyncio.sleep(self.url_params.timeout)

        error = {"Данные не получены": "Превышено количество допустимых попыток запроса"}
        attempts_result.fetch_errors.append(error)
        self.add_log_info(error)

        return attempts_result

    def set_http_method(self) -> Callable:
        return dict_fetch_method(self.session).get(self.url_params.method, self.session.get)

    async def make_marketplace_api_request(self) -> FetchResponse:
        self.add_headers()
        async with self.semaphore:
            fetch_response = await self.attempt_fetch()
            return fetch_response

    async def checking_can_request(self):
        set_auth_headers_access_denied = await get_auth_header_access_denied_set()
        return self.headers.get(self.auth_header) not in set_auth_headers_access_denied

    @staticmethod
    async def checking_can_repeat_request(response_code) -> bool:
        return response_code in HTTP_RESPONSE_CODES_FOR_REPEAT_REQUEST

    @property
    def full_url(self):
        return (
            f"{self.url_params.url_api_point}{self.url_params.url}"
            if self.url_params.url_api_point
            else full_url(self.url_params.url)
        )

    @staticmethod
    async def get_parsed_response(response: ClientResponse) -> dict:
        response_content_type = response.headers.get("Content-Type")
        if "application/json" in response_content_type:
            parsed_response = await response.json()
            return parsed_response
        else:
            parsed_response = await response.text()
            return json.loads(parsed_response)

    def validate_response(self, response_data: dict) -> ValidationResult:
        data = ValidationResult()
        if not response_data:  # Если пришел пустой ответ, то валидировать нечего
            return data
        response_schema = self.valid_type_positive if self.valid_type_positive else self.url_params.response_schema
        if not response_schema:  # Если нигде не задана pydantic-схема парсинга ответа
            data.response_schema_error = True
            return data
        data.valid_data = (
            response_schema(response_data)
            if issubclass(response_schema, ListBaseModel) or isinstance(response_data, list)
            else response_schema(**response_data)
        )

        """
            Закомментированы проверки на нетипичные ответы,которые возможно когда-то
            приходили и были добавлены. Тк дальнейшая логика работы строится на работе
            с экземпляром pydantic модели, то вернуть просто список или словарь не поможет, тк
            будет AttributeError. При следующем получение подобного нетипичного ответа
            необходимо завести под него дополнительную pydantic модель и дополнительно
            парсить эти нетипичные поля через модель. Можно поменять логику самих реквестеров,
            но это будет протечка абстракции. Вся логика парсинга и валидации ответа api
            предполагает инкапсуляцию в одном месте- в классе Fetcher.
        """
        # if self.valid_type_positive.__name__ == "str":
        #     return valid_response
        # if hasattr(response_data, "data") and isinstance(valid_response.data, list):
        #     return valid_response.data
        # elif hasattr(response_data, "root"):
        #     return valid_response.root

        return data

    def get_yml_logs(self) -> dict:
        try:
            with open(self.file_log_requests) as f_yaml:
                result = yaml.safe_load(f_yaml)
        except (Exception,):
            result = {}
        return result or {}

    @property
    def hash_auth(self):
        r = self.headers.get(self.auth_header, "") or ""
        r = hashlib.sha256(str.encode(r)).hexdigest()
        return r

    async def checking_need_to_wait(self) -> bool:
        now = datetime.now()
        self.requests_logs = self.get_yml_logs()
        last_datetime_request = (
            self.requests_logs.get(self.hash_auth, {}).get(self.url_params.url, {}).get("request_at")
        )
        if not last_datetime_request or not self.url_params.timeout:
            return False
        result = (now - last_datetime_request).seconds <= self.url_params.timeout
        self.add_log_info(f"Время последнего запроса:{last_datetime_request}")
        self.add_log_info(
            f"Время между запросами:{(now - last_datetime_request).seconds}\n"
            f"Время ожидания между запросами: {self.url_params.timeout}"
        )
        if result:
            self.add_log_info(f"Нужно подождать {self.url_params.timeout}с")
            await asyncio.sleep(self.url_params.timeout)
        return result

    def get_num_attempt_request(self):
        return self.requests_logs.get(self.hash_auth, {}).get(self.url_params.url, {}).get("num_attempt_request", 1)

    @property
    def params_for_request(self):
        # старое решение
        # key_params = "json" if self.url_params.method == RequestMethod.POST else "params"
        # NOTE: Добавлен метод RequestMethod.PUT, тк в экспорте цен ожидается json в методе PUT
        key_params = "json" if self.url_params.method in {RequestMethod.POST, RequestMethod.PUT} else "params"
        return {"url": self.full_url, key_params: self.params, "headers": self.headers}

    def write_logs_to_yml(self):
        new_data = {
            self.hash_auth: {
                self.url_params.url: {
                    "request_at": datetime.now(),
                    "num_attempt_request": self.num_attempt_request + 1,
                }
            }
        }
        self.requests_logs |= new_data
        with open(self.file_log_requests, "w") as f_yaml:
            yaml.dump(self.requests_logs, f_yaml)
