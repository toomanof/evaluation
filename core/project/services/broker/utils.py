from typing import TypeVar
from pydantic import BaseModel
from aio_pika import Message


T = TypeVar("T", bound=BaseModel)


def convert_pydantic_message_to_aio_pika(
    pydantic_obj: T,
    **kwargs,
) -> Message:
    """

    headers: Optional[HeadersType] = None,
    content_type: Optional[str] = None,
    content_encoding: Optional[str] = None,
    delivery_mode: Union[DeliveryMode, int, None] = None,
    priority: Optional[int] = None,
    correlation_id: Optional[str] = None,
    reply_to: Optional[str] = None,
    expiration: Optional[DateType] = None,
    message_id: Optional[str] = None,
    timestamp: Optional[DateType] = None,
    type: Optional[str] = None,
    user_id: Optional[str] = None,
    app_id: Optional[str] = None,"""
    return Message(body=str.encode(pydantic_obj.model_dump_json(indent=2)), delivery_mode=2, **kwargs)
