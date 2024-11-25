from typing import Optional, Any, Union

from pydantic import Field, BaseModel

from core.project.constants import SECONDS_IN_MINUTE
from core.project.enums.common import RequestMethod


class URLParameterSchema(BaseModel):
    """
    Параметры для ulr запроса.

    url - шаблон ulr адреса
    has_cache - флаг записи данных в кеш
    additional-headers - дополнительные заголовки запроса
    response_schema - схема получаемых данных
    cache_expires_in - время жизни в кеша (секунды)
    max_count_bad_request - максимальное ко-во ошибочных запросов
    """

    title: Optional[str] = None
    name: Optional[str] = None
    url: str
    url_api_point: Optional[str] = None
    url_sandbox: Optional[str] = None
    additional_headers: Optional[Union[type[BaseModel], type[BaseModel]]] = None
    has_cache: bool = False
    body_schema: Optional[type[BaseModel]] = None
    query_schema: Optional[type[BaseModel]] = (
        None  # NOTE: introduced to separate query parameters from body parameters
    )
    response_schema: Optional[type[BaseModel]] = Field(default=None)
    error_schema: Optional[type[BaseModel]] = Field(default=None)
    method: RequestMethod = Field(default=RequestMethod.GET)
    cache_expires_in: int = Field(default=SECONDS_IN_MINUTE * 30)
    max_count_bad_request: int = Field(default=5)
    max_count_bad_response: int = Field(default=5)
    positive_response_code: int = Field(default=200)
    version: int = Field(default=1)
    timeout: Optional[float] = Field(default=0)


class MsgResponseToPlatform(BaseModel):
    marketplace_id: Optional[int] = Field(description="ID маркетплейса запрашивающего задачу", default=None)
    company_id: Optional[int] = Field(description="ID компании запрашивающего задачу", default=None)
    customer_id: Optional[int] = Field(description="ID пользователя запрашивающего задачу", default=None)
    data: Optional[Any] = Field(description="Возвращаемые данные", default=None)
    errors: Optional[list[dict] | dict | Any] = Field(description="Ошибки при выполнении задачи", default=None)
    event_id: Optional[str] = Field(description="ID события", default=None)
    traceback: Optional[str] = Field(default=None)
    task_id: Optional[int] = Field(description="ID задачи", default=None)
    event: Optional[str] = Field(description="Вызываемое событие", default=None)
    callback: Optional[str] = Field(description="метод вызываемый в платформе по завершению события", default=None)
    token: Optional[str] = Field(description="Токен текущего пользователя", default=None)
    sender: str = Field(description="М-с отправитель", default="wb")
    add_info: Optional[dict] = Field(description="Дополнительные данные", default=None)


class MsgSendStartEventInMSMarketplace(BaseModel):
    callback: Optional[str] = Field(description="метод вызываемый в платформе по завершению события", default=None)
    company_id: Optional[int] = Field(description="ID компании", default=None)
    customer_id: Optional[int] = Field(description="ID пользователя запрашивающего задачу", default=None)
    data: Optional[Any] = Field(description="Тело событие", default=None)
    event: str = Field(description="Вызываемое событие")
    event_id: str = Field(description="ID события")
    headers: dict = Field(description="Заголовки REST запроса")
    marketplace_id: Optional[int] = Field(description="ID вызывающего маркета", default=None)
    task_id: Optional[int] = Field(description="ID задачи", default=None)
    channel_centrifugo: Optional[str] = Field(
        description="Канал передачи сообщения на фронт через Центрифугу",
        default_factory=str,
    )
    url_schema: Optional[URLParameterSchema] = Field(description="Параметры REST запроса", default=None)
    queue: Optional[str] = Field(description="RabbitMQ очередь", default=None)
    token: Optional[str] = Field(description="Токен текущего пользователя", default=None)
    add_info: Optional[dict] = Field(description="Дополнительные данные", default=None)
    cached: Optional[bool] = Field(title="Признак кеширования целевого запроса", default=True)


class ParamsView(BaseModel):
    company_id: Optional[int] = None
    marketplace_id: Optional[int] = None
    after: Optional[str] = None
    first: Optional[int] = None
    before: Optional[str] = None
    last: Optional[int] = None
    sorting_directions: Optional[str] = Field(default_factory=list)
    sorting_fields: Optional[list[str]] = Field(default_factory=list)
    filter: Optional[dict] = None


class ResponseView(BaseModel):
    total_count: Optional[int] = None
    result: Optional[Any] = None
    errors: Optional[list[Any]] = Field(default_factory=list)
