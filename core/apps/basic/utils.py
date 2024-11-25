import logging
from typing import Any, Collection, TypeVar

from pydantic import BaseModel

from core.apps.basic.types import WBPhoto
from core.project.services.broker import main_broker
from core.project.services.broker.utils import convert_pydantic_message_to_aio_pika


logger = logging.getLogger(__name__)


T = TypeVar("T", bound=BaseModel)


def get_vendor_codes(
    products: Collection[BaseModel],
) -> tuple[Any, ...]:
    """
    Returns:
        Генератор артикулов продавца из списка товаров
    """
    s = {x.vendorCode for x in products}
    return tuple(i for i in s)


def wb_photos_to_list_str(photos: list):
    result = []
    if not photos:
        return []
    for photo in photos:
        if isinstance(photo, WBPhoto):
            result.append(photo.biggest)
        elif isinstance(photo, str):
            result.append(photo)
    return result


async def send_message_to_stocks_microservice(message: T):
    """Метод для отправки сообщения в очередь сервиса по остаткам.

    Args
        message -- любой pydantic BaseModel объект

    """
    try:
        aio_pika_message = convert_pydantic_message_to_aio_pika(message)
        await main_broker.publish("stock_publisher", aio_pika_message)
        # await stocks_rabbit_broker.publish(aio_pika_message)
        logger.debug(f"SENT MESSAGE: {aio_pika_message}")
        print(f"SENT MESSAGE: {aio_pika_message}")
    except Exception as e:
        print(f"DIDN'T SEND MESSAGE: {message} \n {e}")
