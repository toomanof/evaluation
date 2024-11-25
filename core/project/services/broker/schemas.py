from aio_pika import Exchange, Queue
from aio_pika.abc import AbstractChannel, AbstractIncomingMessage, ConsumerTag, TimeoutType


from pamqp.common import Arguments
from dataclasses import dataclass
from typing import (
    Any,
    Awaitable,
    Callable,
    Optional,
)


@dataclass
class Publisher:
    channel: AbstractChannel
    queue: Queue
    exchange: Exchange


@dataclass
class ConsumerParams:
    callback: Callable[[AbstractIncomingMessage], Awaitable[Any]]
    no_ack: bool = True
    exclusive: bool = False
    arguments: Arguments = None
    consumer_tag: Optional[ConsumerTag] = None
    timeout: TimeoutType = None


@dataclass
class Consumer:
    channel: AbstractChannel
    queue: Queue
    exchange: Exchange
    params: ConsumerParams
