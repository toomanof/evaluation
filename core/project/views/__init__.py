import logging
import traceback
from itertools import zip_longest
from json import JSONDecodeError
from typing import Type

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from icecream import ic

from core.project.services.database_workers import DBHandler
from core.project.types import ParamsView, ResponseView


logger_error = logging.getLogger("errors")
logger_info = logging.getLogger("info")


class MSView(web.View):
    def __init__(self, request: Request) -> None:
        self.params = ParamsView()
        self.errors = []
        super().__init__(request)

    async def get_params_from_json(self):
        try:
            params = await self.request.json()
        except JSONDecodeError:
            params = {}
        return params

    def get_params_from_url(self):
        result = {}
        for key, val in self.request.rel_url.query.items():
            if key in result:
                if not isinstance(result[key], list):
                    result[key] = [result[key]]
                result[key].append(val)
            else:
                result[key] = val
        result |= self.request.match_info
        return result

    def prepare_sorting_params(self, params: dict):
        """
        Подготавливает параметры сортировки запроса
        """
        sorting_fields = params.pop("sort", None)
        sorting_directions = params.pop("asc", None)
        if not sorting_fields:
            self.params.sorting_fields = []
            return
        if not sorting_directions:
            sorting_directions = "ASC"

        if not isinstance(sorting_fields, list):
            sorting_fields = [sorting_fields]
        if sorting_directions and not isinstance(sorting_directions, list):
            sorting_directions = [sorting_directions]
        sorting_directions = sorting_directions[: len(sorting_fields)]
        sorting_fields = list(zip_longest(sorting_fields, sorting_directions, fillvalue="true"))
        for ind, sorting_field in enumerate(sorting_fields):
            sorting_direction = sorting_field[1]
            sorting_direction = "DESC" if sorting_direction.lower() == "false" else "ASC"
            sorting_fields[ind] = f"{sorting_field[0]} {sorting_direction}"
        self.params.sorting_fields = sorting_fields

    async def clean_params(self):
        """
        Производит очистку входящих параметров
        """
        filter_dict = {}
        params = await self.get_params_from_json()
        params |= self.get_params_from_url()
        self.prepare_sorting_params(params)
        for key, val in params.items():
            try:
                setattr(self.params, key, int(val) if val else 0)
            except Exception:
                if key in self.params.model_fields:
                    setattr(self.params, key, val)
                else:
                    filter_dict[key] = val

        self.params.filter = filter_dict

    async def __get_result__(self) -> ResponseView:
        pass

    def __response__(self, result: ResponseView):
        """
        Возвращает подготовленный ответ в формате json
        Args:
            result: ResponseView - подготовленный ответ

        Returns:
            aiohttp.web_response.Response
        """
        data = result.model_dump() if isinstance(result, ResponseView) else None
        return web.json_response(data=data, status=500 if self.errors else 200)

    async def __prepare_response__(self) -> Response:
        result = None
        try:
            await self.clean_params()
            result = await self.__get_result__()
        except Exception as err:
            ic(f"{err}\n{traceback.format_exc()}")
            logger_error.error(err, exc_info=True, stack_info=True)
            result = ResponseView(
                errors=self.errors,
                result=None,
                total_count=0,
            )

        return self.__response__(result)

    async def get(self):
        return await self.__prepare_response__()

    async def post(self) -> Response:
        return await self.__prepare_response__()


class DBHandlerView(MSView):
    db_handler: Type[DBHandler]

    async def __get_result__(self) -> ResponseView:
        from core.project.conf import settings

        db_handler = self.db_handler(
            pool=self.request.app[settings.DEFAULT_DATABASE],
            params=self.params,
            errors=self.errors,
        )
        result = await db_handler.for_platform()
        total_count = await db_handler.total_count()
        errors = db_handler.errors or None
        return ResponseView(
            errors=errors,
            result=result,
            total_count=total_count,
        )
