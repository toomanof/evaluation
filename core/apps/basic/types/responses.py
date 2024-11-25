from datetime import datetime
from typing import (
    Any,
    List,
    Literal,
    Optional,
    Union,
    Collection,
)

from pydantic import (
    BaseModel,
    Field,
    PrivateAttr,
    RootModel,
)
from typing_extensions import TypedDict
from .types import (
    WBFilterListGoods,
    WBListGoodsSizeObject,
    ObjectCharacteristics,
    ItemListOfObjects,
    ParentSubject,
    WBSalesReportItem,
    WBSales,
    UnauthorizedErrors,
    ListBaseModel,
    WBNomenclature,
    WBCursorNomenclature,
    WBErrorNomenclature,
    WBProductInPlatform,
    EliminateEmptyListAndDictModel,
    WBDataStock,
    WBDataObjectErrorExportStock,
    PriceInfo,
    WBResponseError,
    SupplyOrder,
    WBFBOOrder,
    WBFBSOrder,
    WBStock,
    SupplierTaskMetadataBuffer,
    WBStockFBO,
)


class WBResponseBase(BaseModel):
    """
    Общая структура ответа от WB
    """

    data: Optional[Any] = Field(title="Результат", default=None, description="object or null")
    error: Optional[bool] = Field(title="Флаг ошибки", default=False, description="boolean")
    errorText: Optional[str] = Field(title="Описание ошибки", default=None, description="string")

    def __or__(self, other):
        return other


class WBResponse(BaseModel):
    """
    Общая структура ответа от WB
    """

    data: Optional[Any] = Field(title="Результат", default=None, description="object or null")
    error: Optional[bool] = Field(title="Флаг ошибки", default=False, description="boolean")
    errorText: Optional[str] = Field(title="Описание ошибки", default=None, description="string")
    additionalErrors: Optional[Any] = Field(title="Дополнительные ошибки", default=None)

    def __or__(self, other):
        return other


class WBResponseUpdatePriceInProductErrors(BaseModel):
    errors: list[str] = Field(title="")  # TODO: unconfirmed by doc according to actual error response


class WBResponseUpdatePriceInProductError(BaseModel):
    root: Optional[Union[UnauthorizedErrors, str, WBResponseUpdatePriceInProductErrors]] = None


class WBPositiveResponseUpdatePriceInProduct(BaseModel):
    uploadId: Optional[int] = Field(title="", default=None)
    alreadyExists: Optional[bool] = Field(title="", default=None)
    result: Optional[str] = Field(title="", default=None)  # NOTE: special response field for raw responses


class WBResponseUpdatePriceInProduct(BaseModel):
    root: Optional[Union[WBResponseUpdatePriceInProductError, WBPositiveResponseUpdatePriceInProduct]] = None


class WBResponseSuppliesV1Item(BaseModel):
    """
    Если часовой пояс не указан, то берется Московское время UTC+3
    """

    incomeId: int  # Номер поставки
    number: str = Field(..., max_length=40, min_length=0)  # Номер УПД
    date: datetime  # Дата поступления
    lastChangeDate: (
        datetime  # Дата и время обновления информации в сервисе. Соответствует параметру dateFrom в запросе
    )
    supplierArticle: str = Field(..., max_length=75, min_length=0)  # Артикул продавца
    techSize: str = Field(..., max_length=30, min_length=0)  # Размер товара (пример S, M, L, XL, 42, 42-43)
    barcode: str = Field(..., max_length=30, min_length=0)  # Бар-код
    quantity: int  # Количество
    totalPrice: float  # Цена из УПД
    dateClose: datetime  # Дата принятия (закрытия) в WB
    warehouseName: str = Field(..., max_length=50, min_length=0)  # Название склада
    nmId: int  # Артикул WB
    status: str = Field(..., max_length=50, min_length=0)  # Текущий статус поставки


class WBResponseSuppliesV1(ListBaseModel):
    root: Optional[Union[Literal[None], List[WBResponseSuppliesV1Item]]] = None  # Список поставок


class WBResponseListNomenclaturesV2(WBResponse):
    """
    Структура списка номенклатуры V2, возвращаемая WB.
    """

    cards: Optional[list[WBNomenclature]] = Field(default_factory=list)
    """
    Список карточек товаров
    """

    cursor: WBCursorNomenclature
    """
    Курсор
    """


class WBResponseListErrorsNomenclatures(WBResponse):
    """
    Структура ответа метода получения списка номенклатур с ошибками от WB

    error: bool - Флаг ошибки.
    errorText: Optional[str] - Описание ошибки.
    additionalErrors: Optional[str] - Дополнительные ошибки.
    """

    data: list[WBErrorNomenclature]
    """
    Список номенклатур с ошибками
    """


class WBResponseListCardProducts(WBResponse):
    """
    Структура ответа метода получения списка созданных КТ от WB

    error: bool - Флаг ошибки.
    errorText: Optional[str] - Описание ошибки.
    additionalErrors: Optional[str] - Дополнительные ошибки.
    """

    data: list[WBProductInPlatform]
    """
    Список созданных КТ
    """


class WBResponseListStock(EliminateEmptyListAndDictModel):
    """
    Структура ответа товаров поставщика с их остатками.
    """

    total: int
    """
    Количество товаров
    """

    stocks: Optional[list[WBDataStock]]
    """
    Описание остатка товара.
    """


class WBResponseExportStock(WBResponse):
    """
    Структура ответа метода Обновление остатков товара

    data: WBDataObjectErrorExportStock - список ошибок
    error: bool - Флаг ошибки.
    errorText: Optional[str] - Описание ошибки.
    additionalErrors: Optional[str] - Дополнительные ошибки.
    """

    data: WBDataObjectErrorExportStock


class WBResponseGetPriceInfo(ListBaseModel):
    root: List[PriceInfo]


class WBResponseCreateCardsProductsError(BaseModel):
    """
    Структура отрицательного ответа метода создания КТ от WB
    """

    root: Optional[Union[UnauthorizedErrors, str]] = None


class WBResponseCreateCardsProducts(WBResponse):
    """
    Структура ответа метода создания КТ от WB
    """

    pass


class WBResponseUpdateCardsProductsError(BaseModel):
    """
    Структура отрицательного ответа метода обновления медиа в КТ от WB
    """

    root: Optional[Union[UnauthorizedErrors, str]] = None


class WBResponseUpdateCardsProducts(WBResponse):
    """
    Структура ответа метода обновления КТ от WB
    """

    pass


class WBResponseUpdateMediaInCardProductError(BaseModel):
    root: Optional[Union[UnauthorizedErrors, str]] = None


class WBResponseUpdateMediaInCardProduct(WBResponse):
    """
    Структура ответа метода обновления медиа в КТ от WB
    """

    pass


class WBResponseAddMediaInCardProduct(WBResponse):
    """
    Структура ответа метода добавления медиа в КТ от WB

    data: Optional[Any] - результат
    error: bool - Флаг ошибки.
    errorText: Optional[str] - Описание ошибки.
    additionalErrors: Optional[str] - Дополнительные ошибки.
    """

    pass


class WBResponseWarehouse(BaseModel):
    """
    Описание склада продавца
    """

    name: str = Field(description="Название")
    officeId: int = Field(description="ID склада WB")
    id: int = Field(description="ID склада продавца")
    cargoType: int = Literal[
        1,
        2,
        3,
    ]
    deliveryType: int = Literal[
        1,
        2,
        3,
    ]

    @property
    def id_mp(self):
        return self.officeId

    def args_for_insert_row(self, company_id: int, marketplace_id: int) -> tuple:
        return self.name, self.id, self.model_dump_json(), company_id, marketplace_id

    def args_for_update_row(self, company_id: int, marketplace_id: int) -> tuple:
        return self.name, self.id, self.model_dump_json(), company_id, marketplace_id


class WBResponseListWarehouse(ListBaseModel):
    """
    Список складов продавца
    """

    root: List[WBResponseWarehouse]  # Список складов продавца


class WBResponseCreateSupply(BaseModel):
    """
    Ответ запроса создания новой поставки
    """

    _version: int = PrivateAttr(default=3)

    id: str


class WBResponseGetInfoSupply(BaseModel):
    """
    Ответ запроса получения информации о поставке
    """

    _version: int = PrivateAttr(default=3)

    id: str
    done: bool
    createdAt: Optional[datetime]
    closedAt: Optional[datetime]
    scanDt: Optional[datetime]
    name: str
    isLargeCargo: Optional[bool]

    class Config:
        json_encoders = {datetime: lambda v: v.timestamp()}


class WBResponseGetSupplies(BaseModel):
    """
    Ответ запроса получения списка поставок
    """

    _version: int = PrivateAttr(default=3)

    next: int
    supplies: List[WBResponseGetInfoSupply]


class WBResponseGetSuppliesExtra(BaseModel):
    _version: int = PrivateAttr(default=3)

    root: Union[WBResponseGetSupplies, WBResponseError]


class WBResponseCreateSupplyExtra(BaseModel):
    _version: int = PrivateAttr(default=3)

    root: Union[WBResponseCreateSupply, WBResponseError]


class WBResponseGetInfoSupplyExtra(BaseModel):
    _version: int = PrivateAttr(default=3)

    root: Union[WBResponseGetInfoSupply, WBResponseError]


class WBResponseGetSupplyOrders(BaseModel):
    _version: int = PrivateAttr(default=3)

    orders: List[SupplyOrder]


class WBResponseGetSupplyOrdersExtra(BaseModel):
    _version: int = PrivateAttr(default=3)

    root: Union[WBResponseGetSupplyOrders, WBResponseError]


class WBResponseReshipmentOrders(BaseModel):
    _version: int = PrivateAttr(default=3)

    orders: List[TypedDict("User", {"supplyID": str, "orderID": int})]


class WBResponseReshipmentOrdersExtra(BaseModel):
    _version: int = PrivateAttr(default=3)

    root: Union[WBResponseReshipmentOrders, WBResponseError]


class WBResponseSupplyBarcode(BaseModel):
    _version: int = PrivateAttr(default=3)

    barcode: str
    file: bytes


class WBResponseSupplyBarcodeExtra(BaseModel):
    _version: int = PrivateAttr(default=3)

    root: Union[WBResponseSupplyBarcode, WBResponseError]


class WBResponseOrdersStatus(BaseModel):
    _version: int = PrivateAttr(default=3)

    orders: List[
        TypedDict(
            "Orders",
            {
                "id": int,
                "supplierStatus": Literal[
                    "new",
                    "confirm",
                    "complete",
                    "cancel",
                    "deliver",
                    "receive",
                    "reject",
                ],
                "wbStatus": Literal[
                    "waiting",
                    "sorted",
                    "sold",
                    "canceled",
                    "canceled_by_client",
                    "defect",
                    "ready_for_pickup",
                    "declined_by_client",
                ],
            },
        )
    ]


class WBResponseOrdersStatusExtra(BaseModel):
    _version: int = PrivateAttr(default=3)

    root: Union[WBResponseOrdersStatus, WBResponseError]


# class WBResponseFBOOrders(RootModel):
class WBResponseFBOOrders(ListBaseModel):
    root: Optional[list[WBFBOOrder]] = Field(title="Список заказов", default=list)


class WBResponseFBSOrders(BaseModel):
    _version: int = PrivateAttr(default=3)

    next: Optional[int] = 0
    orders: List[WBFBSOrder]


class WBResponseOrdersExtra(RootModel):
    _version: int = PrivateAttr(default=3)

    root: Union[WBResponseFBSOrders, WBResponseError]


class WBResponseOrdersNew(BaseModel):
    _version: int = PrivateAttr(default=3)

    orders: List[WBFBSOrder]


class WBResponseOrdersV3(WBResponseOrdersNew, WBResponseError):
    _version: int = PrivateAttr(default=3)


class WBResponseOrdersMetaSGTIN(RootModel):
    _version: int = PrivateAttr(default=3)

    root: Union[None, WBResponseError]


class WBResponseOrdersStickers(BaseModel):
    _version: int = PrivateAttr(default=3)

    stickers: List[
        TypedDict(
            "Sticker",
            {
                "orderId": int,
                "partA": int,
                "partB": int,
                "barcode": str,
                "file": bytes,
            },
        )
    ]


class WBResponseOrdersStickersExtra(RootModel):
    _version: int = PrivateAttr(default=3)

    root: Union[WBResponseOrdersStickers, WBResponseError]


class WBResponseWarehouseStock(WBResponseError):
    stocks: list[WBStock]


class WBResponseUpdateWarehouseStocks(BaseModel):
    _version: int = PrivateAttr(default=3)

    root: Union[None, WBResponseError]


class WBResponseSupplyDeliver(BaseModel):
    _version: int = PrivateAttr(default=3)

    root: Union[None, WBResponseError]


class WBResponseSupplyAddOrders(BaseModel):
    _version: int = PrivateAttr(default=3)

    root: Union[None, WBResponseError]


class WBResponseDeleteSupply(BaseModel):
    _version: int = PrivateAttr(default=3)

    root: Union[None, WBResponseError]


class WBResponseDeleteWarehouseStocks(BaseModel):
    _version: int = PrivateAttr(default=3)

    root: Union[None, WBResponseError]


class WBResponseOrderCancel(BaseModel):
    _version: int = PrivateAttr(default=3)

    root: Union[None, WBResponseError]


class WBResponseSales(ListBaseModel):
    root: List[WBSales]


class WBResponseRealizationSalesReport(ListBaseModel):
    root: List[WBSalesReportItem]


class WBResponseOfficesItem(BaseModel):
    """
    Описание склада WB
    """

    address: str  # Адрес
    name: str  # Название
    city: str  # Город
    id: int  # ID
    longitude: float  # Долгота
    latitude: float  # Широта
    selected: bool  # Признак того, что склад уже выбран продавцом


class WBResponseWarehouseItem(BaseModel):
    """
    Описание склада WB
    """

    ID: int  # 210515,
    name: str  # "Вёшки",
    address: str  # "Липкинское шоссе, 2-й километр, вл1с1, посёлок Вёшки, городской округ Мытищи, Московская область",
    workTime: str  # "24/7",
    acceptsQR: bool  # false


class WBResponseOffices(ListBaseModel):
    """
    Список складов WB
    """

    root: List[WBResponseOfficesItem]  # Список складов WB


class WBResponseWarehouses(ListBaseModel):
    """
    Список складов WB
    """

    root: List[WBResponseWarehouseItem]  # Список складов WB


class WBResponseWarehouseCreate(BaseModel):
    id: int  # ID склада продавца


class WBResponseTagStatisticsForSelectedPeriod(BaseModel):
    id: Optional[int] = Field(default=None, description="Идентификатор тега")
    name: Optional[str] = Field(default=None, description="Название тега")


class WBResponseObjectStatisticsForSelectedPeriod(BaseModel):
    id: Optional[int] = Field(default=None, description="Идентификатор предмета")
    name: Optional[str] = Field(default=None, description="Название предмета")


class WBResponseStockStatisticsForSelectedPeriod(BaseModel):
    stocksMp: Optional[int] = Field(
        default=0,
        description="Остатки МП, шт. (Общее количество остатков на складе продавца)",
    )
    stocksWb: Optional[int] = Field(
        default=0,
        description="Остатки на складах Wildberries (Общее количество остатков на складах Wildberries)",
    )


class WBResponseCardStatisticsForSelectedPeriod(BaseModel):
    nmID: int
    vendorCode: str
    brandName: Optional[str]
    tags: Optional[Collection[WBResponseTagStatisticsForSelectedPeriod]] = Field(default=None)
    object: Optional[Collection[WBResponseObjectStatisticsForSelectedPeriod]] = Field(default=None)
    statistics: Optional[dict] = Field(default=None, description="Статистика")
    stocks: WBResponseStockStatisticsForSelectedPeriod
    date_reg: Optional[str] = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    @property
    def id(self):
        return self.nmID

    def args_for_insert_row(self, company_id: int, marketplace_id: int) -> tuple:
        return (
            self.nmID,
            self.vendorCode,
            self.model_dump_json(
                exclude={
                    "date_reg",
                }
            ),
            company_id,
            marketplace_id,
            self.stocks.stocksMp,
            self.stocks.stocksWb,
            datetime.strptime(self.date_reg, "%Y-%m-%d"),
        )

    def args_for_update_row(self, company_id: int, marketplace_id: int) -> tuple:
        return self.args_for_insert_row(company_id, marketplace_id)


class WBResponseDataStatisticsForSelectedPeriod(BaseModel):
    page: int
    isNextPage: bool = Field(description="Есть ли следующая страница (false - нет, true - есть)")
    cards: Optional[Collection[WBResponseCardStatisticsForSelectedPeriod]]

    class Config:
        arbitrary_types_allowed = True


class WBResponseStatisticsForSelectedPeriod(WBResponse):
    data: WBResponseDataStatisticsForSelectedPeriod


class WBResponseParentSubjects(WBResponse):
    data: Optional[list[ParentSubject]] = Field(default=None)


class WBResponseListOfObjects(WBResponse):
    data: Optional[list[ItemListOfObjects]] = Field(default=None)


class WBResponseObjectCharacteristics(WBResponse):
    data: Optional[list[ObjectCharacteristics]] = Field(default_factory=list)


class WBResponseFilterListGoods(WBResponse):
    """Структура ответа для эндпоинта получения информации обо всех товаров(простыми словами фильтр)."""

    data: Optional[WBFilterListGoods]


class WBResponseListGoodsSize(WBResponseBase):
    """Структура ответа для эндпоинта получения информации о размерах товара."""

    data: Optional[WBListGoodsSizeObject]


class WBResponseObjectHistoryGoods(BaseModel):
    nmID: Optional[int]
    vendorCode: Optional[str]
    sizeID: Optional[int]
    techSizeName: Optional[str]
    price: Optional[int]
    currencyIsoCode4217: Optional[str]
    discount: Optional[int]
    status: Optional[int]
    errorText: Optional[str]


class WBResponseItemSetPricesAndDiscounts(BaseModel):
    id: int = Field(description="ID загрузки")
    alreadyExists: bool = Field(description="Флаг дублирования загрузки: true — такая загрузка уже есть")


class WBResponseSetPricesAndDiscounts(WBResponse):
    data: Optional[WBResponseItemSetPricesAndDiscounts] = Field(default_factory=list)


class WBResponseObjectDownloadProcessedStatus(WBResponse):
    uploadID: Optional[int] = Field(description="ID загрузки", default=None)
    status: Optional[int] = Field(
        description="Статус загрузки:"
        "3 — обработана, в товарах нет ошибок, цены и скидки обновились"
        "4 — отменена"
        "5 — обработана, но в товарах есть ошибки."
        "6 — обработана, но во всех товарах есть ошибки.",
        default=None,
    )
    uploadDate: Optional[str] = Field(description="Дата и время, когда загрузка создана. YYYY-MM-DDTHH:MM:SSZ")
    activationDate: Optional[str] = Field(
        description="Дата и время, когда загрузка отправляется в обработку." "YYYY-MM-DDTHH:MM:SSZ",
        default=None,
    )
    overAllGoodsNumber: Optional[int] = Field(description="Всего товаров", default=None)
    successGoodsNumber: Optional[int] = Field(description="Товаров без ошибок", default=None)


class WBResponseDownloadProcessedStatus(WBResponse):
    data: Optional[WBResponseObjectDownloadProcessedStatus] = Field(default=None)


class WBResponseObjectProcessedLoadDetail(BaseModel):
    uploadID: Optional[int]
    historyGoods: list[WBResponseObjectHistoryGoods] = Field(default_factory=list)


class WBResponseObjectRawLoadDetail(BaseModel):
    uploadID: Optional[int]
    bufferGoods: list[WBResponseObjectHistoryGoods] = Field(default_factory=list)


class WBResponseProcessedLoadDetails(WBResponse):
    data: Optional[WBResponseObjectProcessedLoadDetail] = Field(default=None)


class WBResponseRawLoadDetails(BaseModel):
    data: Optional[WBResponseObjectProcessedLoadDetail] = Field(default=None)


class WBResponseRawLoadProgress(WBResponse):
    data: Optional[SupplierTaskMetadataBuffer] = Field(default=None)


class WBResponseWBStockFBO(RootModel):
    root: Optional[list[WBStockFBO]] = Field(title="Список остатков FBO", default=list)
