import asyncio
import logging
import traceback
from abc import ABC
from asyncio import Semaphore, Task
from dataclasses import dataclass, field
from typing import Collection, Any, Callable, Optional, TypeVar, Type

from aiohttp import ClientSession
from aiohttp.web_app import Application
from pydantic import BaseModel

from core.project.exceptions import RequestException
from core.project.services.requesters.fetcher import Fetcher, FetchResponse
from core.project.types import MsgSendStartEventInMSMarketplace, URLParameterSchema
from core.project.utils import (
    count_iterations_from_total,
    start_stop_index_in_iteration,
    # execute_async_rest_tasks,
)
from icecream import ic


logger_error = logging.getLogger("errors")
logger_info = logging.getLogger("info")

T = TypeVar("T", bound=BaseModel)


class AbstractRequester(ABC):
    def clean_input_data(self):
        raise NotImplementedError()

    async def execute(self):
        raise NotImplementedError()

    async def fetch(self, *args, **kwargs):
        raise NotImplementedError()

    async def single_fetch(self, url_params: URLParameterSchema, **kwargs):
        raise NotImplementedError()


@dataclass
class AppRequester(AbstractRequester):
    app: Application
    session: ClientSession
    semaphore: Semaphore
    request_body: MsgSendStartEventInMSMarketplace
    url_schema: Optional[URLParameterSchema] = field(default=None)
    errors: list[dict] = field(default_factory=list)
    additional_info: Optional[Any] = field(default=None)
    test: bool = field(default=False)

    def _prepare_url(self, url_params: URLParameterSchema, query_params: Type[T]) -> URLParameterSchema:
        # Применяем интерполяцию строк и формируем окончательнуый url. Метод нужен для генерации динамического URL.
        url_params.url = url_params.url % query_params.model_dump()
        return url_params

    def _get_query_params_from_request_body(self, pydantic_schema: Type[T]):
        return pydantic_schema(**self.request_body.data)

    async def execute_and_process_api_tasks(self, api_request_tasks: Collection[Task]) -> list[Any]:
        process_result = []
        api_done_tasks, _ = await asyncio.wait(api_request_tasks)
        for task in api_done_tasks:
            """
                Функция asyncio.wait перехватывает и записывает все исключения.
                В Fetcher организован перехват ожидаемых исключений согласно логики и
                запись ошибок этих исключений.
                Данная проверка позволит проверить не учтенные логикой Fetcher исключения,
                которые могут появиться при рефакторинге или расширении кода Fetcher.
            """
            if task.exception() is None:
                task_result: FetchResponse = task.result()
                if task_result.fetch_result:
                    process_result.append(task_result.fetch_result)
                self.errors.extend(task_result.fetch_errors)
            else:
                exception = task.exception()
                tb_str = traceback.format_exception(exception, value=exception, tb=exception.__traceback__)
                error = {"Ошибка выполнения Fetcher": {"Тип ошибки": exception, "Traceback": tb_str}}
                ic(error)
                self.errors.append(error)
                logger_error.error(error)
        return process_result

    def _prepare_task_for_single_request(
        self,
        url_schema: Optional[URLParameterSchema] = None,
        params: Optional[dict] = None,
    ) -> Task:
        params = {
            "headers": self.request_body.headers,
            "session": self.session,
            "semaphore": self.semaphore,
            "url_params": url_schema or self.url_schema,
            "params": params,
            "test": self.test,
        }
        return asyncio.create_task(Fetcher()(**params))

    def prepare_tasks_for_bulk_requests(
        self, urls_and_params: Collection[tuple[URLParameterSchema | None, dict]]
    ) -> Collection[Task]:
        urls_and_params = urls_and_params
        result = []
        for url_schema, params in urls_and_params:
            result.append(self._prepare_task_for_single_request(url_schema=url_schema, params=params))
        return result

    async def make_single_api_request(
        self,
        urls_and_params: tuple[URLParameterSchema | None, dict | None] | None = None,
    ) -> Any:
        result = await self.make_bulk_api_requests(urls_and_params=[urls_and_params])
        return result[0] if result else None

    async def make_bulk_api_requests(
        self,
        urls_and_params: Collection[tuple[URLParameterSchema | None, dict | None]] | None = None,
    ) -> list[Any]:
        result = []

        if not urls_and_params:
            return result

        api_request_tasks = self.prepare_tasks_for_bulk_requests(urls_and_params)
        if api_request_tasks:
            api_tasks_result = await self.execute_and_process_api_tasks(api_request_tasks=api_request_tasks)
            result.extend(api_tasks_result)
        return result

    async def fetch(
        self,
        urls_and_params: Collection[tuple[URLParameterSchema | None, dict | None]] | None = None,
    ) -> list[Any]:
        if len(urls_and_params) == 1:
            fetch_result = await self.make_single_api_request(urls_and_params=urls_and_params[0])
        else:
            fetch_result = await self.make_bulk_api_requests(urls_and_params=urls_and_params)

        return fetch_result

    def _prepare_tasks_for_cycle_request(
        self,
        items: Collection[Any],
        count_items_one_iteration: int,
        func_prepare_params: Callable,
        url_schema: URLParameterSchema = None,
        **additional_params,
    ) -> Collection[Task]:
        tasks = []

        count_iterations = count_iterations_from_total(len(items), count_items_one_iteration)
        for iteration in range(count_iterations):
            start_index, stop_index = start_stop_index_in_iteration(iteration, count_items_one_iteration)
            json_params = func_prepare_params(items, start_index, stop_index, self.errors, **additional_params)
            if json_params:
                url_schema = self.url_schema or url_schema
                if not isinstance(url_schema, URLParameterSchema):
                    continue
                tasks.append(
                    asyncio.create_task(
                        Fetcher()(
                            session=self.session,
                            semaphore=self.semaphore,
                            url_params=url_schema,
                            headers=self.request_body.headers,
                            params=json_params,
                            test=self.test,
                        ),
                        name=url_schema.title,
                    )
                )
        return tasks

    async def single_fetch(self, url_params: URLParameterSchema, **kwargs) -> Type[BaseModel] | None:
        response = await Fetcher()(
            session=self.session,
            semaphore=self.semaphore,
            url_params=url_params,
            params=kwargs.get("params"),
            headers=self.request_body.headers,
            valid_type_positive=kwargs.get("valid_type_positive") or url_params.response_schema,
            valid_type_negative=kwargs.get("valid_type_negative") or url_params.error_schema,
            test=self.test,
        )

        if response.fetch_errors:
            self.errors.extend(response.fetch_errors)
            # TODO: можно придумать что-то получше. Например записать ошибку и отдать пустой ответ.
            # Тогда можно не перехватывать исключение на уровне выше
            raise RequestException(
                msg=f"На запрос {url_params.url} пришёл негативный ответ.",
                status=response.response_code,
                response=response.fetch_errors,
            )

        return response.fetch_result


class SingleRequester(AppRequester):
    async def _execute_request(self, input_data: BaseModel):
        try:
            result = await self.single_fetch(self.url_schema, params=input_data.model_dump())

        except RequestException:
            return self.url_schema.response_schema(data=None).model_dump()
        return result

    def clean_input_data(self):
        return self.url_schema.body_schema.model_validate(self.request_body.data)

    async def execute(self):
        input_data = self.clean_input_data()
        return await self._execute_request(input_data)
