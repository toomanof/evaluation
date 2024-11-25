from core.apps.basic.types.from_platform import StatusOrderWildberries, OrderStatusInPlatform
from core.apps.utils import get_postgresql_value

CODE_MARKETPLACE = "WILDBERRIES"

VERSION_1 = 1
VERSION_2 = 2
VERSION_3 = 3
COUNT_ITEMS_ONE_ITERATION_FILTER_CARDS = 100
COUNT_ITEMS_ONE_ITERATION_CREATE_OR_UPDATE_CARDS_V2 = 1000
COUNT_ITEMS_ONE_ITERATION_CREATE_CARDS_V3 = 100
COUNT_ITEMS_ONE_ITERATION_UPDATE_CARDS_V3 = 1

ORDER_TYPE = {
    "Клиентский": "ready_for_pickup",
    "Возврат Брака": "defect",
    "Принудительный возврат": "canceled_by_client",
    "Возврат обезлички": "canceled_by_client",
    "Возврат Неверного Вложения": "canceled_by_client",
    "Возврат Продавца": "canceled_by_client",
}

MATCHING_STATUS_PLATFORM_ORDER = {
    "new": "unconfirmed",
    "confirm": "unconfirmed",
    "complete": "unconfirmed",
    "cancel": "canceled",
    "deliver": "fulfilled",
    "shipped": "shipped",
    "sorted": "shipped",
    "receive": "fulfilled",
    "reject": "canceled",
    "waiting": "unconfirmed",
    "sold": "fulfilled",
    "canceled": "canceled",
    "canceled_by_client": "canceled",
    "declined_by_client": "canceled",
    "defect": "canceled",
    "ready_for_pickup": "shipped",
}

MATCHING_STATUS_PLATFORM_ORDER_POSTGRESQL = {
    get_postgresql_value(mp_status): get_postgresql_value(status)
    for mp_status, status in MATCHING_STATUS_PLATFORM_ORDER.items()
}

HTTP_RESPONSE_CODES_FOR_REPEAT_REQUEST = {429, 500}
HTTP_RESPONSE_CODES_ACCESS_DENIED = {401, 403}
HTTP_RESPONSE_CODES_STOP_REQURESTS = {400, 401, 403, 404}


MATCHING_MARKETPLACE_STATUS_ORDER = {
    StatusOrderWildberries.NEW: OrderStatusInPlatform.NEW,
    StatusOrderWildberries.CONFIRM: OrderStatusInPlatform.AWAITING_PACKAGING,
    StatusOrderWildberries.COMPLETE: OrderStatusInPlatform.AWAITING_DELIVER,
    StatusOrderWildberries.CANCEL: OrderStatusInPlatform.CANCELED,
    StatusOrderWildberries.DELIVERY: OrderStatusInPlatform.SHIPPED,
    StatusOrderWildberries.SHIPPED: OrderStatusInPlatform.SHIPPED,
    StatusOrderWildberries.DELIVERED: OrderStatusInPlatform.DELIVERED,
    StatusOrderWildberries.CLIENT_NOT_ACCEPTED: OrderStatusInPlatform.RETURN,
    StatusOrderWildberries.WAITING: OrderStatusInPlatform.AWAITING_PACKAGING,  # "сборочное задание в работе"
    StatusOrderWildberries.SORTED: OrderStatusInPlatform.AWAITING_PACKAGING,  # "сборочное задание отсортировано"
    StatusOrderWildberries.SOLD: OrderStatusInPlatform.DELIVERED,  # сборочное задание получено покупателем
    StatusOrderWildberries.CANCELED: OrderStatusInPlatform.CANCELED,
    StatusOrderWildberries.CANCELED_BY_CLIENT: OrderStatusInPlatform.CANCELED,
    StatusOrderWildberries.DECLINED_BY_CLIENT: OrderStatusInPlatform.CANCELED,
    StatusOrderWildberries.DEFECT: OrderStatusInPlatform.CANCELED,
    StatusOrderWildberries.READY_FOR_PICKUP: OrderStatusInPlatform.SHIPPED,
    StatusOrderWildberries.FULFILLED: OrderStatusInPlatform.DELIVERED,
    StatusOrderWildberries.UNCONFIRMED: OrderStatusInPlatform.NEW,
}
