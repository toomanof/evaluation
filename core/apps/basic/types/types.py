from datetime import datetime, timedelta
from enum import Enum
from typing import (
    Any,
    Dict,
    List,
    Literal,
    NewType,
    Optional,
    Union,
    Iterable,
)

from pydantic import (
    BaseModel,
    Field,
    PrivateAttr,
    model_validator,
    RootModel,
    functional_validators,
)

from core.apps.basic.types.from_platform import StatusOrderWildberries
from core.apps.basic.types.to_platform import ResponseOrderToPlatform

WbNmID = NewType("WbNmID", int)


class BarcodeType(str, Enum):
    SVG = "svg"
    ZPLV = "zp" "lv"
    ZPLH = "zp" "lh"
    PNG = "png"


class EliminateEmptyListAndDictModel(BaseModel):
    """
    Миксин для восприятия пустых словарей и списков как None.
    Без него пустые ответы вызывают ошибку валидации pydantic'а.
    """

    # TODO: В дальнейшем уточнить назначение валидации!

    @classmethod
    def remove_empty(cls, values) -> Any:
        for key, value in values.items():
            if isinstance(value, (dict, list)) and not value:
                values[key] = None
        return values

    _validator: functional_validators.ModelBeforeValidator = remove_empty
    _validations = model_validator(mode="before")(_validator)


class ListBaseModel(RootModel):
    def dict(self, **kwargs):
        result = super().model_dump(**kwargs)
        return result.get("root", result)

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]

    def __len__(self):
        if "root" in self.model_fields:
            try:
                return len(self.__dict__.get("root", {}))
            except (Exception,):
                return ...
        return 0


class WBCharacteristicValue(BaseModel):
    id: int = Field(description="Идентификатор характеристики")
    name: Optional[str] = Field(description="Название характеристики")
    value: Any = Field(description="Значение характеристики. Тип значения зависит от типа характеристики")


class WBDimensions(BaseModel):
    length: Optional[int] = Field(description="Длина", default=None)
    width: Optional[int] = Field(description="Ширина", default=None)
    height: Optional[int] = Field(description="Высота", default=None)


class WbListNmID(ListBaseModel):
    root: list[WbNmID]


class WBResponseError(BaseModel):
    _version: int = PrivateAttr(default=3)

    code: Optional[str] = Field(default=None)
    message: Optional[str] = Field(default=None)
    data: Optional[Dict[str, Any]] = Field(default=None)


class UnauthorizedErrors(str, Enum):
    TokenMissing = "proxy: unauthorized"
    TokenInvalid = "proxy: invalid token"
    TokenNotFound = "proxy: not found"


class WBResponseErrors(BaseModel):
    root: Optional[Union[UnauthorizedErrors, str, WBResponseError]] = None


class WBResponseCursor(BaseModel):
    """
    Структура курсора, возвращаемая WB.
    """

    offset: int
    """
    Смещение от начала списка с указанными критериями поиска и сортировки.
    """

    limit: int
    """
    Ограничение по количеству НМ в ответе
    """

    total: int
    """
    Общее количество НМ. (Временно отключено)
    """


class WBCursorNomenclature(BaseModel):
    """
    Структура курсора, возвращаемая в списке номенклатуры WB.
    """

    updatedAt: Optional[str] = None
    """
    Дата, с которой надо запрашивать следующий список КТ
    """

    nmID: Optional[WbNmID] = None
    """
    Номер номенклатуры, с которой надо запрашивать следующий список КТ
    """

    total: Optional[int] = None
    """
    Количество возвращенных КТ
    """


class WBCursorNomenclatureV2(BaseModel):
    """
    Структура курсора, возвращаемая в списке номенклатуры WB.
    """

    updatedAt: Optional[str] = None
    """
    Время обновления последней КТ из предыдущего ответа на запрос списка КТ.
    """

    nmID: Optional[int] = None
    """
    Номенклатура последней КТ из предыдущего ответа на запрос списка КТ.
    """

    limit: Optional[int] = None
    """
    Количество запрашиваемых КТ.
    """


class WBFilterNomenclature(BaseModel):
    """
    Структура фильтра, возвращаемая в списке номенклатуры WB.
    """

    textSearch: Optional[Union[int, str]] = None  # NOTE: int values cause errors although described in documentation
    """
    Поиск по номеру НМ или артикулу товара.
    """

    withPhoto: Optional[int] = Field(ge=-1, le=1)
    """
    Флаг показа фото:
    -1 - Показать все КТ.
     0 - Показать КТ без фото.
     1 - Показать КТ с фото.
    """
    tagIDs: Optional[Iterable[int]] = None
    allowedCategoriesOnly: Optional[bool] = None
    objectIDs: Optional[Iterable[int]] = None
    brands: Optional[Iterable[str]] = None
    imtID: Optional[int] = None


class WBSortNomenclature(BaseModel):
    """
    Поле по которому будет сортироваться список КТ (пока что поддерживается только updatedAt).
    """

    ascending: str
    """
    Тип сортировки.
    """


class WBCreateCardProductSize(BaseModel):
    """
    Структура размера карточки товара, возвращаемая WB.
    """

    techSize: Optional[str | int] = None
    """
    Размер поставщика (пример S, M, L, XL, 42, 42-43)
    """

    wbSize: Optional[str] = None
    """
    Рос. размер
    """

    price: Optional[int] = None
    """
    Цена
    """

    skus: list[Optional[str]] = Field(default=list)
    """
    Массив бар-кодов, строковых идентификаторов размеров поставщика
    """


class WBCardProductSize(WBCreateCardProductSize):
    """
    Структура размера карточки товара, возвращаемая WB.

    techSize: Optional[str] - Размер поставщика (пример S, M, L, XL, 42, 42-43)
    wbSize: Optional[str] - Рос. размер
    price: Optional[int] - Цена
    skus: list[str] - Массив бар-кодов, строковых идентификаторов размеров поставщика
    """

    chrtID: Optional[int] = None
    """
    Числовой идентификатор размера для данной номенклатуры Wildberries
    """


class WBCardProduct(BaseModel):
    """
    Структура карточки товара, возвращаемая WB.
    """

    imtID: Optional[int | str] = None
    """
    Идентификатор карточки товара (нужен для группирования НМ в одно КТ)
    """

    nmID: Optional[WbNmID] = None
    """
    Числовой идентификатор номенклатуры Wildberries
    """

    vendorCode: Optional[str]
    """
    Вендор код, текстовый идентификатор номенклатуры поставщика
    """

    mediaFiles: Optional[list[str]] = None
    """
    """

    sizes: Optional[list[WBCardProductSize]] = None
    """
    Список размеров (Варианты)
    """

    characteristics: Optional[list[dict]]
    """
    Список характеристик
    """

    is_variant: Optional[bool] = False
    """
    Флаг варианта (Внутренние поле платформы)
    """

    sub_id_mp: Optional[str | int] = None
    """
    ID текущего размера. (Внутренние поле платформы)
    """

    index_active_variant: Optional[int] = 0
    """
    Индекс активного размера. (Внутренние поле платформы)
    """

    barcodes: Optional[list[str]] = None
    """
    Список штрих-кодов. (Внутренние поле платформы)
    """

    price: Optional[int] = None
    """
    Цена текущего варианта. (Внутренние поле платформы)
    """

    dimensions: Optional[WBDimensions] = None


class WBPhoto(BaseModel):
    biggest: Optional[Any] = Field(alias="516x288", default=None)
    big: Optional[Any] = None
    small: Optional[Any] = None


class WBCardProductForUpdate(BaseModel):
    """
    Структура карточки товара, используемая в запросе обновления карточки товара WB.
    """

    imtID: Optional[int] = None
    """
    Идентификатор карточки товара (нужен для группирования НМ в одно КТ)
    """

    nmID: Optional[WbNmID] = None
    """
    Числовой идентификатор номенклатуры Wildberries
    """

    vendorCode: str
    """
    Вендор код, текстовый идентификатор номенклатуры поставщика
    """
    subjectID: Optional[int] = None
    subjectName: Optional[str] = None
    brand: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    dimensions: Optional[WBDimensions] = None
    sizes: Optional[list[WBCardProductSize]] = None
    """
    Список размеров (Варианты)
    """

    characteristics: Optional[list[dict]] = None
    """
    Список характеристик
    """
    mediaFiles: Optional[list[str]] = None
    object: Optional[str] = None
    objectID: Optional[int] = None


class WBTagColor(str, Enum):
    Gray = "D1CFD7"
    Red = "FEE0E0"
    Purple = "ECDAFF"
    Blue = "E4EAFF"
    Green = "DEF1DD"
    Yellow = "FFECC7"


class WBTag(BaseModel):
    id: int = Field(title="Идентификатор тега")
    name: Any = Field(title="Название тега")
    color: WBTagColor = Field(title="Цвет тега в формате HEX")

    class Config:
        use_enum_values = True


class WBNomenclature(BaseModel):
    """
    Структура номенклатуры возвращаемая WB.
    """

    mediaFiles: Optional[list[str]] = None
    """
    Медиафайлы номенклатуры
    """

    colors: Optional[list[str]] = None
    """
    Цвета номенклатуры
    """

    updateAt: Optional[str] = None
    """
    Дата обновления
    """

    vendorCode: str
    """
    Текстовый идентификатор НМ поставщика
    """

    brand: Optional[str] = None
    """
    Брэнд
    """

    object: Optional[str] = None
    """
    Категория для который создавалось КТ с данной НМ
    """

    objectID: Optional[int] = None

    nmID: Optional[WbNmID] = None
    """
    Числовой идентификатор номенклатуры Wildberries
    """
    imtID: Optional[int | str] = None
    isProhibited: Optional[bool] = None
    tags: Optional[list[WBTag]] = Field(default_factory=list)
    subjectID: Optional[int] = None
    subjectName: Optional[str] = None
    title: str | None = None
    photos: Optional[list[WBPhoto | str]] = Field(default_factory=list)
    video: Optional[str] = None
    dimensions: Optional[WBDimensions] = None
    description: Optional[str] = None
    characteristics: Optional[list[WBCharacteristicValue]] = Field(
        description="Массив характеристик товара", default_factory=list
    )
    sizes: Optional[list[WBCardProductSize]] = Field(default_factory=list)
    createdAt: str | None = None
    updatedAt: str | None = None


class WBProductInPlatform(WBCardProduct, WBNomenclature):
    object: Optional[str] = None
    objectID: Optional[int] = None
    discount: Optional[int] = None


class WBListProductInPlatform(BaseModel):
    items: list[WBProductInPlatform]


class WBErrorNomenclature(BaseModel):
    """
    Структура ошибки номенклатуры возвращаемая WB.
    """

    object: Optional[str] = Field(description="Категория для которой создавалось КТ с данной НМ", default=None)
    vendorCode: Optional[str] = Field(description="Текстовый идентификатор НМ поставщика", default=None)
    updatedAt: Optional[str] = Field(description="Дата и время запроса на создание КТ с данным НМ", default=None)
    errors: Optional[list[str]] = Field(
        description="Список ошибок из-за которых не обработался запрос на создание КТ с данным НМ",
        default=None,
    )
    objectID: Optional[int] = Field(description="Идентификатор предмета", default=None)


class WBDataStock(BaseModel):
    """
    Структура остатков, возвращаемая WB.
    """

    subject: str
    """
    Категория
    """

    brand: str
    """
    Бренд
    """

    name: str
    """
    Наименование
    """

    size: str
    """
    Размер
    """

    barcode: str
    """
    Бар-код
    """

    barcodes: list[str]
    """
    Массив бар-кодов
    """

    article: str
    """
    Артикул поставщика
    """

    stock: int
    """
    Остаток
    """

    warehouseName: str
    """
    Склад с товаром.
    """

    warehouseId: int
    """
    ID склада.
    """

    id: int
    """
    Числовой идентификатор
    """

    chrtId: int
    """
    Числовой идентификатор размера для данной номенклатуры Wildberries
    """

    nmId: WbNmID
    """
    Числовой идентификатор номенклатуры Wildberries
    """

    isCargoDelivery: bool


class WBDataExportStock(BaseModel):
    """
    Структура экспортируемого остатка в WB.
    """

    barcode: str
    """
    Бар-код
    """

    stock: int
    """
    Остаток
    """

    warehouseId: int
    """
    ID склада.
    """


class WBDataErrorExportStock(BaseModel):
    """
    Структура ошибок экспортируемого остатка в WB.
    """

    barcode: str
    """
    Бар-код.
    """

    err: str
    """
    Ошибка, случившаяся при загрузке остатка с данным бар-кодом.
    """


class WBDataObjectErrorExportStock(BaseModel):
    """
    Структура списка ошибок экспортируемых остатков в WB.
    """

    errors: Optional[list[WBDataErrorExportStock]]
    """
    Список ошибок
    """


class WBDataPrice(BaseModel):
    """
    Структура параметра загрузки цены в WB
    """

    nmID: WbNmID = Field(alias="nmId", title="Номенклатура")
    price: int = Field(title="Цена", description="Указывать без копеек")
    discount: Optional[int] = Field(title="Скидка", default=None)
    promoCode: Optional[float] = Field(title="Промокод", default=None)


class WBDataListPrice(ListBaseModel):
    root: List[WBDataPrice]


class WBDataPriceForMS(WBDataPrice):
    """
    Структура параметра загрузки цены через м-с WB
    """

    product_id: int
    vendorCode: str
    old_price: int
    error: Optional[Any] = Field(default=None)


class WBDataListPriceForMS(BaseModel):
    items: List[WBDataPriceForMS]


class PriceInfo(BaseModel):
    """
    Структура ответа получения цены
    """

    nmId: WbNmID
    """
    ID номенклатуры
    """

    price: float
    """
    Цена
    """

    discount: int

    promoCode: float


class SupplyUser(BaseModel):
    fio: Optional[str]
    phone: Optional[str]

    class Config:
        arbitrary_types_allowed = True


class SupplyOrder(BaseModel):
    id: int
    rid: str
    createdAt: datetime
    warehouseId: int
    prioritySc: Optional[List[str]]
    offices: Optional[List[str]]
    user: Optional[SupplyUser]
    skus: List[str]
    price: int
    convertedPrice: int
    currencyCode: int
    convertedCurrencyCode: int
    orderUid: str
    nmId: WbNmID
    chrtId: int
    article: str
    isLargeCargo: Optional[bool] = False
    supplierStatus: Optional[str]
    wbStatus: Optional[str]
    supplyId: Optional[str]


class WBFBOOrder(BaseModel):
    date: datetime = Field(
        title="Дата и время заказа",
        description="""
        Это поле соответствует параметру dateFrom в запросе, если параметр flag=1
        Если часовой пояс не указан, то берется Московское время UTC+3
        """,
    )
    lastChangeDate: datetime = Field(
        title="Дата и время обновления информации в сервисе",
        description="""
        Это поле соответствует параметру dateFrom в запросе, если параметр flag=0 или не указан
        Если часовой пояс не указан, то берется Московское время UTC+3
        """,
    )
    warehouseName: str = Field(title="Название склада отгрузки", max_length=50)
    countryName: str = Field(description="Страна", default=None)
    oblastOkrugName: str = Field(description="Округ", default=None)
    regionName: str = Field(description="Регион", default=None)
    supplierArticle: str = Field(description="Артикул продавца", default=None)
    nmId: int = Field(description="Артикул WB")
    barcode: str = Field(description="Штрихкод", default=None)
    category: str = Field(title="Категория", max_length=50)
    subject: str = Field(title="Предмет", max_length=50)
    brand: str = Field(title="Бренд", max_length=50)
    techSize: str = Field(
        title="Размер товара",
        description="Пример: S, M, L, XL, 42, 42-43",
        max_length=30,
    )
    incomeID: int = Field(title="Номер поставки (от продавца на склад)")
    isSupply: bool = Field(description="Договор поставки")
    isRealization: bool = Field(description="Договор реализации")
    totalPrice: float = Field(
        title="Цена до согласованной итоговой скидки/промо/спп",
        description="""
        Для получения цены со скидкой можно воспользоваться формулой:
        priceWithDiscount = totalPrice * (1 - discountPercent/100)
        """,
    )
    discountPercent: int = Field(
        title="Согласованный итоговый дисконт",
        description="Будучи примененным к totalPrice, даёт сумму к оплате",
    )
    spp: float = Field(description="Скидка WB")
    finishedPrice: float = Field(description="Фактическая цена с учетом всех скидок (к взиманию с покупателя)")
    priceWithDisc: float = Field(
        description="Цена со скидкой продавца, от которой считается сумма "
        "к перечислению продавцу forPay "
        "(= totalPrice * (1 - discountPercent/100))"
    )
    isCancel: bool = Field(title="Отмена заказа", description="True - заказ отменен до оплаты")
    cancelDate: Optional[datetime] = Field(
        title="Дата и время отмены заказа",
        description="""
        Если заказ не был отменен, то "0001-01-01T00:00:00"
        Если часовой пояс не указан, то берется Московское время UTC+3
        """,
        default=None,
    )
    orderType: Union[dict, str] = Field(title="Тип поступившего заказа")
    sticker: str = Field(
        title="Цифровой стикер, который клеится на товар в процессе сборки заказа по системе Маркетплейс",
    )
    gNumber: str = Field(
        title="Номер заказа",
        description="Объединяет все позиции одного заказа",
        max_length=50,
    )
    srid: str = Field(
        title="Уникальный идентификатор заказа",
        description="Примечание для использующих API Marketplace: srid равен rid в ответах методов сборочных заданий",
    )
    # Поля для взаимодействия с платформой
    id_platform: Optional[int] = Field(title="Идентификатор товара в платформе", default=None)
    name_platform: Optional[str] = Field(title="Наименование товара в платформе", default=None)
    supplierStatus: Optional[str] = None
    wbStatus: Optional[str] = Field(default="ready_for_pickup")
    nomenclature: Optional[str] = None
    transfer_to_platform: Optional[bool] = Field(default=True)
    all_products_matched_to_platform: bool = Field(default=False)
    sales: Optional[dict] = Field(description="Поле для хранения json данных с метода продаж.", default=None)
    sales_report: Optional[dict] = Field(
        description="Поле для хранения json данных с метода отчёта продаж.", default=None
    )

    @property
    def id(self):
        return self.srid

    @property
    def id_mp(self):
        return self.srid

    def args_for_insert_row(self, company_id: int, marketplace_id: int) -> tuple:
        date_reg = self.date + timedelta(hours=-3)
        return (
            self.srid,  # id_mp
            date_reg.strftime("%Y-%m-%dT%H:%M:%SZ"),  # date_reg
            self.gNumber,  # posting_number
            company_id,
            marketplace_id,
            None,  # warehouse_id
            None,  # packaging_info
            None,  # shipment_date
            "cancel" if self.isCancel else self.wbStatus or "new",  # status,
            "RUB",  # currency
            self.priceWithDisc,  # total
            self.model_dump_json(),
            "FBO",  # schema,
            self.transfer_to_platform,
        )

    def args_for_update_row(self, company_id: int, marketplace_id: int) -> tuple:
        return self.args_for_insert_row(company_id, marketplace_id)

    def model_to_platform(self, company_id: int, marketplace_id: int) -> dict:
        date_reg = self.date + timedelta(hours=-3)
        return ResponseOrderToPlatform(
            id=1,
            company_id=company_id,
            marketplace_id=marketplace_id,
            total=self.priceWithDisc,
            schema="FBO",
            created_at=date_reg.strftime("%Y-%m-%dT%H:%M:%SZ"),
            currency="RUB",
            date_reg=date_reg.strftime("%Y-%m-%dT%H:%M:%SZ"),
            status="cancel" if self.isCancel else self.wbStatus or "new",
            posting_number=self.gNumber,
            id_mp=self.srid,
            json_data=self.model_dump(),
            all_products_matched_to_platform=self.all_products_matched_to_platform,
        ).model_dump()

    @property
    def items_for_line_orders(self):
        return ((str(self.srid), self.nmId, 1, self.totalPrice, self.nomenclature),)

    @property
    def status(self):
        return self.wbStatus


class WBFBSOrder(BaseModel):
    id_order: int = Field(alias="id")
    rid: str
    createdAt: datetime | str
    warehouseId: int
    supplyId: Optional[str] = None
    # prioritySc: Optional[List[str]]
    offices: Optional[List[str]] = None
    address: Optional[dict] = None
    user: Optional[dict] = None
    skus: List[str]
    price: Optional[int] = None
    convertedPrice: Optional[int] = None
    currencyCode: Optional[int] = None
    convertedCurrencyCode: Optional[int] = None
    orderUid: Optional[str] = None
    deliveryType: Optional[Literal["dbs", "fbs", "wbgo"]] = None
    nmId: WbNmID
    id_platform: Optional[int] = Field(title="Идентификатор товара в платформе", default=None)
    name_platform: Optional[str] = Field(title="Наименование товара в платформе", default=None)
    chrtId: int
    article: Optional[str] = None
    isLargeCargo: Optional[bool] = None
    supplierStatus: Optional[str] = None
    wbStatus: Optional[str] = None
    nomenclature: Optional[str] = None
    transfer_to_platform: Optional[bool] = Field(default=True)
    all_products_matched_to_platform: bool = Field(default=False)
    # Дополнительные поля в которые инфа берется из метода заказы(Статистика)
    discountPercent: Optional[int] = Field(
        title="Согласованный итоговый дисконт",
        description="Будучи примененным к totalPrice, даёт сумму к оплате",
        default=None,
    )
    spp: Optional[float] = Field(description="Скидка WB", default=None)
    finishedPrice: Optional[float] = Field(
        description="Фактическая цена с учетом всех скидок (к взиманию с покупателя)", default=None
    )
    priceWithDisc: Optional[float] = Field(
        description="Цена со скидкой продавца, от которой считается сумма "
        "к перечислению продавцу forPay "
        "(= totalPrice * (1 - discountPercent/100))",
        default=None,
    )
    statistics: Optional[dict] = Field(
        description="Поле для хранения json данных с метода статистика по заказу.", default=None
    )
    sales: Optional[dict] = Field(description="Поле для хранения json данных с метода продаж.", default=None)
    sales_report: Optional[dict] = Field(
        description="Поле для хранения json данных с метода отчёта продаж.", default=None
    )

    def get_status(self):
        if self.wbStatus == StatusOrderWildberries.SOLD:
            return self.wbStatus
        if self.wbStatus in (
            StatusOrderWildberries.DECLINED_BY_CLIENT,
            StatusOrderWildberries.CANCELED_BY_CLIENT,
            StatusOrderWildberries.CANCELED,
        ):
            return StatusOrderWildberries.CANCEL

        if self.supplierStatus in (
            StatusOrderWildberries.NEW,
            StatusOrderWildberries.COMPLETE,
            StatusOrderWildberries.CONFIRM,
            StatusOrderWildberries.CANCEL,
        ):
            return self.supplierStatus

        # TODO Необходима обработка если нет данных от WB
        return "ERROR"

    def args_for_insert_row(self, company_id: int, marketplace_id: int) -> tuple:
        return (
            str(self.rid),  # id_mp
            self.createdAt,  # date_reg
            str(self.id_order),  # posting_number
            company_id,
            marketplace_id,
            None,  # warehouse_id
            None,  # packaging_info
            None,  # shipment_date
            self.get_status(),  # status,
            str(self.currencyCode),  # currency
            self.convertedPrice // 100,  # total
            self.model_dump_json(),
            "FBS",
            self.transfer_to_platform,
        )

    def args_for_update_row(self, company_id: int, marketplace_id: int) -> tuple:
        return self.args_for_insert_row(company_id, marketplace_id)

    def model_to_platform(self, company_id: int, marketplace_id: int) -> dict:
        return ResponseOrderToPlatform(
            id=1,
            company_id=company_id,
            marketplace_id=marketplace_id,
            total=self.convertedPrice // 100,
            schema="FBS",
            created_at=self.createdAt,
            currency=str(self.currencyCode),
            date_reg=self.createdAt,
            status=self.get_status(),
            posting_number=str(self.id_order),
            id_mp=self.rid,
            json_data=self.model_dump(),
            all_products_matched_to_platform=self.all_products_matched_to_platform,
        ).model_dump()

    @property
    def id(self):
        return self.rid

    @property
    def id_mp(self):
        return self.rid

    @property
    def items_for_line_orders(self):
        return str(self.rid), self.nmId, 1, self.price, self.nomenclature

    @property
    def status(self):
        return self.wbStatus


class WBStock(BaseModel):
    sku: str
    good_id_mp: Optional[int] = Field(description="nmID", default=None)
    amount: int
    warehouse_id: Optional[int] = Field(description="ID склада продавца", default=None)
    trader_schema: Optional[str] = Field(default=None)


class WBSales(BaseModel):
    date: str | datetime = Field(
        description="""
            Дата и время продажи. Это поле соответствует параметру dateFrom в запросе,
            если параметр flag=1. Если часовой пояс не указан, то берется Московское время (UTC+3).
            """
    )
    lastChangeDate: str | datetime = Field(
        description="""
            Дата и время обновления информации в сервисе.
            Это поле соответствует параметру dateFrom в запросе,
            если параметр flag=0 или не указан.
            Если часовой пояс не указан, то берется Московское время (UTC+3).
            """
    )
    warehouseName: Optional[str] = Field(description="Склад отгрузки", default=None)
    countryName: str = Field(description="Страна", default=None)
    oblastOkrugName: str = Field(description="Округ", default=None)
    regionName: str = Field(description="Регион", default=None)
    supplierArticle: str = Field(description="Артикул продавца", default=None)
    nmId: int = Field(description="Артикул WB")
    barcode: str = Field(description="Штрихкод", default=None)
    category: str = Field(description="Категория", default=None)
    subject: str = Field(description="Предмет", default=None)
    brand: str = Field(description="Предмет", default=None)
    techSize: str = Field(description="Размер товара", default=None)
    incomeID: int = Field(description="Номер поставки")
    isSupply: bool = Field(description="Договор поставки")
    isRealization: bool = Field(description="Договор реализации")
    totalPrice: float = Field(description="Цена без скидок")
    discountPercent: int = Field(description="Скидка продавца")
    spp: float = Field(description="Скидка WB")
    forPay: float = Field(description="К перечислению продавцу")
    finishedPrice: float = Field(description="Фактическая цена с учетом всех скидок (к взиманию с покупателя)")
    priceWithDisc: float = Field(
        description="Цена со скидкой продавца, от которой считается сумма "
        "к перечислению продавцу forPay "
        "(= totalPrice * (1 - discountPercent/100))"
    )
    saleID: str = Field(description="Уникальный идентификатор продажи/возврата")
    orderType: str = Field(description="Тип заказа")
    sticker: str = Field(description="Идентификатор стикер-значения")
    gNumber: str = Field(description="Номер заказа")
    srid: str = Field(
        description="Уникальный идентификатор заказа."
        "Примечание для использующих API Маркетплейс: "
        "srid равен rid в ответах методов сборочных заданий."
    )

    @property
    def id(self):
        return self.saleID

    @property
    def id_mp(self):
        return self.saleID

    def args_for_insert_row(self, company_id: int, marketplace_id: int) -> tuple:
        return (
            self.saleID,
            self.gNumber,
            self.srid,
            self.model_dump_json(),
            company_id,
            marketplace_id,
        )

    def args_for_update_row(self, company_id: int, marketplace_id: int) -> tuple:
        return self.args_for_insert_row(company_id, marketplace_id)


class WBSalesReportItem(BaseModel):
    realizationreport_id: int
    date_from: str
    date_to: str
    create_dt: str
    suppliercontract_code: Optional[Dict[str, Any]] = None
    rrd_id: int
    gi_id: int
    subject_name: str
    nm_id: int
    brand_name: str
    sa_name: str
    ts_name: str
    barcode: str
    doc_type_name: str
    quantity: int
    retail_price: float
    retail_amount: float
    sale_percent: int
    commission_percent: float
    office_name: Optional[str] = None
    supplier_oper_name: Optional[str]
    order_dt: Optional[datetime] = None
    sale_dt: Optional[datetime] = None
    rr_dt: Optional[str] = None
    shk_id: Optional[int] = None
    retail_price_withdisc_rub: Optional[float] = None
    delivery_amount: Optional[int] = None
    return_amount: Optional[int] = None
    delivery_rub: Optional[float] = None
    gi_box_type_name: Optional[str] = None
    product_discount_for_report: Optional[float] = None
    supplier_promo: Optional[float] = None
    rid: Optional[int] = None
    ppvz_spp_prc: Optional[float] = None
    ppvz_kvw_prc_base: Optional[float] = None
    ppvz_kvw_prc: Optional[float] = None
    sup_rating_prc_up: Optional[float]
    is_kgvp_v2: Optional[float] = None
    ppvz_sales_commission: Optional[float] = None
    ppvz_for_pay: Optional[float] = None
    ppvz_reward: Optional[float] = None
    acquiring_fee: Optional[float] = None
    acquiring_bank: Optional[str] = None
    ppvz_vw: Optional[float] = None
    ppvz_vw_nds: Optional[float] = None
    ppvz_office_id: Optional[int] = None
    ppvz_office_name: Optional[str] = None
    ppvz_supplier_id: Optional[int] = None
    ppvz_supplier_name: Optional[str] = None
    ppvz_inn: Optional[str] = None
    declaration_number: Optional[str] = None
    bonus_type_name: Optional[str] = None
    sticker_id: Optional[str] = None
    site_country: Optional[str] = None
    penalty: Optional[float] = None
    additional_payment: Optional[float] = None
    rebill_logistic_cost: Optional[float] = None
    rebill_logistic_org: Optional[str] = None
    kiz: Optional[str] = None
    srid: Optional[str] = None


class WBSelectedPeriod(BaseModel):
    begin: str = Field(title="Начало периода", description="string <time-date>")
    end: str = Field(title="Конец периода", description="string <time-date>")


class WBOrderSelectedPeriod(BaseModel):
    field: str = Field(title="Виды сортировки", default="openCard")
    mode: str = Field(default="asc")


class ParentSubject(BaseModel):
    subjectId: int = Field(description="Id категории товара")
    subjectName: str = Field(description="Название категории товара")


class ObjectCharacteristics(BaseModel):
    charcID: int = Field(description="Идентификатор характеристики")
    subjectName: str = Field(description="Название предмета")
    subjectID: int = Field(description="Идентификатор предмета")
    name: str = Field(description="Название характеристики")
    required: bool = Field(
        description="true - характеристику необходимо обязательно указать в КТ."
        "false - характеристику не обязательно указывать"
    )
    unitName: Optional[str] = Field(description="Единица измерения", default=None)
    maxCount: Optional[int] = Field(
        description="Максимальное кол-во значений, которое можно присвоить данной характеристике. "
        "Если 0, то нет ограничения.",
        default=0,
    )
    popular: Optional[bool] = Field(
        description="Характеристика популярна у пользователей (true - да, false - нет)",
        default=None,
    )
    charcType: Optional[int] = Field(
        description="Тип характеристики (1 и 0 - строка или массив строк; " "4 - число или массив чисел)",
        default=None,
    )


class ItemListOfObjects(BaseModel):
    subjectID: int = Field(description="Идентификатор предмета")
    parentID: Optional[int] = Field(description="Идентификатор родительской категории", default=None)
    subjectName: str = Field(description="Название предмета")
    parentName: Optional[str] = Field(description="Название родительской категории", default=None)
    isVisible: Optional[bool] = Field(description="Видимость на сайте", default=None)


class WBSizeGoodsBody(BaseModel):
    """
    nmID: Артикул Wildberries
    sizeID: ID размера
    price: Цена
    """

    nmID: int
    sizeID: int
    price: int


class WBFilterSizeObject(BaseModel):
    """Базовая стуктура 'размера' в фильтре товаров."""

    sizeID: int = Field(description="ID размера. В методах контента это поле chrtID")
    price: int = Field(description="Цена")
    discountedPrice: int = Field(description="Цена со скидкой")
    techSizeName: str = Field(description="Размер товара")


class WBFilterGoodsObject(BaseModel):
    """Базовая стуктура 'товара' в фильтре товаров."""

    nmID: int = Field(description="Артикул Wildberries")
    vendorCode: str = Field(description="Артикул продавца")
    sizes: List[WBFilterSizeObject] = Field(description="Размер")
    currencyIsoCode4217: str = Field(description="Валюта, по стандарту ISO 4217")
    discount: int = Field(description="Скидка, %")
    editableSizePrice: bool = Field(
        description="Можно ли устанавливать цены отдельно для разных размеров: true — можно, false — нельзя. Эта возможность зависит от категории товара"
    )


class WBGoodsSizeObject(BaseModel):
    """
    Структура для информации о размере
    """

    nmID: int = Field(description="Артикул Wildberries")
    sizeID: int = Field(
        description="ID размера. Можно получить с помощью метода Получение списка товаров по артикулам, поле sizeID. В методах контента это поле chrtID"
    )
    vendorCode: str = Field(description="Артикул продавца")
    price: int = Field(description="Цена")
    currencyIsoCode4217: str = Field(description="Валюта, по стандарту ISO 4217")
    discountedPrice: float = Field(description="Цена со скидкой")
    discount: int = Field(description="Скидка, %")
    techSizeName: str = Field(description="Размер товара")
    editableSizePrice: bool = Field(
        description="Можно ли устанавливать цены отдельно для разных размеров: true — можно, false — нельзя. Эта возможность зависит от категории товара"
    )


class WBFilterListGoods(BaseModel):
    listGoods: List[WBFilterGoodsObject]


class WBListGoodsSizeObject(BaseModel):
    listGoods: List[WBGoodsSizeObject]


class SupplierTaskMetadataBuffer(BaseModel):
    """Структура объекта с информацией про загрузку в обработке."""

    uploadID: int = Field(description="ID загрузки")
    status: int = Field(description="Статус загрузки: 1 — в обработке")
    uploadDate: str = Field(description="Дата и время, когда загрузка создана")
    activationDate: str = Field(description="Дата и время, когда загрузка отправляется в обработку")

    overAllGoodsNumber: int = Field(description="Всего товаров")
    successGoodsNumber: int = Field(description="Товаров без ошибок (0, потому что загрузка в обработке)")


class MovementType(Enum):
    ARRIVAL = "+"  # Приход
    SPENDING = "-"  # Расход


class ItemMoveStock(BaseModel):
    product_name: Optional[str] = Field(default=None)
    product_id: Optional[int] = Field(title="ID товара в маркете", default=None)
    sku: Optional[str] = Field(title="SKU товара в маркете")
    value: int = Field(title="Значение движения остатка")
    movement: Optional[str] = Field(title="Тип движения", default=MovementType.SPENDING)
    id_order: Optional[Union[str, int]] = Field(title="ID заказа в маркетплейсе")
    id_warehouse: Optional[Union[str, int]] = Field(title="ID склада в маркете", default=None)


class WBStockFBO(BaseModel):
    lastChangeDate: Optional[str] | datetime = Field(
        description="""
            Дата и время обновления информации в сервисе.
            Это поле соответствует параметру dateFrom в запросе,
            если параметр flag=0 или не указан.
            Если часовой пояс не указан, то берется Московское время (UTC+3).
            """,
        default=None,
    )
    warehouseName: Optional[str] = Field(title="Название склада", max_length=50, default=None)
    supplierArticle: Optional[str] = Field(description="Артикул продавца", default=None)
    nmId: Optional[int] = Field(description="Артикул WB", default=None)
    barcode: Optional[str] = Field(description="Штрихкод", default=None)
    quantity: Optional[int] = Field(
        description="Количество, доступное для продажи (сколько можно добавить в корзину)", default=None
    )
    inWayToClient: Optional[int] = Field(description="В пути к клиенту", default=None)
    inWayFromClient: Optional[int] = Field(description="В пути от клиента", default=None)
    quantityFull: Optional[int] = Field(
        description="Полное (непроданное) количество, которое числится за складом (= quantity + в пути)", default=None
    )
    category: Optional[str] = Field(title="Категория", max_length=50, default=None)
    subject: Optional[str] = Field(title="Предмет", max_length=50, default=None)
    brand: Optional[str] = Field(title="Бренд", max_length=50, default=None)
    techSize: Optional[str] = Field(title="Размер товара", max_length=30, default=None)
    Price: Optional[float] = Field(title="Цена", default=None)
    Discount: Optional[float] = Field(title="Скидка", default=None)
    isSupply: Optional[bool] = Field(description="Договор поставки", default=None)
    isRealization: Optional[bool] = Field(description="Договор реализации", default=None)
    SCCode: Optional[str] = Field(description="Код контракта (внутренние технологические данные)", default=None)
    # Поля для платформы
    id_platform: Optional[int] = Field(title="Идентификатор товара в платформе", default=None)
    name_platform: Optional[str] = Field(title="Наименование товара в платформе", default=None)
