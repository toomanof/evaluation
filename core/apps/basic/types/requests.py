import json

from datetime import datetime
from typing import (
    List,
    Literal,
    Optional,
    Collection,
)

from pandas import to_datetime, NaT
from pydantic import (
    BaseModel,
    Field,
    PrivateAttr,
    conlist,
    ValidationInfo,
    field_validator,
)
from typing_extensions import TypedDict
from .types import (
    WBSizeGoodsBody,
    WBSelectedPeriod,
    WBOrderSelectedPeriod,
    ListBaseModel,
    WBCursorNomenclatureV2,
    WBFilterNomenclature,
    WBSortNomenclature,
    WBCreateCardProductSize,
    WbNmID,
    WBCardProductSize,
    WBDimensions,
    WBCharacteristicValue,
    BarcodeType,
)
from .query_params import WBOrdersStickersQueryParams


def encode_datetime(value):
    return value.isoformat(timespec="seconds")


def validate_datetime(value):
    value = to_datetime(value, errors="coerce")
    if value is NaT:
        raise ValueError("can't parse datetime")
    return value.to_pydatetime()


class WBRequestParamsAddOrderToSupply(BaseModel):
    supply_id: int
    order_id: int


class WBRequestParamsSuppliesV1(BaseModel):
    dateFrom: str
    """
    Дата в формате RFC3339. Можно передать дату или дату со временем.
    Время можно указывать с точностью до секунд или миллисекунд. Литера Z в конце строки означает,
    что время передается в UTC-часовом поясе. При ее отсутствии время считается в часовом поясе МСК (UTC+3).
    """


class WBRequestParamsUpdateDiscount(BaseModel):
    """
    Структура параметра запроса установка скидок.
    """

    discount: int
    """
    Размер скидки
    """
    nm: int
    """
    Артикул WB
    """


class WBRequestListParamsUpdateDiscount(ListBaseModel):
    root: list[WBRequestParamsUpdateDiscount]


class WBRequestParamsSortListNomenclatures(BaseModel):
    """
    Структура параметра запроса списка номенклатуры.
    """

    limit: int = Field(ge=1000)
    """
    Максимальное кол-во карточек, которое необходимо вывести. (Максимальное значение - 1000, по умолчанию 10)
    """

    offset: int = 0
    """
    Смещение от начала списка с указанными критериями поиска и сортировки.
    """

    searchValue: Optional[str] = None
    """
    Значение для поиска. Всегда строка. Поиск работает по номенклатурам, артикулам и бар-кодам.
    """

    sortColumn: Optional[str] = None
    """
    Выбор параметра для сортировки. По умолчанию updateAt desc - дата обновления по убыванию.
    Доступен так же параметр сортировки - hasPhoto
    """

    ascending: bool = False
    """
    Направление сортировки. True - по возрастанию, False - по убыванию.
    """


class WBRequestParamsListNomenclaturesV2(BaseModel):
    """
    Структура параметра запроса списка номенклатуры по второй версии.
    """

    cursor: Optional[WBCursorNomenclatureV2] = None
    filter: Optional[WBFilterNomenclature] = None
    sort: Optional[WBSortNomenclature] = None


class WBRequestParamsListNomenclatures(BaseModel):
    """
    Структура параметра метода получения списка созданных НМ.
    """

    settings: WBRequestParamsListNomenclaturesV2


class WBRequestParamsListCardProducts(BaseModel):
    """
    Структура параметра запроса получение КТ по вендор кодам (артикулам).

    vendorCodes: list[str] -
        Массив идентификаторов НМ поставщика.
        Максимальное количество в запросе 100.
    allowedCategoriesOnly: bool -
        true - показать КТ только из разрешенных к реализации категорий
        false - показать КТ из всех категорий

    """

    vendorCodes: conlist(str, min_length=1, max_length=100)
    allowedCategoriesOnly: bool = Field(default=True)


class WBRequestParamsListStock(BaseModel):
    """
    Структура параметра запроса для получения списка товаров поставщика с их остатками, возвращаемая WB.
    """

    search: Optional[str]
    """
    Поиск по всем полям таблицы.
    """

    skip: int
    """
    Сколько записей пропустить (для пагинации).
    """

    take: int
    """
    Сколько записей выдать (для пагинации).
    """


class WBRequestParamsGetPrice(BaseModel):
    """
    Структура параметра запроса получение информации по номенклатурам, их ценам, скидкам и промокодам.
    Если не указывать фильтры, вернётся весь товар.
    """

    quantity: int = Field(ge=0, le=2, default=0)
    """
    Возможные варианты:
    0 - товар с любым остатком
    1 - товар с ненулевым остатком
    2 - товар с нулевым остатком
    """


class WBRequestParamsCreateCardsProducts(BaseModel):
    """
    Структура параметра запроса создание КТ.

    Создание карточки товара происходит асинхронно,
    при отправке запроса на создание КТ ваш запрос становится
    в очередь на создание КТ.
    ПРИМЕЧАНИЕ: Карточка товара считается созданной,
    если успешно создалась хотя бы одна НМ.
    ВАЖНО: Если во время обработки запроса в очереди выявляются ошибки,
    то НМ считается ошибочной.
    Если запрос на создание прошел успешно, а карточка не создалась,
    то необходимо в первую очередь проверить наличие карточки
    в методе cards/error/list.
    Если карточка попала в ответ к этому методу, то необходимо исправить
    описанные ошибки в запросе на создание карточки и отправить его повторно.
    """

    vendorCode: str
    """
    Артикул новой НМ которую хотим создать в КТ
    """

    characteristics: Optional[list[dict]] = None
    """
    Массив характеристик, индивидуальный для каждой категории
    """

    sizes: Optional[list[WBCreateCardProductSize]] = None
    """
    Массив размеров для номенклатуры
    (для безразмерного товара все равно нужно передавать данный массив с одним элементом и пустым Рос. размером,
    но с ценой и бар-кодом)
    """


class WBRequestListParamsCreateCardsProducts(ListBaseModel):
    root: list[WBRequestParamsCreateCardsProducts]


class WBRequestParamsUpdateCardsProducts(BaseModel):
    """
    Структура параметра запроса создание КТ.

    Создание карточки товара происходит асинхронно,
    при отправке запроса на создание КТ ваш запрос становится
    в очередь на создание КТ.
    ПРИМЕЧАНИЕ: Карточка товара считается созданной,
    если успешно создалась хотя бы одна НМ.
    ВАЖНО: Если во время обработки запроса в очереди выявляются ошибки,
    то НМ считается ошибочной.
    Если запрос на создание прошел успешно, а карточка не создалась,
    то необходимо в первую очередь проверить наличие карточки
    в методе cards/error/list.
    Если карточка попала в ответ к этому методу, то необходимо исправить
    описанные ошибки в запросе на создание карточки и отправить его повторно.
    """

    imtID: int
    """
    Идентификатор карточки товара
    """

    nmID: WbNmID
    """
    Числовой идентификатор номенклатуры Wildberries
    """

    vendorCode: str
    """
    Вендор код, текстовый идентификатор номенклатуры поставщика
    """

    characteristics: Optional[list[dict]] = None
    """
    Массив характеристик, индивидуальный для каждой категории
    """

    sizes: Optional[list[WBCardProductSize]] = None
    """
    Массив размеров для номенклатуры
    (для безразмерного товара все равно нужно передавать данный массив с одним элементом и пустым Рос. размером,
    но с ценой и бар-кодом)
    """

    mediaFiles: Optional[list[str]] = None


class WBRequestParamsUpdateMediaCardProduct(BaseModel):
    """
    Структура параметров в запросе обновления медиафайлов номенклатуры
    """

    # nmID: str = Field(title="Артикул Wildberries")
    nmId: int = Field(title="Артикул Wildberries")

    # !!!: Определение nmID из документации не соответствует используемому в методе API
    """
    12.03.2024
    "Failed to deserialize the JSON body into the target type: missing field `nmId` at line 6 column 1"
    "Failed to deserialize the JSON body into the target type: nmId: invalid type: string \"216398244\",
     expected i64 at line 2 column 21"
    """

    data: Optional[list[str]] = Field(
        title="Ссылки на изображения в том порядке, в котором они будут на карточке товара",
        description="Array of strings",
        default=None,
    )
    # NOTE: В новых методах загрузки, добавления медиафайлов используется артикул Wildberries вместо артикула продавца
    # NOTE: Старые методы перестанут работать 15 марта


class WBRequestParamsAddMediaCardProductHeaders(BaseModel):
    """
    Дополнительные заголовки запроса добавление медиа контента КТ.
    """

    XVendorCode: str = Field(alias="X-Vendor-Code")
    XPhotoNumber: str = Field(alias="X-Photo-Number")
    ContentType: str = Field(alias="Content-type", default="multipart/form-data")
    upload_file_uri: Optional[str]

    class Config:
        populate_by_name = True


class WBRequestBodyCreateSupply(BaseModel):
    """
    Тело запроса создания новой поставки
    """

    _version: int = PrivateAttr(default=3)

    name: str = Field(
        ...,
        max_length=128,  # NOTE: constraint from documentation
        min_length=0,  # NOTE: constraint from documentation not correspond to the reality
    )


class WBRequestBodyListSupplies(BaseModel):
    """
    Структура параметра запроса списка поставок
    """

    limit: int
    """
    Параметр пагинации. Устанавливает предельное количество возвращаемых данных.
    """

    next: int
    """
    Параметр пагинации. Устанавливает значение, с которого надо получить следующий пакет данных.
    Для получения полного списка данных должен быть равен 0 в первом запросе.
    """


class WBRequestBodyFBOOrders(BaseModel):
    """
    Структура параметра запроса списка FBO заказов (сборочных заданий)
    """

    dateFrom: str
    """
    Дата в формате RFC3339. Можно передать дату или дату со временем.
    Время можно указывать с точностью до секунд или миллисекунд. Литера Z в конце строки означает,
    что время передается в UTC-часовом поясе. При ее отсутствии время считается в часовом поясе МСК (UTC+3).
    """
    flag: int = Field(default=0)
    """
    Если параметр flag=0 (или не указан в строке запроса), при вызове API возвращаются данные,
    у которых значение поля lastChangeDate (дата время обновления информации в сервисе) больше или равно
    переданному значению параметра dateFrom. При этом количество возвращенных строк данных варьируется
    в интервале от 0 до примерно 100 000.
    Если параметр flag=1, то будет выгружена информация обо всех заказах или продажах с датой,
    равной переданному параметру dateFrom (в данном случае время в дате значения не имеет).
    При этом количество возвращенных строк данных будет равно количеству всех заказов или продаж,
    сделанных в указанную дату, переданную в параметре dateFrom.
    """


class WBRequestBodyFBSOrders(BaseModel):
    """
    Структура параметра запроса списка FBS заказов (сборочных заданий)
    """

    limit: int
    """
    Параметр пагинации. Устанавливает предельное количество возвращаемых данных.
    """

    next: int
    """
    Параметр пагинации. Устанавливает значение, с которого надо получить следующий пакет данных.
    Для получения полного списка данных должен быть равен 0 в первом запросе.
    """

    dateFrom: Optional[int]
    """
    Дата начала периода в формате Unix timestamp. Необязательный параметр.
    """

    dateTo: Optional[int]
    """
    Дата конца периода в формате Unix timestamp. Необязательный параметр.
    """


class WBRequestBodyOrdersStatus(BaseModel):
    _version: int = PrivateAttr(default=3)

    orders: conlist(int, min_length=1, max_length=1000)


class WBRequestVariantsCreateProduct(BaseModel):
    brand: Optional[str] = Field(description="Бренд", default=None)
    title: str = Field(description="Наименование товара")
    description: Optional[str] = Field(description="Описание товара.", default=None)
    vendorCode: str = Field(description="Артикул продавца")
    dimensions: Optional[WBDimensions] = Field(
        description="""
        Габариты упаковки товара, единица измерения для каждого товара указана в соответствующей характеристике,
        в ответе метода "Характеристики предмета".
        Если не указать структуру dimensions в запросе, то она сгенерируется системой автоматически
        с нулевыми значениями длины, ширины, высоты""",
        default=None,
    )
    sizes: Optional[list[WBCardProductSize]] = Field(
        description="""
        Array of objects
        Массив с размерами.
        Если для размерного товара (обувь, одежда и др.) не указать этот массив,
        то системой в карточке он будет сгенерирован автоматически с techSize = "A" и wbSize = "1" и штрих-кодом.""",
        default=None,
    )
    characteristics: Optional[list[WBCharacteristicValue]] = Field(
        description="Массив характеристик товара", default=None
    )


class WBRequestParamsCreateCardsProductsV3(BaseModel):
    subjectID: int = Field(description="ID предмета")
    variants: list[WBRequestVariantsCreateProduct] = Field(
        description="Массив вариантов товара. В каждой КТ может быть не более 30 вариантов (НМ)"
    )


class WBRequestItemSetPriceAndDiscount(BaseModel):
    nmID: int = Field(description="Артикул Wildberries")
    price: int = Field(description="Цена")
    discount: int = Field(description="Скидка, %")


class WBRequestParamsExportPricesAndDiscounts(BaseModel):
    data: list[WBRequestItemSetPriceAndDiscount] = Field(max_items=1000)


class WBRequestParamsDownloadProcessedStatus(BaseModel):
    uploadID: int = Field(description="ID загрузки")


class WBRequestParamsLoadDetails(BaseModel):
    limit: int
    offset: int = Field(default=0)
    uploadID: int


class WBRequestParamsGetInfoSupply(BaseModel):
    supply: str


class WBRequestParamsSupplyBarcode(BaseModel):
    supply: str
    type: BarcodeType
    # width: int  # NOTE: deprecated
    # height: int  # NOTE: deprecated


class WBRequestBodyOrdersMetaSGTIN(BaseModel):
    _version: int = PrivateAttr(default=3)

    sgtin: conlist(
        TypedDict(
            "SGTIN",
            {"code": str, "sid": int, "numerator": int, "denominator": int},
        ),
        min_length=1,
        max_length=1000,
    )


class WBRequestBodyOrdersStickers(BaseModel):
    _version: int = PrivateAttr(default=3)

    orders: conlist(int, min_length=1, max_length=100)


class WBRequestBodyOrdersWithParamsStickers(WBOrdersStickersQueryParams):
    """Структура для 'Получить этикетки для сборочных заданий'"""

    _version: int = PrivateAttr(default=3)

    orders: conlist(int, min_length=1, max_length=100)


class WBRequestParamsOrdersStickers(WBRequestBodyOrdersStickers):
    type: BarcodeType
    width: Literal[58, 40]
    height: Literal[40, 30]


class WBRequestBodyGetWarehouseStocks(BaseModel):
    skus: conlist(str, min_length=1, max_length=1000)


class WBRequestBodyGetStocksFBO(BaseModel):
    dateFrom: str


class WBRequestBodyUpdateWarehouseStocks(BaseModel):
    stocks: conlist(TypedDict("Stocks", {"sku": str, "amount": int}))


class DataExportStock(BaseModel):
    warehouse_id: int
    stocks: WBRequestBodyUpdateWarehouseStocks


class WBRequestBodyDeleteWarehouseStocks(BaseModel):
    _version: int = PrivateAttr(default=3)

    skus: conlist(str, min_length=1, max_length=1000)


class WBRequestParamsDeleteSupply(BaseModel):
    supply: str


class WBRequestParamsOrderCancel(BaseModel):
    order: int


class ValidatedDatetime(BaseModel):
    @classmethod
    def validate_datetime(cls, value, _info: ValidationInfo) -> datetime:
        return validate_datetime(value)

    _validations = field_validator("dateFrom", "dateTo", mode="before", check_fields=False)(validate_datetime)


class WBRequestParamsMixin(BaseModel):
    def dict(self, primitives=True, exclude_unset=True, exclude_none=True, **kwargs):
        if primitives:
            d = json.loads(self.model_dump_json(exclude_unset=exclude_unset, exclude_none=exclude_none, **kwargs))
        else:
            d = super().model_dump(exclude_unset=exclude_unset, exclude_none=exclude_none, **kwargs)
        return d


class WBRequestParamsSales(WBRequestParamsMixin, ValidatedDatetime):
    dateFrom: datetime
    flag: Optional[int] = 0

    class Config:
        json_encoders = {datetime: encode_datetime}


class WBRequestParamsSupplierStocks(WBRequestParamsMixin, ValidatedDatetime):
    dateFrom: datetime

    class Config:
        json_encoders = {datetime: encode_datetime}


class WBRequestParamsRealizationSalesReport(WBRequestParamsMixin, ValidatedDatetime):
    _version: int = PrivateAttr(default=1)

    dateFrom: datetime
    limit: Optional[int] = 0
    dateTo: datetime
    rrdid: Optional[int] = 0

    class Config:
        json_encoders = {datetime: encode_datetime}


class WBRequestParamsSupplyOrders(BaseModel):
    supplyId: str


class WBRequestParamsWarehouseCreate(BaseModel):
    name: str = Field(..., max_length=200, min_length=1)  # Имя склада продавца
    officeId: int  # ID склада WB


class WBRequestPathParamsWarehouseUpdate(BaseModel):
    warehouseId: int  # ID склада продавца


class WBRequestBodyParamsWarehouseUpdate(BaseModel):
    name: str = Field(..., max_length=200, min_length=1)  # Имя склада продавца
    officeId: int  # ID склада WB


class WBRequestParamsWarehouseUpdate(WBRequestPathParamsWarehouseUpdate, WBRequestBodyParamsWarehouseUpdate): ...


class WBRequestParamsWarehouseDelete(BaseModel):
    warehouseId: int  # ID склада продавца


class WBRequestParamsStatisticsForSelectedPeriod(BaseModel):
    brandNames: Optional[Collection[str]] = Field(description="Название бренда", default=None)
    objectIDs: Optional[Collection[int]] = Field(description="Идентификатор предмета", default=None)
    tagIDs: Optional[Collection[int]] = Field(description="Идентификатор тега", default=None)
    nmIDs: Optional[Collection[int]] = Field(description="Артикул WB", default=None)
    timezone: Optional[str] = Field(
        title="Временная зона",
        description="Если не указано, то по умолчанию используется Europe/Moscow.",
        default=None,
    )
    period: WBSelectedPeriod = Field(title="Период")
    orderBy: Optional[WBOrderSelectedPeriod] = Field(default=None)
    page: int = Field(title="Страница", default=1)

    class Config:
        arbitrary_types_allowed = True


class WBRequestListOfObjects(BaseModel):
    name: Optional[str] = Field(
        default=None,
        description="Поиск по наименованию предмета (Носки), "
        "поиск работает по подстроке, искать можно на любом"
        "из поддерживаемых языков",
    )
    limit: int = Field(
        description="Ограничение по количеству выдаваемых предметов. Максимум 1000.",
        default=1000,
        le=1000,
    )
    locale: str = Field(
        description="Код языка, на котором будут выданы значения полей ответа "
        "(ru - русский, en - английский, zh - китайский)",
        default="ru",
    )
    offset: int = Field(description="Номер позиции, с которой необходимо получить ответ", default=0)
    parentID: Optional[int] = Field(description="Идентификатор родительской категории предмета.", default=None)


class WBRequestLocale(BaseModel):
    locale: str = Field(
        description="Параметр выбора языка (ru, en, zh) значений полей subjectName, name.",
        default="ru",
    )


class WBRequestObjectCharacteristics(WBRequestLocale):
    subjectId: int = Field(description="Идентификатор предмета")


class WBRequestBodySizeGoodsPriceUpdate(BaseModel):
    """
    Структура для "Установить цены для размеров"
    """

    data: List[WBSizeGoodsBody]
