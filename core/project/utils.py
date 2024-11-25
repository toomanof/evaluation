import asyncio
import copy
import datetime
import json
import logging

from asyncio import Task
from contextlib import contextmanager
from decimal import Decimal
from functools import wraps
from hashlib import md5
from pprint import pformat
from time import localtime

from aiocache import caches
from aiohttp import ClientSession, ClientConnectorError, ClientResponse
from aiohttp.web_app import Application
from asyncpg.connection import Connection
from asyncpg import utils
from base64 import b64encode as _base64, b64decode as _unbase64
from datetime import datetime as datetime_class
from importlib import import_module
from typing import Any, Type, Generator, Collection, Tuple, List

from icecream import ic
from pydantic import BaseModel, ValidationError
from six import text_type

from core.apps.basic.types import WBResponse
from core.apps.basic.types.from_platform import ResponseCompanyWithHeader, MarketplaceWithHeader
from core.project.constants import J2000
from core.project.enums.common import RequestMethod
from core.project.types import MsgResponseToPlatform, MsgSendStartEventInMSMarketplace, URLParameterSchema

logger_error = logging.getLogger("errors")
logger_info = logging.getLogger("info")


class PGAsyncUtilities:
    asyncpg_utilities = vars(utils)
    mogrify = asyncpg_utilities.get("_mogrify")


async def asyncpg_mogrify(connection: Connection, query: str, arguments: List) -> str:
    return await PGAsyncUtilities.mogrify(conn=connection, query=query, args=arguments)


def call_event(app: Application, body: MsgSendStartEventInMSMarketplace):
    from core.project.conf import settings

    event = body.event
    class_handler = import_string(settings.CONSUMER_HANDLER)
    assert hasattr(class_handler, event), f"The {settings.CONSUMER_HANDLER} is missing a method {event}"
    instance_handler = class_handler(app=app, body=body)
    return getattr(instance_handler, event)


def count_iterations_from_total(total_count: int, count_items_one_iteration: int) -> int:
    """
    Возвращает количество итераций из общего количество итерируемого объекта.
    Args:
        total_count - общее количество итерируемого объекта;
        count_items_one_iteration - количество объектов в одной итерации
    """
    if not total_count:
        return 0
    if total_count < count_items_one_iteration:
        total_count = count_items_one_iteration

    count_iter = total_count // count_items_one_iteration
    remainder = total_count % count_items_one_iteration
    count_iter += 1 if remainder > 0 else 0
    return count_iter


def datetime2int_timestamp(val: datetime_class) -> int:
    return int(datetime_class.timestamp(val))


async def execute_async_rest_tasks(
    tasks: Collection[Task],
    valid_type_positive: Type[BaseModel] | Type[str],
    valid_type_error: Type[BaseModel] | Type[str],
    errors: list[dict],
) -> list[Any]:
    result = []
    if not tasks:
        return list()
    try:
        done_tasks, _ = await asyncio.wait(tasks)
    except Exception as err:
        ic(err)
        if hasattr(err, "message"):
            errors.append(WBResponse(error=True, errorText=getattr(err, "message")).model_dump())

        logger_error.error(err, exc_info=True, stack_info=True)
        raise err

    for task in done_tasks:
        item = task.result()
        match item.response_code:
            case 400:
                errors.append(
                    WBResponse(
                        error=True,
                        errorText=f"Задача: {task.get_name()}. Не верная форма запроса: {item}",
                        additionalErrors=item,
                    ).model_dump()
                )
            case 200:
                if valid_type_positive.__name__ == "str":
                    result.append(item)
                    break

                response = valid_type_positive.model_validate(item.fetch_result)
                if hasattr(response, "error") and response.error:
                    errors.append(response.model_dump())

                if hasattr(response, "data") and isinstance(response.data, list):
                    result.extend(response.data)
                elif hasattr(response, "root"):
                    result.extend(response.root)
                else:
                    result.append(response)
            case _:
                # errors.append(
                #     WBResponse(
                #         error=True,
                #         errorText=str(item),
                #         additionalErrors=item,
                #     ).model_dump()
                # )
                for error in item.fetch_errors:
                    errors.append(
                        WBResponse(
                            error=True,
                            errorText=str(error),
                            additionalErrors=error,
                        ).model_dump()
                    )

    return result


def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit(".", 1)
    except ValueError as err:
        logger_error.error(err, exc_info=True, stack_info=True)
        raise ImportError("%s doesn't look like a module path" % dotted_path) from err

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError as err:
        raise ImportError('Module "%s" does not define a "%s" attribute/class' % (module_path, class_name)) from err


def prepare_response(body_request: MsgSendStartEventInMSMarketplace, response: MsgResponseToPlatform):
    from core.project.conf import settings

    if not settings.DEBUG:
        response.traceback = None
    response.callback = body_request.callback
    response.event = body_request.event
    response.marketplace_id = body_request.marketplace_id
    response.company_id = body_request.company_id
    response.customer_id = body_request.customer_id
    response.task_id = body_request.task_id
    response.token = body_request.token
    response.event_id = body_request.event_id
    response.add_info = body_request.add_info
    return serialize(response.model_dump())


def start_stop_index_in_iteration(iteration: int, count_items_in_iteration: int) -> tuple[int, int]:
    start_index = iteration * count_items_in_iteration
    stop_index = (iteration + 1) * count_items_in_iteration
    return start_index, stop_index


async def send_response_to_platform(
    request_body: MsgSendStartEventInMSMarketplace, response_body: MsgResponseToPlatform
):
    async with ClientSession() as session:
        try:
            response = await session.post(
                get_url_callback_platform(request_body),
                json=prepare_response(request_body, response_body),
            )
        except ClientConnectorError as err:
            logger_error.error(err, exc_info=True, stack_info=True)
            logger_error.info(
                "Необходимо продумать механизм повторного отправления сообщений при не удачной отправке!"
            )
        else:
            if response.status == 200:
                logger_info.info("Response delivered.")
            else:
                logger_info.info("The platform responded with an error!")

        await asyncio.sleep(0.1)


async def get_access_token_from_platform(email: str, password: str):
    from core.project.conf import settings

    url = settings.PLATFORM.get("url_auth", "")
    params = {"email": email, "password": password}
    async with ClientSession() as session:
        try:
            response = await session.post(url, json=params)
        except ClientConnectorError:
            logger_error.error(f"Нет подключения к платформе.\n{email}")
            return
        if response.status != 200:
            logger_error.error(f"Платформа ответила отрицательным ответом.\n{email}\n{response}")
            return
        result_response = await response.json()
    return result_response.get("access")


async def fetch_collection_from_platform(
    url: str, headers: dict, response_type: Type[BaseModel], params: dict = None
) -> Collection:
    result = []
    while url:
        async with ClientSession() as session:
            response = await session.get(url, headers=headers, params=params)
            if response.status != 200:
                break
            result_response = await response.json()
            try:
                valid_response = response_type.model_validate(result_response)
            except ValidationError as err:
                ic(err)
                break

            url = valid_response.next
            result.extend(valid_response.results)
    return result


async def post_collection_from_ms(
    url: str, headers: dict, response_type: Type[BaseModel], params: dict = None, body: dict = None
) -> Collection:
    result = []
    async with ClientSession() as session:
        response = await session.post(url, headers=headers, json=body)
        if response.status != 201:
            return result
        result_response = await response.json()
        try:
            for item in result_response:
                result.append(response_type(**item))

        except ValidationError as err:
            ic(err)

    return result


async def fetch_companies_with_header() -> Collection[MarketplaceWithHeader]:
    from core.project.conf import settings

    headers = {"Content-Type": "application/json"}
    url = settings.PLATFORM.get("url_marketplaces")
    return await fetch_collection_from_platform(
        url=url, headers=headers, response_type=ResponseCompanyWithHeader, params={"marketplace": "WILDBERRIES"}
    )


def base64(s: object) -> object:
    return _base64(s.encode("utf-8")).decode("utf-8")


def unbase64(s):
    return _unbase64(s).decode("utf-8")


def valid_response_from_tasks(
    done_tasks: set[Task], valid_type: Type[BaseModel]
) -> Generator[tuple[Any, BaseModel], Any, None]:
    """
    Производит проверку результатов задач на соответствие переданного типа
    Args:
        done_tasks: список выполненных задач
        valid_type: проверочный тип

    Returns:
        генератор кортежей статуса запроса и результата запроса переведенного в проверочный тип
    """
    tasks_results = [task.result() for task in done_tasks]
    return ((item[0], valid_type.model_validate(item[1])) for item in tasks_results)


def get_url_callback_platform(body_request: MsgSendStartEventInMSMarketplace):
    from core.project.conf import settings

    marketplace_id = base64(":".join(["Marketplace", text_type(body_request.marketplace_id)]))
    return f"{settings.PLATFORM.get('url_webhook', '').removesuffix('/')}/{marketplace_id}/{body_request.callback}/"


def full_url(url: str) -> str:
    from core.project.conf import settings

    return f"{settings.API_BASE_URL}{url}"


def collection_of_dates_for_year():
    yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
    return set((yesterday - datetime.timedelta(days=x)).date() for x in range(31))


async def response_processing(
    errors: list[dict],
    response: ClientResponse,
    valid_type_positive: Type[BaseModel] | Type[str],
):
    response_content_type = response.headers.get("Content-Type")
    if "text/plain" in response_content_type:
        response_body = await response.text()
    elif "application/json" in response_content_type:
        response_body = await response.json()
    else:
        response_body = response.text()

    match response.status:
        case 400:
            errors.append(
                WBResponse(
                    error=True,
                    errorText=f"{response_body}",
                    additionalErrors=response_body,
                ).model_dump()
            )
        case 200:
            if valid_type_positive.__name__ == "str":
                response = response_body
            else:
                response_body = valid_type_positive.model_validate(response_body)
                if hasattr(response_body, "error") and response_body.error:
                    errors.append(response_body.model_dump())

        case _:
            errors.append(
                WBResponse(
                    error=True,
                    errorText=str(response_body),
                    additionalErrors=response_body,
                ).model_dump()
            )
    return response.status, response_body


def serialize_record(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()


def serialize(collection):
    collection = json.dumps(
        collection,
        indent=4,
        sort_keys=True,
        ensure_ascii=False,
        default=serialize_record,
    )
    return json.loads(collection)


def deserialize(obj):
    return json.loads(obj) if isinstance(obj, (str, bytes, bytearray)) else obj


def time_of_completion(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        print(f"Старт теста {func.__name__}")
        start = datetime_class.now()
        await func(*args, **kwargs)
        end = datetime_class.now()
        print(f"Тест {func.__name__} прошёл за {end - start} с")

    return wrapper


def dict_fetch_method(session: ClientSession) -> dict:
    return {
        RequestMethod.POST: session.post,
        RequestMethod.GET: session.get,
        RequestMethod.PUT: session.put,
        RequestMethod.PATCH: session.patch,
    }


def url_with_params(url_schema: URLParameterSchema, *args) -> URLParameterSchema:
    result = copy.deepcopy(url_schema)
    result.url = url_schema.url % args
    return result


def replace_multiline_single_quotes(x: str, single_quote_substitution: str = "$$"):
    """
    Объединение многострочного запроса БД без разбиения в одной строке с заменой одинарных кавычек на двойной знак $

    @param x: многострочный запрос БД
    @param single_quote_substitution: строковое значение для замены одинарных кавычек
    @return: однострочный запрос БД с замененными одинарными кавычками
    """
    dollar_quoted = x.replace(*("'", single_quote_substitution))
    return pformat(
        object=" ".join([y.strip().replace(*("'", single_quote_substitution)) for y in dollar_quoted.splitlines()]),
        width=len(repr(dollar_quoted)),
    )


@contextmanager
def replace_multiline_single_quotes_context():
    """
    Контекст печати многострочного запроса БД без разбиения в одной строке с заменой одинарных кавычек на двойной знак $
    """
    clone = copy.copy(x=ic)
    ic.configureOutput(
        argToStringFunction=replace_multiline_single_quotes,
    )
    try:
        yield
    finally:
        ic.configureOutput(
            argToStringFunction=clone.argToStringFunction,  # NOTE: restore icecream configuration
        )


def timestamp_with_timezone_decoder(value: Tuple) -> str:
    return (J2000 + datetime.timedelta(microseconds=value[0])).isoformat()


async def set_connection_numeric_type_codec(connection: Connection) -> None:
    await connection.set_type_codec(
        typename="numeric",
        encoder=str,
        decoder=float,
        schema="pg_catalog",
        format="text",
    )


async def set_connection_json_type_codec(connection: Connection) -> None:
    await connection.set_type_codec(
        typename="json",
        encoder=json.dumps,
        decoder=json.loads,
        schema="pg_catalog",
        format="text",
    )


async def set_connection_jsonb_type_codec(connection: Connection) -> None:
    await connection.set_type_codec(
        typename="jsonb",
        encoder=json.dumps,
        decoder=json.loads,
        schema="pg_catalog",
        format="text",
    )


async def set_connection_timestamp_with_timezone_type_codec(connection: Connection) -> None:
    await connection.set_type_codec(
        typename="timestamp with timezone",
        encoder=lambda x: x,
        decoder=timestamp_with_timezone_decoder,
        schema="pg_catalog",
        format="tuple",
    )


async def set_connection_date_type_codec(connection: Connection) -> None:
    await connection.set_type_codec(
        typename="date",
        encoder=lambda x: x,
        decoder=lambda x: x,
        schema="pg_catalog",
        format="text",
    )


async def set_connection_types_codecs(connection: Connection) -> None:
    await set_connection_numeric_type_codec(connection=connection)
    await set_connection_json_type_codec(connection=connection)
    await set_connection_jsonb_type_codec(connection=connection)
    await set_connection_timestamp_with_timezone_type_codec(connection=connection)
    await set_connection_date_type_codec(connection=connection)


async def client_session(app: Application):
    """
    Создание глобальной ClientSession
    """
    print("Создается ClientSession")
    session = ClientSession()
    app["session"] = session
    yield
    print("Закрывается ClientSession")
    await session.close()


def get_cache_handler_or_none():
    from core.project.conf import settings

    if settings.CACHE:
        return caches.get("redis_alt")
    return


def set_cache_config():
    from core.project.conf import settings

    caches.set_config(settings.CACHE_CONFIG)


# NOTE: из app кэш нигде не извлекается и возможно стоит пересмотреть механизм инициализации
async def client_cache(app: Application):
    set_cache_config()
    cache_handler = get_cache_handler_or_none()
    if cache_handler:
        print("Подключается кэш")
        app["cache"] = get_cache_handler_or_none()
    else:
        print("Не удалось подключить кэш")


async def get_auth_header_access_denied_set() -> set[str]:
    return set()

    cache = get_cache_handler_or_none()
    if not cache:
        return set()
    access_denied_headers = await cache.get("access_denied_headers") or []
    if not isinstance(access_denied_headers, list):
        access_denied_headers = []
    return set(access_denied_headers)


def get_random_text() -> str:
    return md5(str(localtime()).encode("utf-8")).hexdigest()
