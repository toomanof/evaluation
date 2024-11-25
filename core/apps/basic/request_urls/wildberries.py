from core.project.types import URLParameterSchema
from core.apps.basic.types import (
    WBRequestParamsRealizationSalesReport,
    WBRequestBodyCreateSupply,
    WBRequestBodyDeleteWarehouseStocks,
    WBRequestBodyGetWarehouseStocks,
    WBRequestBodyOrdersMetaSGTIN,
    WBRequestBodyOrdersStatus,
    WBRequestBodyUpdateWarehouseStocks,
    WBRequestParamsAddMediaCardProductHeaders,
    WBResponseAddMediaInCardProduct,
    WBResponseCreateCardsProducts,
    WBResponseCreateSupply,
    WBResponseDeleteSupply,
    WBResponseDeleteWarehouseStocks,
    WBResponseError,
    WBResponseGetInfoSupply,
    WBResponseGetSupplies,
    WBResponseGetSupplyOrders,
    WBResponseWarehouseStock,
    WBResponseListCardProducts,
    WBResponseListErrorsNomenclatures,
    WBResponseListNomenclaturesV2,
    WBResponseOrderCancel,
    WBResponseFBSOrders,
    WBResponseOrdersMetaSGTIN,
    WBResponseOrdersStatus,
    WBResponseOrdersStickersExtra,
    WBResponseRealizationSalesReport,
    WBResponseReshipmentOrders,
    WBResponseSupplyAddOrders,
    WBResponseSupplyBarcodeExtra,
    WBResponseSupplyDeliver,
    WBResponseUpdateCardsProducts,
    WBResponseUpdateMediaInCardProduct,
    WBResponseUpdateWarehouseStocks,
    WBResponseListWarehouse,
    WBRequestParamsAddOrderToSupply,
    WBRequestBodyFBSOrders,
    WBRequestBodyFBOOrders,
    WBResponseErrors,
    WBResponseOffices,
    WBRequestParamsWarehouseCreate,
    WBResponseWarehouseCreate,
    WBRequestBodyParamsWarehouseUpdate,
    WBRequestParamsSuppliesV1,
    WBResponseSuppliesV1,
    WBResponseCreateCardsProductsError,
    WBRequestParamsStatisticsForSelectedPeriod,
    WBResponseStatisticsForSelectedPeriod,
    WBResponseFBOOrders,
    WBResponseSales,
    WBRequestParamsSales,
    WBResponseParentSubjects,
    WBRequestListOfObjects,
    WBResponseListOfObjects,
    WBResponseObjectCharacteristics,
    WBRequestObjectCharacteristics,
    WBRequestLocale,
    WBRequestParamsUpdateMediaCardProduct,
    WBRequestParamsExportPricesAndDiscounts,
    WBResponseSetPricesAndDiscounts,
    WBRequestParamsDownloadProcessedStatus,
    WBResponseDownloadProcessedStatus,
    WBRequestParamsLoadDetails,
    WBResponseProcessedLoadDetails,
    WBResponseRawLoadDetails,
    WBRequestBodySizeGoodsPriceUpdate,
    WBResponseListGoodsSize,
    WBResponseFilterListGoods,
    WBResponseRawLoadProgress,
    WBLoadProgressQueryParams,
    WBGoodsSizeQueryParams,
    WBFilterGoodsQueryParams,
    WBRequestBodyOrdersWithParamsStickers,
    WBRequestBodyGetStocksFBO,
    WBResponseWBStockFBO,
    WBResponseWarehouses,
)
from core.apps.constants import (
    VERSION_1,
    VERSION_3,
    VERSION_2,
)
from core.project.constants import (
    SECONDS_IN_MINUTE,
    SECONDS_IN_DAY,
)
from core.project.enums.common import RequestMethod
from core.project.conf import settings


URL_CREATE_CARDS_PRODUCTS_WILDBERRIES_V2 = URLParameterSchema(
    name="CONTENT_V1_CARDS_UPLOAD",
    method=RequestMethod.POST,
    has_cache=False,
    response_schema=WBResponseCreateCardsProducts,
    error_schema=WBResponseCreateCardsProductsError,
    title="Создание КТ",
    positive_response_code=200,
    url=f"/content/v{VERSION_2}/cards/upload",
    url_api_point=settings.API_CONTENT_URL,
)

URL_UPDATE_CARDS_PRODUCTS_WILDBERRIES_V3 = URLParameterSchema(
    name="CONTENT_V1_CARDS_UPDATE",
    method=RequestMethod.POST,
    has_cache=False,
    response_schema=WBResponseUpdateCardsProducts,
    title="Редактирование КТ",
    url=f"/content/v{VERSION_2}/cards/update",
    url_api_point=settings.API_CONTENT_URL,
)

URL_LIST_NOMENCLATURES_WILDBERRIES_V2 = URLParameterSchema(
    name="CONTENT_V1_CARDS_CURSOR_LIST",
    method=RequestMethod.POST,
    has_cache=False,
    response_schema=WBResponseListNomenclaturesV2,
    title="Список НМ",
    timeout=0.8,
    url=f"/content/v{VERSION_2}/get/cards/list",
    url_api_point=settings.API_CONTENT_URL,
    url_sandbox=settings.SANDBOX_API_CONTENT_URL,
)


URL_LIST_ERROR_NOMENCLATURES_WILDBERRIES = URLParameterSchema(
    name="CONTENT_V1_CARDS_ERROR_LIST",
    method=RequestMethod.GET,
    has_cache=False,
    body_schema=WBRequestLocale,
    response_schema=WBResponseListErrorsNomenclatures,
    title="Список несозданных НМ с ошибками",
    url=f"/content/v{VERSION_2}/cards/error/list",
    url_api_point=settings.API_CONTENT_URL,
)


URL_LIST_CARD_PRODUCTS_WILDBERRIES = URLParameterSchema(
    url_api_point=settings.API_CONTENT_URL,
    name="CONTENT_V1_CARDS_FILTER",
    method=RequestMethod.POST,
    url=f"/content/v{VERSION_1}/cards/filter",
    has_cache=False,
    response_schema=WBResponseListCardProducts,
    title="Получение КТ по артикулам продавца",
)


URL_UPDATE_MEDIA_IN_CARD_PRODUCT_WILDBERRIES = URLParameterSchema(
    name="CONTENT_V3_MEDIA_SAVE",
    method=RequestMethod.POST,
    has_cache=False,
    query_schema=None,
    body_schema=WBRequestParamsUpdateMediaCardProduct,
    response_schema=WBResponseUpdateMediaInCardProduct,
    error_schema=WBResponseErrors,
    title="Изменить медиафайлы",
    positive_response_code=200,
    version=VERSION_3,
    url=f"/content/v{VERSION_3}/media/save",
    url_api_point=settings.API_CONTENT_URL,
)


URL_ADD_MEDIA_IN_CARD_PRODUCT_WILDBERRIES = URLParameterSchema(
    name="CONTENT_V1_MEDIA_FILE",
    additional_headers=WBRequestParamsAddMediaCardProductHeaders,
    method=RequestMethod.POST,
    has_cache=False,
    response_schema=WBResponseAddMediaInCardProduct,
    title="Добавление медиа контента в КТ",
    url=f"/content/v{VERSION_1}/media/file",
    url_api_point=settings.API_CONTENT_URL,
)

# TODO: Deprecated
URL_EXPORT_PRICES_WILDBERRIES = URLParameterSchema(
    name="PUBLIC_API_V1_PRICES",
    method=RequestMethod.POST,
    url=f"/public/api/v{VERSION_1}/prices",
    has_cache=False,
    title="Загрузка цен",
)

# TODO: Deprecated
URL_GET_INFO_PRODUCTS_WILDBERRIES = URLParameterSchema(
    name="PUBLIC_API_V1_INFO",
    method=RequestMethod.GET,
    url=f"/public/api/v{VERSION_1}/info",
    has_cache=False,
    title="Получение информации о ценах.",
)


URL_UPDATE_DISCOUNTS_WILDBERRIES = URLParameterSchema(
    name="PUBLIC_API_V1_UPDATE_DISCOUNTS",
    method=RequestMethod.POST,
    url=f"/public/api/v{VERSION_1}/updateDiscounts",
    has_cache=False,
    title="Установка скидок",
)

# TODO: Deprecated
URL_REVOKE_DISCOUNTS_WILDBERRIES = URLParameterSchema(
    name="PUBLIC_API_V1_REVOKE_DISCOUNTS",
    method=RequestMethod.POST,
    url=f"/public/api/v{VERSION_1}/revokeDiscounts",
    has_cache=False,
    title="Сброс скидок для номенклатур",
)


URL_GET_ORDERS_WILDBERRIES_V1 = URLParameterSchema(
    name="API_V1_FBO_ORDERS",
    method=RequestMethod.GET,
    has_cache=True,
    cache_expires_in=SECONDS_IN_MINUTE * 15,
    title="Импорт Заказов FBO",
    body_schema=WBRequestBodyFBOOrders,
    response_schema=WBResponseFBOOrders,
    timeout=70,
    url=f"/api/v{VERSION_1}/supplier/orders",
    url_api_point=settings.API_STATISTICS_URL,
    url_sandbox=settings.SANDBOX_API_STATISTICS_URL,
)


URL_GET_SUPPLIES_WILDBERRIES_V1 = URLParameterSchema(
    title="Импорт поставок из статистики",
    name="API_V1_SUPPLIER_INCOMES",
    has_cache=True,
    body_schema=None,
    response_schema=WBResponseSuppliesV1,
    query_schema=WBRequestParamsSuppliesV1,
    method=RequestMethod.GET,
    sync=False,
    url=f"/api/v{VERSION_1}/supplier/incomes",
    url_api_point=settings.API_STATISTICS_URL,
)


URL_GET_SUPPLIES_WILDBERRIES_V3 = URLParameterSchema(
    name="API_V3_SUPPLIES_GET",
    method=RequestMethod.GET,
    has_cache=False,
    body_schema=None,
    response_schema=WBResponseGetSupplies,
    positive_response_code=200,
    title="Импорт поставок по версии 3",
    version=VERSION_3,
    url=f"/api/v{VERSION_3}/supplies",
    url_api_point=settings.API_MARKETPLACE_URL,
)
"""Возвращает список поставок"""

URL_CREATE_SUPPLY_WILDBERRIES_V3 = URLParameterSchema(
    title="Создание новой поставки Wildberries",
    name="API_V3_SUPPLIES_POST",
    method=RequestMethod.POST,
    has_cache=False,
    body_schema=WBRequestBodyCreateSupply,
    response_schema=WBResponseCreateSupply,
    positive_response_code=201,
    error_schema=WBResponseErrors,
    sync=True,
    version=VERSION_3,
    url=f"/api/v{VERSION_3}/supplies",
    url_api_point=settings.API_MARKETPLACE_URL,
)
"""Создать новую поставку"""

URL_DELIVER_SUPPLY_WILDBERRIES_V3 = URLParameterSchema(
    name="API_V3_SUPPLIES_SUPPLY_DELIVER",
    method=RequestMethod.PATCH,
    has_cache=False,
    body_schema=None,
    response_schema=WBResponseSupplyDeliver,
    positive_response_code=204,
    title="Метод Передачи поставки в доставку",
    version=VERSION_3,
    url=f"/api/v{VERSION_3}/supplies/%s/deliver",
    url_api_point=settings.API_MARKETPLACE_URL,
)


URL_ADD_ORDERS_TO_SUPPLY_WILDBERRIES_V3 = URLParameterSchema(
    name="API_V3_SUPPLIES_SUPPLY_ORDERS_ORDER",
    method=RequestMethod.PATCH,
    has_cache=True,
    cache_expires_in=SECONDS_IN_MINUTE * 15,
    body_schema=WBRequestParamsAddOrderToSupply,
    response_schema=WBResponseSupplyAddOrders,
    positive_response_code=204,
    title="Добавить к поставке сборочное задание",
    version=VERSION_3,
    url=f"/api/v{VERSION_3}/supplies/%s/orders/%s",
    url_api_point=settings.API_MARKETPLACE_URL,
)


URL_GET_BARCODE_SUPPLY_WILDBERRIES_V3 = URLParameterSchema(
    name="API_V3_SUPPLIES_SUPPLY_BARCODE",
    method=RequestMethod.GET,
    has_cache=False,  # NOTE: infrequent case
    body_schema=None,
    response_schema=WBResponseSupplyBarcodeExtra,
    positive_response_code=200,
    title="Получить QR поставки",
    version=VERSION_3,
    url=f"/api/v{VERSION_3}/supplies/%s/barcode",
    url_api_point=settings.API_MARKETPLACE_URL,
)


URL_GET_BARCODE_ORDERS_WILDBERRIES_V3 = URLParameterSchema(
    name="API_V3_ORDERS_STICKERS",
    method=RequestMethod.POST,
    has_cache=False,
    body_schema=WBRequestBodyOrdersWithParamsStickers,
    response_schema=WBResponseOrdersStickersExtra,
    error_schema=WBResponseError,
    positive_response_code=200,
    title="Получить этикетки для сборочных заданий",
    sync=True,
    version=VERSION_3,
    url=f"/api/v{VERSION_3}/orders/stickers",
    url_api_point=settings.API_MARKETPLACE_URL,
)


URL_GET_SUPPLY_ORDERS_WILDBERRIES_V3 = URLParameterSchema(
    name="API_V3_SUPPLIES_SUPPLY_ORDERS",
    method=RequestMethod.GET,
    has_cache=True,
    cache_expires_in=SECONDS_IN_DAY,
    body_schema=None,
    response_schema=WBResponseGetSupplyOrders,
    positive_response_code=200,
    title="Получить сборочные задания в поставке",
    sync=False,
    version=VERSION_3,
    url=f"/api/v{VERSION_3}/supplies/%s/orders",
    url_api_point=settings.API_MARKETPLACE_URL,
)
"""Возвращает сборочные задания, закреплённые за поставкой."""

URL_GET_ORDERS_WILDBERRIES_V3 = URLParameterSchema(
    name="API_V3_FBS_ORDERS",
    method=RequestMethod.GET,
    has_cache=False,
    body_schema=WBRequestBodyFBSOrders,
    response_schema=WBResponseFBSOrders,
    positive_response_code=200,
    title="Импорт Заказов FBS",
    version=VERSION_3,
    url=f"/api/v{VERSION_3}/orders",
    url_api_point=settings.API_MARKETPLACE_URL,
    url_sandbox=settings.API_BASE_URL,
)


URL_GET_NEW_ORDERS_WILDBERRIES_V3 = URLParameterSchema(
    name="API_V3_ORDERS_NEW",
    method=RequestMethod.GET,
    has_cache=False,
    body_schema=None,
    response_schema=WBResponseFBSOrders,
    positive_response_code=200,
    version=VERSION_3,
    url=f"/api/v{VERSION_3}/orders/new",
    url_api_point=settings.API_MARKETPLACE_URL,
)
"""Возвращает список всех новых сборочных заданий у поставщика на данный момент."""

URL_STOCKS_WILDBERRIES_V3 = URLParameterSchema(
    name="API_V3_STOCKS_WAREHOUSE_POST",
    method=RequestMethod.POST,
    has_cache=False,
    body_schema=WBRequestBodyGetWarehouseStocks,
    response_schema=WBResponseWarehouseStock,
    positive_response_code=200,
    title="Остатки товаров на складе",
    version=VERSION_3,
    url=f"/api/v{VERSION_3}/stocks/%s",
    url_api_point=settings.API_MARKETPLACE_URL,
)
"""Возвращает остатки товаров."""

URL_EXPORT_STOCKS_WILDBERRIES_V3 = URLParameterSchema(
    name="API_V3_STOCKS_WAREHOUSE_PUT",
    method=RequestMethod.PUT,
    has_cache=False,
    body_schema=WBRequestBodyUpdateWarehouseStocks,
    response_schema=WBResponseUpdateWarehouseStocks,
    positive_response_code=204,
    title="Обновление остатков товара",
    version=VERSION_3,
    url=f"/api/v{VERSION_3}/stocks/%s",
    url_api_point=settings.API_MARKETPLACE_URL,
)
"""Обновление остатков товара"""

URL_WAREHOUSES_WILDBERRIES_SELLER = URLParameterSchema(
    title="Импорт списка складов продавца",
    name="API_V3_WAREHOUSES",
    method=RequestMethod.GET,
    has_cache=False,
    cache_expires_in=1 if not settings.DEBUG else 0,  # костыль, тк запрос кэшируется на тестах и часть падает в CI
    response_schema=WBResponseListWarehouse,
    version=VERSION_3,
    url=f"/api/v{VERSION_3}/warehouses",
    url_api_point=settings.API_MARKETPLACE_URL,
)
"""Список складов продавца"""

URL_STOCKS_WILDBERRIES_V1 = URLParameterSchema(
    title="Данные статистики по остаткам на складах",
    name="API_V1_SUPPLIER_STOCKS",
    method=RequestMethod.GET,
    has_cache=True,
    query_schema=WBRequestBodyGetStocksFBO,
    response_schema=WBResponseWBStockFBO,
    timeout=61,
    cache_expires_in=SECONDS_IN_MINUTE,
    url=f"/api/v{VERSION_1}/supplier/stocks",
    url_api_point=settings.API_STATISTICS_URL,
    url_sandbox=settings.SANDBOX_API_STATISTICS_URL,
)


URL_SALES_WILDBERRIES_V1 = URLParameterSchema(
    title="Данные статистики продаж",
    name="API_V1_SUPPLIER_SALES",
    method=RequestMethod.GET,
    has_cache=True,
    timeout=61,
    body_schema=WBRequestParamsSales,
    response_schema=WBResponseSales,
    cache_expires_in=SECONDS_IN_MINUTE * 30,
    url=f"/api/v{VERSION_1}/supplier/sales",
    url_api_point=settings.API_STATISTICS_URL,
    url_sandbox=settings.SANDBOX_API_STATISTICS_URL,
)


URL_GET_INFO_SUPPLY_WILDBERRIES_V3 = URLParameterSchema(
    title="Информация о поставке",
    method=RequestMethod.GET,
    has_cache=True,
    body_schema=None,
    response_schema=WBResponseGetInfoSupply,
    positive_response_code=200,
    name="API_V3_SUPPLIES_SUPPLY_GET",
    sync=True,
    version=VERSION_3,
    url=f"/api/v{VERSION_3}/supplies/%s",
    url_api_point=settings.API_MARKETPLACE_URL,
)
"""Возвращает информацию о поставке"""

URL_DELETE_SUPPLY_WILDBERRIES_V3 = URLParameterSchema(
    title="Удаление активной поставки без сборочных заданий",
    name="API_V3_SUPPLIES_SUPPLY_DELETE",
    method=RequestMethod.DELETE,
    has_cache=False,
    body_schema=None,
    response_schema=WBResponseDeleteSupply,
    positive_response_code=204,
    sync=True,
    version=VERSION_3,
    url=f"/api/v{VERSION_3}/supplies/%s",
    url_api_point=settings.API_MARKETPLACE_URL,
)
"""Удаляет поставку, если она активна и за ней не закреплено ни одно сборочное задание."""

URl_ORDERS_RESHIPMENT_WILDBERRIES_V3 = URLParameterSchema(
    name="API_V3_SUPPLIES_ORDERS_RESHIPMENT",
    method=RequestMethod.GET,
    has_cache=False,  # NOTE: infrequent case
    body_schema=None,
    response_schema=WBResponseReshipmentOrders,
    positive_response_code=200,
    version=VERSION_3,
    url=f"/api/v{VERSION_3}/supplies/orders/reshipment",
    url_api_point=settings.API_MARKETPLACE_URL,
)
"""Возвращает все сборочные задания, требующие повторной отгрузки."""

URL_DELETE_STOCKS_WILDBERRIES_V3 = URLParameterSchema(
    name="API_V3_STOCKS_WAREHOUSE_DELETE",
    method=RequestMethod.DELETE,
    has_cache=False,
    body_schema=WBRequestBodyDeleteWarehouseStocks,
    response_schema=WBResponseDeleteWarehouseStocks,
    version=VERSION_3,
    url=f"/api/v{VERSION_3}/stocks/%s",
    url_api_point=settings.API_MARKETPLACE_URL,
)


URL_CANCEL_ORDER_WILDBERRIES_V3 = URLParameterSchema(
    title="Отмена сборочного задания",
    name="API_V3_ORDERS_ORDER_CANCEL",
    method=RequestMethod.PATCH,
    has_cache=False,
    body_schema=None,
    response_schema=WBResponseOrderCancel,
    positive_response_code=204,
    url=f"/api/v{VERSION_3}/orders/%s/cancel",
    url_api_point=settings.API_MARKETPLACE_URL,
)
"""Переводит сборочное задание в статус cancel ("Отменено поставщиком")."""

URL_GET_ORDERS_STATUS_WILDBERRIES_V3 = URLParameterSchema(
    title="Импорт статусов FBS заказов",
    name="API_V3_ORDERS_STATUS",
    method=RequestMethod.POST,
    has_cache=False,
    cache_expires_in=SECONDS_IN_MINUTE * 15,
    body_schema=WBRequestBodyOrdersStatus,
    response_schema=WBResponseOrdersStatus,
    positive_response_code=200,
    version=VERSION_3,
    url=f"/api/v{VERSION_3}/orders/status",
    url_api_point=settings.API_MARKETPLACE_URL,
)


URL_ORDERS_META_SERIALISED_GLOBAL_TRADE_ITEM_NUMBER = URLParameterSchema(
    name="API_V3_ORDERS_ORDER_META_SERIALISED_GLOBAL_TRADE_ITEM_NUMBER",
    method=RequestMethod.POST,
    has_cache=False,
    body_schema=WBRequestBodyOrdersMetaSGTIN,
    response_schema=WBResponseOrdersMetaSGTIN,
    positive_response_code=204,
    title="Закрепить за сборочным заданием КиЗ (маркировку Честного знака)",
    version=VERSION_3,
    url=f"/api/v{VERSION_3}/orders/%s/meta/{'#sgtin'[1:]}",
    url_api_point=settings.API_MARKETPLACE_URL,
)


URL_REALIZATION_SALES_REPORT = URLParameterSchema(
    title="Realization Sales Report",
    name="API_V1_SUPPLIER_REPORT_DETAIL_BY_PERIOD",
    method=RequestMethod.GET,
    has_cache=False,
    body_schema=WBRequestParamsRealizationSalesReport,
    response_schema=WBResponseRealizationSalesReport,
    positive_response_code=200,
    sync=False,
    url="/api/v5/supplier/reportDetailByPeriod",
    url_api_point=settings.API_STATISTICS_URL,
)

URL_OFFICES_WILDBERRIES_V3 = URLParameterSchema(
    title="Список складов WB",
    name="API_V3_OFFICES",
    method=RequestMethod.GET,
    has_cache=True,
    body_schema=None,
    response_schema=WBResponseOffices,
    positive_response_code=200,
    sync=False,
    version=VERSION_3,
    url=f"/api/v{VERSION_3}/offices",
    url_api_point=settings.API_MARKETPLACE_URL,
)

URL_WAREHOUSE_CREATE_WILDBERRIES_SELLER = URLParameterSchema(
    title="Создать склад продавца",
    name="API_V3_WAREHOUSES_POST",
    method=RequestMethod.POST,
    has_cache=False,
    body_schema=WBRequestParamsWarehouseCreate,
    response_schema=WBResponseWarehouseCreate,
    positive_response_code=201,
    sync=True,
    url=f"/api/v{VERSION_3}/warehouses",
    url_api_point=settings.API_MARKETPLACE_URL,
)

URL_WAREHOUSE_UPDATE_WILDBERRIES_SELLER = URLParameterSchema(
    title="Обновить склад продавца",
    name="API_V3_WAREHOUSES_PUT",
    method=RequestMethod.PUT,
    has_cache=False,
    body_schema=WBRequestBodyParamsWarehouseUpdate,
    response_schema=None,
    positive_response_code=204,
    sync=True,
    url=f"/api/v{VERSION_3}/warehouses/%s",
    url_api_point=settings.API_MARKETPLACE_URL,
)

URL_WAREHOUSE_DELETE_WILDBERRIES_SELLER = URLParameterSchema(
    title="Удалить склад продавца",
    name="API_V3_WAREHOUSES_DELETE",
    method=RequestMethod.DELETE,
    has_cache=False,
    body_schema=None,
    response_schema=None,
    positive_response_code=204,
    sync=True,
    url=f"/api/v{VERSION_3}/warehouses/%s",
    url_api_point=settings.API_MARKETPLACE_URL,
)

URL_STATISTICS_FOR_SELECTED_PERIOD = URLParameterSchema(
    title="Получение статистики КТ за выбранный период, по nmID/предметам/брендам/тегам",
    name="API_STATISTICS_FOR_SELECTED_PERIOD",
    method=RequestMethod.POST,
    has_cache=False,
    body_schema=WBRequestParamsStatisticsForSelectedPeriod,
    response_schema=WBResponseStatisticsForSelectedPeriod,
    error_schema=WBResponseErrors,
    positive_response_code=200,
    sync=True,
    url=f"/content/v{VERSION_1}/analytics/nm-report/detail",
    url_api_point=settings.API_STATISTICS_URL,
)

URL_PARENT_SUBJECTS = URLParameterSchema(
    title="Родительские категории товаров",
    name="API_PARENT_SUBJECTS",
    method=RequestMethod.GET,
    has_cache=True,
    response_schema=WBResponseParentSubjects,
    error_schema=WBResponseErrors,
    positive_response_code=200,
    url="/api/v1/parent-subjects",
    url_api_point=settings.API_FEEDBACKS_URL,
)

URL_LIST_OF_OBJECTS = URLParameterSchema(
    title="Список предметов",
    name="API_LIST_OF_OBJECTS",
    method=RequestMethod.GET,
    has_cache=True,
    body_schema=WBRequestListOfObjects,
    response_schema=WBResponseListOfObjects,
    error_schema=WBResponseErrors,
    positive_response_code=200,
    url="/content/v2/object/all",
    url_api_point=settings.API_CONTENT_URL,
)


URL_OBJECT_CHARACTERISTICS = URLParameterSchema(
    title="Характеристики предмета",
    name="API_OBJECT_CHARACTERISTICS",
    method=RequestMethod.GET,
    has_cache=True,
    body_schema=WBRequestObjectCharacteristics,
    response_schema=WBResponseObjectCharacteristics,
    error_schema=WBResponseErrors,
    positive_response_code=200,
    url="/content/v2/object/charc" "s/%s",
    url_api_point=settings.API_CONTENT_URL,
)

URL_EXPORT_PRICES_AND_DISCOUNTS = URLParameterSchema(
    title="Установить цены и скидки",
    name="API_EXPORT_PRICES_AND_DISCOUNTS",
    method=RequestMethod.POST,
    body_schema=WBRequestParamsExportPricesAndDiscounts,
    response_schema=WBResponseSetPricesAndDiscounts,
    error_schema=WBResponseErrors,
    positive_response_code=200,
    timeout=1,
    url="/api/v2/upload/task",
    url_api_point=settings.API_PRICES_URL,
    url_sandbox=settings.SANDBOX_API_PRICES_URL,
)

URL_DOWNLOAD_PROCESSED_STATUS = URLParameterSchema(
    title="Состояние обработанной загрузки",
    name="API_DOWNLOAD_PROCESSED_STATUS",
    method=RequestMethod.GET,
    body_schema=WBRequestParamsDownloadProcessedStatus,
    response_schema=WBResponseDownloadProcessedStatus,
    error_schema=WBResponseErrors,
    positive_response_code=200,
    timeout=1,
    url="/api/v2/history/tasks",
    url_api_point=settings.API_PRICES_URL,
    url_sandbox=settings.SANDBOX_API_PRICES_URL,
)

URL_PROCESSED_LOAD_DETAILS = URLParameterSchema(
    title="Детализация обработанной загрузки",
    name="API_PROCESSED_LOAD_DETAILS",
    method=RequestMethod.GET,
    body_schema=WBRequestParamsLoadDetails,
    response_schema=WBResponseProcessedLoadDetails,
    error_schema=WBResponseErrors,
    positive_response_code=200,
    timeout=1,
    url="/api/v2/history/goods/task",
    url_api_point=settings.API_PRICES_URL,
    url_sandbox=settings.SANDBOX_API_PRICES_URL,
)

URL_RAW_LOAD_DETAILS = URLParameterSchema(
    title="Детализация необработанной загрузки",
    name="API_RAW_LOAD_DETAILS",
    method=RequestMethod.GET,
    body_schema=WBRequestParamsLoadDetails,
    response_schema=WBResponseRawLoadDetails,
    error_schema=WBResponseErrors,
    positive_response_code=200,
    timeout=1,
    url="/api/v2/buffer/goods/task",
    url_api_point=settings.API_PRICES_URL,
    url_sandbox=settings.SANDBOX_API_PRICES_URL,
)

URL_RAW_LOAD_PROGRESS = URLParameterSchema(
    title="Состояние необработанной загрузки",
    name="API_RAW_LOAD_PROGRESS",
    method=RequestMethod.GET,
    body_schema=WBLoadProgressQueryParams,
    response_schema=WBResponseRawLoadProgress,
    error_schema=WBResponseErrors,
    positive_response_code=200,
    timeout=1,
    url=f"/api/v{VERSION_2}/buffer/tasks",
    url_api_point=settings.API_PRICES_URL,
    url_sandbox=settings.SANDBOX_API_PRICES_URL,
)


URL_SIZE_GOODS_PRICE_UPDATE = URLParameterSchema(
    title="Установить цены отдельно для размеров",
    name="API_V2_TASK_SIZE_POST",
    method=RequestMethod.POST,
    has_cache=False,
    body_schema=WBRequestBodySizeGoodsPriceUpdate,
    response_schema=WBResponseError,
    positive_response_code=200,
    url=f"/api/v{VERSION_2}/upload/task/size",
    url_api_point=settings.API_PRICES_URL,
    url_sandbox=settings.SANDBOX_API_PRICES_URL,
)


URL_LIST_GOODS_SIZE = URLParameterSchema(
    title="Получить цены и скидки по размерам товара",
    name="API_V2_LIST_GOODS_SIZE",
    method=RequestMethod.GET,
    has_cache=False,
    body_schema=WBGoodsSizeQueryParams,
    response_schema=WBResponseListGoodsSize,
    positive_response_code=200,
    url=f"/api/v{VERSION_2}/list/goods/size/nm",
    url_api_point=settings.API_PRICES_URL,
    url_sandbox=settings.SANDBOX_API_PRICES_URL,
)


URL_LIST_GOODS_FILTER = URLParameterSchema(
    title="Получить товары",
    name="API_V2_LIST_GOODS_FILTER",
    method=RequestMethod.GET,
    has_cache=False,
    body_schema=WBFilterGoodsQueryParams,
    response_schema=WBResponseFilterListGoods,
    positive_response_code=200,
    url=f"/api/v{VERSION_2}/list/goods/filter",
    url_api_point=settings.API_PRICES_URL,
    url_sandbox=settings.SANDBOX_API_PRICES_URL,
)

URL_WAREHOUSES_FBO_WILDBERRIES_V1 = URLParameterSchema(
    title="Список складов WB",
    name="API_V1_WAREHOUSES",
    method=RequestMethod.GET,
    has_cache=True,
    body_schema=None,
    response_schema=WBResponseWarehouses,
    positive_response_code=200,
    sync=False,
    version=VERSION_3,
    url=f"/api/v{VERSION_1}/warehouses",
    url_api_point=settings.API_SUPPLIES_URL,
)
