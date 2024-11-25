from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class EventInMSMarketplace(Enum):
    """
    Перечисления событий отправляемых на микро-сервисы
    Должны соответствовать именам вызываемых методов класса CommonHandler в микросервисах
    """

    START_EXPORT_PRODUCTS = "export_products"
    START_EXPORT_PRICES = "export_prices"
    START_IMPORT_STOCK = "import_stock"
    START_IMPORT_STOCK_FBO = "import_stock_fbo"
    START_EXPORT_STOCK = "export_stock"
    START_IMPORT_WAREHOUSES = "import_warehouses"
    START_IMPORT_ORDERS = "import_orders"
    START_BALANCE_MOVEMENT = "balance_movement"
    START_GENERATE_BARCODES = "generate_barcodes"
    START_CHECKING_ORDER_STATUSES = "checking_order_statuses"


class OrderStatusInPlatform:
    NEW = "NEW"  # Новый
    AWAITING_PACKAGING = "AWAITING_PACKAGING"  # В сборке
    AWAITING_DELIVER = "AWAITING_DELIVER"  # Собран
    SHIPPED = "SHIPPED"  # Отгружен
    DELIVERED = "DELIVERED"  # Доставлен
    CANCELED = "CANCELED"  # Отмена
    RETURN = "RETURN"  # Возврат
    ARBITRATION = "ARBITRATION"  # арбитраж
    UNDEFINED = "UNDEFINED"  # Неопределенный статус


class StatusOrderWildberries:
    NEW = "new"  # Новый заказ
    CONFIRM = "confirm"  # Принял заказ(На сборке)
    COMPLETE = "complete"  # Сборочное задание завершено, ожидает отгрузки
    CANCEL = "cancel"  # Сборочное задание отклонено
    DELIVERY = "deliver"  # На доставке курьером
    DELIVERED = "receive"  # Курьер довез и клиент принял товар
    CLIENT_NOT_ACCEPTED = "reject"  # Клиент не принял товар
    PICKUP_ACCEPTED = 8  # Товар для самовывоза из магазина принят к работе
    PICKUP_READY = 9  # Товар для самовывоза из магазина готов к выдаче
    SHIPPED = "shipped"  # Товар отгружен
    WAITING = "waiting"  # "сборочное задание в работе"
    SORTED = "sorted"  # "сборочное задание отсортировано"
    SOLD = "sold"  # сборочное задание получено покупателем
    CANCELED = "canceled"
    CANCELED_BY_CLIENT = "canceled_by_client"
    DECLINED_BY_CLIENT = "declined_by_client"
    DEFECT = "defect"
    READY_FOR_PICKUP = "ready_for_pickup"
    FULFILLED = "fulfilled"
    UNCONFIRMED = "unconfirmed"


class RelationProduct(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    product: int
    marketplace: int
    idMp: str = Field(alias="id_mp")
    variant: int
    name: str
    article: str


class CompanySmallContent(BaseModel):
    id: int
    title: str
    owner: int


class MarketplaceWithHeader(BaseModel):
    id: int
    company: CompanySmallContent
    headers: dict
    title: str


class WarehouseFBO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: int
    name: str


class ResponseCompanyWithHeader(BaseModel):
    count: Optional[int] = Field(default=None)
    next: Optional[str] = Field(default=None)
    previous: Optional[str] = Field(default_factory=None)
    results: list[MarketplaceWithHeader] = Field(default_factory=list)


class ResponseRelationProduct(BaseModel):
    count: Optional[int] = Field(default=None)
    next: Optional[str] = Field(default=None)
    previous: Optional[str] = Field(default_factory=None)
    results: list[RelationProduct] = Field(default_factory=list)


class ResponseChangeStatusOrderFromMs(BaseModel):
    id_platform: int = Field(title="Идентификатор заказа в платформе Order")
    order_id: str = Field(title="Идентификатор заказа в маркетплейсе")
    old_status_platform: str = Field(title="Статус заказа до изменения")
    new_status_platform: Optional[str] = Field(title="Новый статус заказа в модели Order", default=None)
    new_status_from_marketplace: Optional[str] = Field(
        title="Новый статус заказа в модели RelationsMpOrder", default=None
    )


class ResponseWarehousesFBO(BaseModel):
    count: Optional[int] = Field(default=None)
    next: Optional[str] = Field(default=None)
    previous: Optional[str] = Field(default_factory=None)
    results: list[WarehouseFBO] = Field(default_factory=list)
