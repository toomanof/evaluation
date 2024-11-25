import asyncio
import logging
import warnings

from asyncio import Task
from dataclasses import dataclass, field
from typing import Collection, Optional
from warnings import warn

from icecream import ic
from pydantic import ValidationError

from core.apps.basic.request_urls.wildberries import (
    URL_LIST_CARD_PRODUCTS_WILDBERRIES,
    URL_LIST_ERROR_NOMENCLATURES_WILDBERRIES,
    URL_UPDATE_MEDIA_IN_CARD_PRODUCT_WILDBERRIES,
    URL_EXPORT_PRICES_WILDBERRIES,
    URL_UPDATE_DISCOUNTS_WILDBERRIES,
    URL_REVOKE_DISCOUNTS_WILDBERRIES,
    URL_GET_INFO_PRODUCTS_WILDBERRIES,
    URL_PARENT_SUBJECTS,
    URL_LIST_OF_OBJECTS,
    URL_OBJECT_CHARACTERISTICS,
    URL_CREATE_CARDS_PRODUCTS_WILDBERRIES_V2,
    URL_UPDATE_CARDS_PRODUCTS_WILDBERRIES_V3,
    URL_LIST_NOMENCLATURES_WILDBERRIES_V2,
    URL_SIZE_GOODS_PRICE_UPDATE,
    URL_LIST_GOODS_SIZE,
    URL_LIST_GOODS_FILTER,
    URL_EXPORT_PRICES_AND_DISCOUNTS,
)
from core.apps.basic.types import (
    WBListProductInPlatform,
    WBRequestParamsListCardProducts,
    WBCardProduct,
    WBResponseCreateCardsProducts,
    WBResponse,
    WBErrorNomenclature,
    WBResponseListErrorsNomenclatures,
    WBRequestParamsUpdateMediaCardProduct,
    WBProductInPlatform,
    PriceInfo,
    WBResponseGetPriceInfo,
    WBDataListPriceForMS,
    WBDataPriceForMS,
    ParentSubject,
    ItemListOfObjects,
    WBRequestListOfObjects,
    ObjectCharacteristics,
    WBRequestObjectCharacteristics,
    WBRequestLocale,
    WBRequestParamsCreateCardsProductsV3,
    WBRequestVariantsCreateProduct,
    WBNomenclature,
    WBFilterNomenclature,
    WBCursorNomenclatureV2,
    WBRequestParamsListNomenclatures,
    WBRequestParamsListNomenclaturesV2,
    WBRequestItemSetPriceAndDiscount,
    WBRequestParamsExportPricesAndDiscounts,
)
from core.apps.basic.utils import get_vendor_codes, wb_photos_to_list_str
from core.apps.constants import (
    COUNT_ITEMS_ONE_ITERATION_FILTER_CARDS,
    COUNT_ITEMS_ONE_ITERATION_CREATE_OR_UPDATE_CARDS_V2,
    COUNT_ITEMS_ONE_ITERATION_CREATE_CARDS_V3,
    COUNT_ITEMS_ONE_ITERATION_UPDATE_CARDS_V3,
)
from core.project.exceptions import RequestException
from core.project.services.requesters import AppRequester
from core.project.services.requesters.fetcher import Fetcher
from core.project.types import MsgResponseToPlatform
from core.project.utils import execute_async_rest_tasks, url_with_params

logger_error = logging.getLogger("errors")
logger_info = logging.getLogger("info")


def prepare_params_for_request_cards(
    items: Collection[str],
    start_index: int,
    stop_index: int,
    errors: list[dict],
    **additional_params,
):
    items_for_iteration = list(filter(lambda x: bool(x), items[start_index:stop_index]))
    try:
        result = WBRequestParamsListCardProducts(vendorCodes=items_for_iteration).model_dump(
            exclude_unset=True, exclude_none=True
        )
    except ValidationError as err:
        errors.append(WBResponse(error=True, errorText=str(err)).model_dump())
        logger_error.error(err, exc_info=True, stack_info=True)
        raise err
    return result


def prepare_params_for_request_create_cards(
    items: Collection[WBProductInPlatform],
    start_index: int,
    stop_index: int,
    errors: list[dict],
    **additional_params,
):
    result = []

    for item in filter(lambda x: bool(x), items[start_index:stop_index]):
        try:
            result.append(
                WBRequestParamsCreateCardsProductsV3(
                    subjectID=item.subjectID,
                    variants=[
                        WBRequestVariantsCreateProduct(
                            brand=item.brand,
                            title=item.title,
                            description=item.description,
                            vendorCode=item.vendorCode,
                            dimensions=item.dimensions,
                            sizes=item.sizes,
                            characteristics=item.characteristics,
                        )
                    ],
                ).model_dump(exclude_unset=True, exclude_none=True)
            )
        except ValidationError as err:
            errors.append(
                WBResponse(
                    data=item.vendorCode,
                    error=True,
                    errorText=str(err),
                ).model_dump()
            )
            logger_error.error(err, exc_info=True, stack_info=True)
            raise err
    return result


def prepare_params_for_request_change_media(
    items: Collection[str],
    start_index: int,
    stop_index: int,
    errors: list[dict],
    **additional_params,
):
    item_single_iteration = [*items][start_index]  # NOTE: Class 'Collection' does not define '__getitem__'
    if not item_single_iteration.nmID or not item_single_iteration.photos:
        return

    try:
        result = WBRequestParamsUpdateMediaCardProduct(
            nmId=item_single_iteration.nmID,
            data=wb_photos_to_list_str(item_single_iteration.photos),
        ).model_dump(exclude_unset=True, exclude_none=True)
    except ValidationError as err:
        errors.append(
            WBResponse(
                data=item_single_iteration.vendorCode,
                error=True,
                errorText=str(err),
            ).model_dump()
        )
        logger_error.error(err, exc_info=True, stack_info=True)
        raise err
    return result


def prepare_params_for_request_export_discounts(
    items: Collection[WBProductInPlatform],
    start_index: int,
    stop_index: int,
    errors: list[dict],
    **additional_params,
):
    result = []
    for item in filter(lambda x: bool(x), items[start_index:stop_index]):
        if (
            item.vendorCode in additional_params.get("vendor_codes_with_error", [])
            or not item.discount
            or not item.nmID
        ):
            continue
        result.append({"nm": item.nmID, "discount": int(item.discount)})
    return result


def prepare_params_for_request_revoke_discounts(
    items: Collection[WBProductInPlatform],
    start_index: int,
    stop_index: int,
    errors: list[dict],
    **additional_params,
):
    items_for_iteration = tuple(filter(lambda x: bool(x), items[start_index:stop_index]))
    result = [
        item.nmID
        for item in items_for_iteration
        if item.vendorCode not in additional_params.get("vendor_codes_with_error", []) and item.nmID
    ]
    return result


def prepare_params_for_request_export_prices(
    items: Collection[WBProductInPlatform],
    start_index: int,
    stop_index: int,
    errors: list[dict],
    **additional_params,
):
    """DEPRECATED."""
    warn("Метод устарел! Теряет силу после 02.04.2024", DeprecationWarning, stacklevel=2)
    result = []
    for item in filter(lambda x: bool(x), items[start_index:stop_index]):
        if item.vendorCode in additional_params.get("vendor_codes_with_error", []) or not item.price or not item.nmID:
            continue
        result.append({"nmId": item.nmID, "price": int(item.price)})
    return result


def prepare_params_for_request_export_prices_and_discounts(
    items: Collection[WBProductInPlatform],
    start_index: int,
    stop_index: int,
    errors: list[dict],
    **additional_params,
):
    result = []
    for item in filter(lambda x: bool(x), items[start_index:stop_index]):
        if item.vendorCode in additional_params.get("vendor_codes_with_error", []) or not item.price or not item.nmID:
            continue
        result.append({"nmID": item.nmID, "price": int(item.price), "discount": int(item.discount)})
    return {"data": result}


def prepare_params_for_request_update_cards(
    items: Collection[WBCardProduct],
    start_index: int,
    stop_index: int,
    errors: list[dict],
    **additional_params,
):
    result = []
    for item in filter(lambda x: bool(x), items[start_index:stop_index]):
        try:
            result.append(item.model_dump(exclude_unset=True, exclude_none=True))
        except ValidationError as err:
            errors.append(
                WBResponse(
                    data=item.vendorCode,
                    error=True,
                    errorText=str(err),
                ).model_dump()
            )
            logger_error.error(err, exc_info=True, stack_info=True)
            raise err
    return result


def select_products_from_info_prices(
    input_products: Collection[WBNomenclature],
    cards_in_markets: Collection[WBNomenclature],
    info_prices: Collection[PriceInfo],
    name_attr: str,
) -> Collection:
    vcs_products = [x.vendorCode for x in input_products]
    slice_cards_in_markets = tuple(
        filter(lambda x: x.vendorCode in vcs_products, cards_in_markets)
    )  # NOTE: Выбираются записи задействованные в работе
    nm_ids = [x.nmID for x in slice_cards_in_markets]
    info_prices = tuple(filter(lambda x: x.nmId in nm_ids, info_prices))
    result = []
    for product in input_products:
        for info_price in info_prices:
            if product.nmID == info_price.nmId and product.discount != getattr(info_price, name_attr):
                result.append(product)
    return result


class NomenclatureRequest(AppRequester):
    async def export_discounts(self) -> list[WBCardProduct]:
        logger_info.info("Export discounts.")
        result = await execute_async_rest_tasks(
            tasks=self.prepare_tasks_for_request_export_discounts(),
            valid_type_positive=str,
            valid_type_error=str,
            errors=[],
        )
        return result

    async def export_prices(self):
        logger_info.info("Export prices.")

        return await execute_async_rest_tasks(
            tasks=self.prepare_tasks_for_request_export_prices(),
            valid_type_positive=str,
            valid_type_error=str,
            errors=[],
        )

    async def export_prices_and_discounts(self):
        logger_info.info("Export prices|discounts.")
        return await execute_async_rest_tasks(
            tasks=self.prepare_tasks_for_request_export_prices_and_discounts(),
            valid_type_positive=str,
            valid_type_error=str,
            errors=[],
        )

    async def fetch_nomenclature(self, vendor_code: Optional[str] = "") -> list[WBNomenclature]:
        result: list[WBNomenclature] = []
        next_request = True
        filter_params = WBFilterNomenclature(withPhoto=-1, textSearch=vendor_code)
        cursor_params = WBCursorNomenclatureV2(limit=COUNT_ITEMS_ONE_ITERATION_FILTER_CARDS)
        while next_request:
            params = WBRequestParamsListNomenclatures(
                settings=WBRequestParamsListNomenclaturesV2(cursor=cursor_params, filter=filter_params)
            )
            response = await self.single_fetch(
                url_params=URL_LIST_NOMENCLATURES_WILDBERRIES_V2,
                params=params.model_dump(exclude_none=True, exclude_unset=True),
                valid_type_negative=WBResponse,
            )

            if not response:
                return []
            if isinstance(response.cards, list):
                result.extend(response.cards)

            next_request = response.cursor.nmID != 0
            # Условие response.cursor.total < COUNT_ITEMS_ONE_ITERATION_FILTER_CARDS не работает!!!
            if next_request:
                cursor_params = WBCursorNomenclatureV2(
                    limit=COUNT_ITEMS_ONE_ITERATION_FILTER_CARDS,
                    updatedAt=response.cursor.updatedAt,
                    nmID=response.cursor.nmID,
                )
        return result

    async def fetch_uncreated_nms_with_errors(self) -> tuple[WBErrorNomenclature]:
        print("Fetching uncreated nms with errors.")
        logger_info.info("Fetching uncreated nms with errors.")
        result = await execute_async_rest_tasks(
            tasks=self.prepare_tasks_for_request_uncreated_nms_with_errors(),
            valid_type_positive=WBResponseListErrorsNomenclatures,
            valid_type_error=WBResponse,
            errors=self.errors,
        )
        result = await self.fetch_uncreated_products(result)
        return result

    async def fetch_prices(self) -> Collection[PriceInfo]:
        return await execute_async_rest_tasks(
            tasks=self.prepare_tasks_for_request_fetch_prices(),
            valid_type_positive=WBResponseGetPriceInfo,
            valid_type_error=WBResponse,
            errors=self.errors,
        )

    def prepare_tasks_for_request_export_discounts(self) -> Collection[Task]:
        """DEPRECATED."""
        warn("Метод устарел! Теряет силу после 02.04.2024", DeprecationWarning, stacklevel=2)
        raise NotImplementedError()

    def prepare_tasks_for_request_export_prices(self) -> Collection[Task]:
        """DEPRECATED."""
        warn("Метод устарел! Теряет силу после 02.04.2024", DeprecationWarning, stacklevel=2)
        raise NotImplementedError()

    def prepare_tasks_for_request_export_prices_and_discounts(self) -> Collection[Task]:
        raise NotImplementedError()

    def prepare_tasks_for_request_fetch_prices(self) -> Collection[Task]:
        return [
            asyncio.create_task(
                Fetcher()(
                    headers=self.request_body.headers,
                    session=self.session,
                    semaphore=self.semaphore,
                    url_params=URL_GET_INFO_PRODUCTS_WILDBERRIES,
                    test=self.test,
                )
            )
        ]

    def prepare_tasks_for_request_uncreated_nms_with_errors(self) -> Collection[Task]:
        return [
            asyncio.create_task(
                Fetcher()(
                    headers=self.request_body.headers,
                    session=self.session,
                    semaphore=self.semaphore,
                    url_params=URL_LIST_ERROR_NOMENCLATURES_WILDBERRIES,
                    test=self.test,
                )
            )
        ]

    def prepare_tasks_for_request_cards(self) -> Collection[Task]:
        warnings.warn(
            "The `prepare_tasks_for_request_cards` method is deprecated",
            DeprecationWarning,
        )
        return self._prepare_tasks_for_cycle_request(
            items=self.vendor_codes,
            count_items_one_iteration=COUNT_ITEMS_ONE_ITERATION_FILTER_CARDS,
            func_prepare_params=prepare_params_for_request_cards,
            url_schema=URL_LIST_CARD_PRODUCTS_WILDBERRIES,
        )

    def prepare_tasks_for_request_revoke_discounts(self) -> Collection[Task]:
        raise NotImplementedError()

    async def revoke_discounts(self):
        logger_info.info("Revoke discounts.")
        return await execute_async_rest_tasks(
            tasks=self.prepare_tasks_for_request_revoke_discounts(),
            valid_type_positive=str,
            valid_type_error=str,
            errors=[],
        )


class ProductRequester(NomenclatureRequest):
    async def _execute(self, class_service):
        service = class_service(
            app=self.app,
            semaphore=self.semaphore,
            session=self.session,
            request_body=self.request_body,
        )

        return await service.execute()

    async def export_products(self):
        """
        Обобщенный метод экспорта списка товаров.
        Returns:
            Возвращает результаты экспорта товаров
        """
        return await self._execute(ExportProductsRequester)

    async def export_prices(self):
        """
        Обобщенный метод экспорта списка товаров.
        Returns:
            Возвращает результаты экспорта цен товаров
        """
        return await self._execute(ExportPriceRequester)

    async def export_prices_v2(self):
        """
        Обобщенный метод экспорта списка товаров с использованием обновленного апи.
        Returns:
            Возвращает результаты экспорта цен товаров
        """
        return await self._execute(ExportPriceRequesterV2)

    async def import_goods_list_by_filter(self) -> Optional[dict]:
        """Получить информацию о товарах.
        Важно!!! В data обязательно передать query_params.

        Пример request_body:
        {
          "headers": {
            "Authorization": "<token>"
          },
          "company_id": 1,
          "marketplace_id": 1,
          "event": "import_goods_list_by_filter",
          "data": {

                  "limit": 10,
                  "offset": 0,
                  "filterNmID": 253
          },
          "callback": "result_import_goods_list_by_filter",
          "event_id": "1",
          "task_id": 1
        }
        """
        try:
            query_params = self._get_query_params_from_request_body(pydantic_schema=URL_LIST_GOODS_FILTER.body_schema)
            response = await self.single_fetch(
                url_params=URL_LIST_GOODS_FILTER,
                params=query_params.model_dump(exclude_none=True),
                valid_type_negative=WBResponse,
            )
        except RequestException:
            return {}
        return response.data.model_dump()


@dataclass
class ExportProductsRequester(NomenclatureRequest):
    """
    Класс выполняющий экспорт товаров по V3.
    """

    vendor_codes_with_error: list[str] = field(default_factory=list)
    vendor_codes: Collection[str] = field(default_factory=list)
    cards_in_markets: Collection[WBNomenclature] = field(default_factory=list)
    info_prices: Collection[PriceInfo] = field(default_factory=list)
    products_for_create_cards: list[WBNomenclature] = field(default_factory=list)
    products_for_update_cards: list[WBNomenclature] = field(default_factory=list)

    def __post_init__(self):
        self.input_data = WBListProductInPlatform.model_validate(self.request_body.data, strict=False).items
        ic(self.input_data)
        self.vendor_codes = get_vendor_codes(self.input_data)

    def adding_changes_to_cards_in_markets(self):
        """
        >>>
        Вносятся изменения в массив данных полученных от маркетплейса
        """

        for item_with_new_data in self.products_for_update_cards:
            collection = filter(
                lambda x: x.vendorCode == item_with_new_data.vendorCode,
                self.cards_in_markets,
            )
            for item_from_market in collection:
                item_with_new_data.nmID = item_from_market.nmID
                item_with_new_data.imtID = item_from_market.imtID
                item_with_new_data.object = item_from_market.object
                item_with_new_data.objectID = item_from_market.objectID
                item_with_new_data.barcodes = None
                index = 0
                for size in item_with_new_data.sizes:
                    size.price = None
                    size.techSize = None
                    size.wbSize = None
                    size.chrtID = item_from_market.sizes[index].chrtID
                    index += 1

        for item in self.input_data:
            collection = filter(
                lambda x: x.vendorCode == item.vendorCode,
                self.cards_in_markets,
            )
            for item_from_market in collection:
                item.nmID = item_from_market.nmID
                item.imtID = item_from_market.imtID
                item.object = item_from_market.object
                item.objectID = item_from_market.objectID

    def cards_to_platform(self):
        return (
            [item for item in self.input_data if item.vendorCode not in self.vendor_codes_with_error]
            if not self.errors
            else []
        )

    async def fetch_uncreated_products(self, uncreated_nms_with_errors: list[WBErrorNomenclature]):
        logger_info.info("Checking creation product card.")
        vcs_products = get_vendor_codes(self.input_data)
        return tuple(
            filter(
                lambda nm: nm.vendorCode in vcs_products,
                uncreated_nms_with_errors,
            )
        )

    def fetch_created_nomenclatures(self):
        vc_cards = [x.vendorCode for x in self.products_for_create_cards]
        return tuple(filter(lambda x: x.vendorCode in vc_cards, self.cards_in_markets))

    async def create_cards_in_markets(self):
        result = []
        if self.products_for_create_cards:
            print("Creating cards in market.")
            logger_info.info("Creating cards in market.")
            await execute_async_rest_tasks(
                tasks=self.prepare_tasks_for_request_create_cards(),
                valid_type_positive=WBResponseCreateCardsProducts,
                valid_type_error=WBResponse,
                errors=self.errors,
            )
            if not self.errors:
                print("Waiting for 20s.")
                logger_info.info("Waiting for 20s.")
                await asyncio.sleep(20)
                print("Create cards in market.")
                self.cards_in_markets = await self.fetch_nomenclature()
                result = self.fetch_created_nomenclatures()
            return result

    async def change_media_content(self):
        if self.input_data:
            logger_info.info("Change media content card.")
            result = await execute_async_rest_tasks(
                tasks=self.prepare_tasks_for_request_change_media(),
                valid_type_positive=WBResponse,
                valid_type_error=WBResponse,
                errors=self.errors,
            )
            return result

    async def fill_list_vendor_codes_with_error(self):
        nms_with_errors = await self.fetch_uncreated_nms_with_errors()
        for item in nms_with_errors:
            self.vendor_codes_with_error.append(item.vendorCode)
            self.errors.append(
                WBResponse(
                    data=item.vendorCode,
                    error=True,
                    errorText=", ".join(item.errors),
                ).model_dump()
            )

    def divide_products_into_created_and_updated(self):
        vendor_codes_in_markets = get_vendor_codes(self.cards_in_markets)

        self.products_for_create_cards = list(
            filter(lambda x: x.vendorCode not in vendor_codes_in_markets, self.input_data)
        )
        self.products_for_update_cards = list(
            filter(lambda x: x.vendorCode in vendor_codes_in_markets, self.input_data)
        )
        # self.products_for_update_cards.extend(self.products_for_create_cards)
        # Не понял зачем тут такое реализовывал!
        # Но оно вызывает ошибку при попытке обновления нового товара

    async def execute(self) -> MsgResponseToPlatform:
        """
        Устарел.
        Основной метод, запускающий все методы по заданному алгоритму.
        1. Сначала существующие карточки необходимо запросить методом cards/filter.
        2. Забираем из ответа массив data.
        3. Фильтруем список products в соответствии с полученными данными,
           создаем два списка на создание КТ и обновления КТ.
        4. В массиве, полученным методом cards/filter, вносим необходимые изменения
           и отправляем его в cards/update
        5. Отфильтрованный массив КТ на создание отправляем в метод cards/upload
        6. Добавление медиа контента в КТ
        7. Загрузка цен.
        8. Повторная загрузка карточек товара с помощью методом cards/filter для получения измененной информации.

        Новый алгоритм.
        1. Получить все карточки /content/v2/get/cards/list
        2. Забираем из ответа массив data.
        3. Фильтруем список products в соответствии с полученными данными,
                   создаем два списка на создание КТ и обновления КТ.
        4. В массиве, полученным методом /content/v2/get/cards/list,
        вносим необходимые изменения и отправляем его в /api/v2/upload/task
        5. Отфильтрованный массив КТ на создание отправляем в метод cards/upload
        6. Добавление медиа контента в КТ
        7. Загрузка цен и скидок для всех объектов из коллекции cards_in_markets
        8. Повторная загрузка карточек товара с помощью методом cards/filter для получения измененной информации.

        Returns:
            Возвращает результаты экспорта товаров
        """
        logger_info.info(f"Start {__class__}.{__name__}")
        print("Start")
        self.cards_in_markets = await self.fetch_nomenclature()
        ic(len(self.cards_in_markets))
        self.divide_products_into_created_and_updated()
        created_nomenclatures = await self.create_cards_in_markets()
        ic(created_nomenclatures)
        self.adding_changes_to_cards_in_markets()
        await self.update_cards_in_markets()

        process_capability = bool(self.products_for_create_cards)
        if process_capability and not self.errors:
            print("Waiting for 5s, before fetch_uncreated_nms_with_errors")
            logger_info.info("Waiting for 5s.")
            await asyncio.sleep(5)
            await self.fill_list_vendor_codes_with_error()
            comparison_set = set(self.vendor_codes_with_error) | set(get_vendor_codes(self.cards_in_markets))
            logger_info.info(
                f"Проверка создания всех товаров"
                f"\n\t{process_capability=}"
                f"\n\t{self.errors=}"
                f"\n\t{self.vendor_codes=}"
                f"\n\t{comparison_set=}"
            )

        if not self.errors:
            await self.change_media_content()
            # TODO: deprecated.
            # self.info_prices = await self.fetch_prices()
            # await self.revoke_discounts()
            await asyncio.sleep(10)
            # await self.export_prices()
            # await self.export_discounts()
            # TODO: добавить новый метод, который устанавливает цену и скидку сразу
            await self.export_prices_and_discounts()

        ic("Exit export product")
        return MsgResponseToPlatform(data=self.cards_to_platform(), errors=self.errors)

    def prepare_tasks_for_request_create_cards(self) -> Collection[Task]:
        result = self._prepare_tasks_for_cycle_request(
            items=self.products_for_create_cards,
            count_items_one_iteration=COUNT_ITEMS_ONE_ITERATION_CREATE_CARDS_V3,
            func_prepare_params=prepare_params_for_request_create_cards,
            url_schema=URL_CREATE_CARDS_PRODUCTS_WILDBERRIES_V2,
        )
        return result

    def prepare_tasks_for_request_update_cards(self) -> Collection[Task]:
        return self._prepare_tasks_for_cycle_request(
            items=self.products_for_update_cards,
            count_items_one_iteration=COUNT_ITEMS_ONE_ITERATION_UPDATE_CARDS_V3,
            func_prepare_params=prepare_params_for_request_update_cards,
            url_schema=URL_UPDATE_CARDS_PRODUCTS_WILDBERRIES_V3,
        )

    def prepare_tasks_for_request_change_media(self) -> Collection[Task]:
        return self._prepare_tasks_for_cycle_request(
            items=self.input_data,
            count_items_one_iteration=1,
            func_prepare_params=prepare_params_for_request_change_media,
            url_schema=URL_UPDATE_MEDIA_IN_CARD_PRODUCT_WILDBERRIES,
        )

    def prepare_tasks_for_request_export_discounts(self) -> Collection[Task]:
        """DEPRECATED."""
        warnings.warn(
            "The `prepare_tasks_for_request_cards` method is deprecated",
            DeprecationWarning,
        )
        items = select_products_from_info_prices(self.input_data, self.cards_in_markets, self.info_prices, "discount")
        if not items:
            return []
        return self._prepare_tasks_for_cycle_request(
            items=items,
            count_items_one_iteration=COUNT_ITEMS_ONE_ITERATION_CREATE_OR_UPDATE_CARDS_V2,
            func_prepare_params=prepare_params_for_request_export_discounts,
            url_schema=URL_UPDATE_DISCOUNTS_WILDBERRIES,
            vendor_codes_with_error=self.vendor_codes_with_error,
        )

    def prepare_tasks_for_request_revoke_discounts(self) -> Collection[Task]:
        """DEPRECATED."""
        items = select_products_from_info_prices(self.input_data, self.cards_in_markets, self.info_prices, "discount")
        if not items:
            return []
        return self._prepare_tasks_for_cycle_request(
            items=items,
            count_items_one_iteration=COUNT_ITEMS_ONE_ITERATION_CREATE_OR_UPDATE_CARDS_V2,
            func_prepare_params=prepare_params_for_request_revoke_discounts,
            url_schema=URL_REVOKE_DISCOUNTS_WILDBERRIES,
            vendor_codes_with_error=self.vendor_codes_with_error,
        )

    def _convert_input_data_to_dict(self, input_data):
        result = dict()
        for item in input_data:
            result[item.nmID] = item
        return result

    def _select_products_data_for_updating_prices(self):
        input_data_dict = self._convert_input_data_to_dict(self.input_data)
        result = list()
        for item in self.cards_in_markets:
            result.append(input_data_dict.get(item.nmID))

        return result

    def prepare_tasks_for_request_export_prices(self) -> Collection[Task]:
        """DEPRECATED."""
        warn("Метод устарел! Теряет силу после 02.04.2024", DeprecationWarning, stacklevel=2)
        items = select_products_from_info_prices(self.input_data, self.cards_in_markets, self.info_prices, "price")
        if not items:
            return []
        return self._prepare_tasks_for_cycle_request(
            items=items,
            count_items_one_iteration=COUNT_ITEMS_ONE_ITERATION_CREATE_OR_UPDATE_CARDS_V2,
            func_prepare_params=prepare_params_for_request_export_prices,
            url_schema=URL_EXPORT_PRICES_WILDBERRIES,
            vendor_codes_with_error=self.vendor_codes_with_error,
        )

    def prepare_tasks_for_request_export_prices_and_discounts(self) -> Collection[Task]:
        items = self._select_products_data_for_updating_prices()

        if not items:
            return []
        return self._prepare_tasks_for_cycle_request(
            items=items,
            count_items_one_iteration=COUNT_ITEMS_ONE_ITERATION_CREATE_OR_UPDATE_CARDS_V2,
            func_prepare_params=prepare_params_for_request_export_prices_and_discounts,
            url_schema=URL_EXPORT_PRICES_AND_DISCOUNTS,
            vendor_codes_with_error=self.vendor_codes_with_error,
        )

    async def update_cards_in_markets(self):
        if self.products_for_update_cards:
            print("Updating cards in markets.")
            logger_info.info("Updating cards in markets.")
            result = await execute_async_rest_tasks(
                tasks=self.prepare_tasks_for_request_update_cards(),
                valid_type_positive=WBResponse,
                valid_type_error=WBResponse,
                errors=self.errors,
            )
            logger_info.info("Waiting for 10s.")
            print("Waiting for 10s.")
            await asyncio.sleep(10)
            return result


@dataclass
class ExportPriceRequester(NomenclatureRequest):
    cards_in_markets: Collection[WBNomenclature] = field(default_factory=list)
    info_prices: Collection[PriceInfo] = field(default_factory=list)
    input_data: list[WBDataPriceForMS] = field(default_factory=list)
    response_data: list[WBDataPriceForMS] = field(default_factory=list)
    vendor_codes: Collection[str] = field(default=None)

    def __post_init__(self):
        self.input_data = WBDataListPriceForMS.model_validate(self.request_body.data, strict=False).items
        self.vendor_codes = get_vendor_codes(self.input_data)

    def check_cards_in_market(self):
        vendors_in_markets = get_vendor_codes(self.cards_in_markets)
        for index, item in enumerate(self.input_data):
            copy_item = item.model_copy(deep=True)
            if item.vendorCode not in vendors_in_markets:
                self.input_data.pop(index)
                copy_item.price = item.old_price
                copy_item.error = f"Товар c артикулом: {item.vendorCode} отсутствует в каталоге Wildberries."

            self.response_data.append(copy_item)

    def set_prices_in_response_data_from_marketplace(self):
        if self.errors:
            for response_item in self.response_data:
                for item in self.info_prices:
                    if response_item.nmID == item.nmId:
                        response_item.price = int(item.price)
                        continue

    async def execute(self):
        self.cards_in_markets = await self.fetch_nomenclature()
        self.check_cards_in_market()
        if self.input_data:
            # TODO: DEPRECATED
            self.info_prices = await self.fetch_prices()
            await self.revoke_discounts()
            await asyncio.sleep(10)
            await self.export_prices()
            await self.export_discounts()

        self.set_prices_in_response_data_from_marketplace()
        return MsgResponseToPlatform(data=self.response_data, errors=self.errors)

    def prepare_tasks_for_request_export_discounts(self) -> Collection[Task]:
        def clean_input_data() -> Collection:
            result = []
            for item in self.input_data:
                f_appended = False
                for price_from_market in self.info_prices:
                    if item.nmID == price_from_market.nmId:
                        f_appended = True
                        if price_from_market.discount:
                            result.append(item)
                        break
                if not f_appended:
                    result.append(item)
            return result

        items = clean_input_data()
        if not items:
            return []
        return self._prepare_tasks_for_cycle_request(
            items=items,
            count_items_one_iteration=COUNT_ITEMS_ONE_ITERATION_CREATE_OR_UPDATE_CARDS_V2,
            func_prepare_params=prepare_params_for_request_export_discounts,
            url_schema=URL_UPDATE_DISCOUNTS_WILDBERRIES,
        )

    def prepare_tasks_for_request_export_prices(self) -> Collection[Task]:
        """DEPRECATED."""
        warn("Метод устарел! Теряет силу после 02.04.2024", DeprecationWarning, stacklevel=2)

        def clean_input_data() -> Collection:
            result = []
            for item in self.input_data:
                f_appended = False
                for price_from_market in self.info_prices:
                    if item.nmID == price_from_market.nmId:
                        f_appended = True
                        if item.price != price_from_market.price:
                            result.append(item)
                        break
                if not f_appended:
                    result.append(item)
            return result

        items = clean_input_data()
        if not items:
            return []

        return self._prepare_tasks_for_cycle_request(
            items=items,
            count_items_one_iteration=COUNT_ITEMS_ONE_ITERATION_CREATE_OR_UPDATE_CARDS_V2,
            func_prepare_params=prepare_params_for_request_export_prices,
            url_schema=URL_EXPORT_PRICES_WILDBERRIES,
        )

    def prepare_tasks_for_request_revoke_discounts(self) -> Collection[Task]:
        def clean_input_data() -> Collection:
            result = []
            for item in self.input_data:
                f_appended = False
                for price_from_market in self.info_prices:
                    if item.nmID == price_from_market.nmId:
                        f_appended = True
                        if price_from_market.discount:
                            result.append(item)
                        break
                if not f_appended:
                    result.append(item)
            return result

        items = clean_input_data()
        if not items:
            return []

        return self._prepare_tasks_for_cycle_request(
            items=items,
            count_items_one_iteration=COUNT_ITEMS_ONE_ITERATION_CREATE_OR_UPDATE_CARDS_V2,
            func_prepare_params=prepare_params_for_request_revoke_discounts,
            url_schema=URL_REVOKE_DISCOUNTS_WILDBERRIES,
        )


@dataclass
class ExportPriceRequesterV2(NomenclatureRequest):
    cards_in_markets: Collection[WBNomenclature] = field(default_factory=list)
    info_prices: Collection[PriceInfo] = field(default_factory=list)
    response_data: list[WBRequestParamsExportPricesAndDiscounts] = field(default_factory=list)
    vendor_codes: Collection[str] = field(default=None)
    _converted_input_data: Collection[str] = field(default_factory=dict)

    def __post_init__(self):
        self.input_data = WBRequestParamsExportPricesAndDiscounts.model_validate(
            self.request_body.data, strict=False
        ).data

    @staticmethod
    def _convert_input_data_to_dict(input_data):
        result = dict()
        for item in input_data:
            result[item.nmID] = item
        return result

    @staticmethod
    def _prepare_params_for_request_export_prices_and_discounts(
        items: Collection[WBRequestItemSetPriceAndDiscount],
        start_index: int,
        stop_index: int,
        errors: list[dict],
        **additional_params,
    ):
        result = list()
        for item in filter(lambda x: bool(x), items[start_index:stop_index]):
            result.append(item.model_dump())
        return {"data": result}

    def check_cards_in_market(self):
        # Собираю словарь, чтобы выполнять проверку за O(1) алгоритмическую сложность
        cards_in_markets_dict = self._convert_input_data_to_dict(self.cards_in_markets)
        for index, item in enumerate(self.input_data):
            if item.nmID not in cards_in_markets_dict:
                self.input_data.pop(index)
                error = f"Товар c id: {item.nmID} отсутствует в каталоге Wildberries."
                self.errors.append({"errorText": error})

    async def fetch_load_progress(self, data, status=1):
        from core.apps.basic.services.handlers.prices_and_discounts import PricesAndDiscountsHandler

        # Используем уже готовый функционал для получения "Состояния обработанной загрузки"
        request_body = self.request_body.model_copy(update={"data": data})
        handler = PricesAndDiscountsHandler(
            app=self.app,
            body=request_body,
        )
        total_objects_count = 0
        #
        while status == 1:
            # Запрашиваем информацию до тех пор, пока статус не поменяется на "обработана, ..."
            result = await handler.download_processed_status()
            result_data = result.data
            if result_data and result_data.data:
                status = result_data.data.status
            else:
                break
            total_objects_count = result_data.data.overAllGoodsNumber + result_data.data.successGoodsNumber
            if status == 1:
                await asyncio.sleep(6)
        return total_objects_count

    async def fetch_load_detail(self, data, limit) -> MsgResponseToPlatform:
        from core.apps.basic.services.handlers.prices_and_discounts import PricesAndDiscountsHandler

        # Добавляем лимит в уже существующие параметры
        data["limit"] = limit
        request_body = self.request_body.model_copy(update={"data": data})
        handler = PricesAndDiscountsHandler(
            app=self.app,
            body=request_body,
        )
        result: MsgResponseToPlatform = await handler.processed_load_details()
        return result

    def _prepare_data_for_checking_load_progress(self, upload_task_response_data: list):
        if upload_task_response_data:
            # data = upload_task_response_data[0].get("data")
            data = upload_task_response_data[0].fetch_result.data
            if data:
                # return {"uploadID": data.get("id")}
                return {"uploadID": data.id}

    async def execute(self):
        # self.cards_in_markets = await self.fetch_nomenclature()
        # self.check_cards_in_market()
        # if self.input_data:
        upload_task_response_data: list = await self.export_prices_and_discounts()
        # Подготавливаем информацию для дальнейшей проверки статуса обработки
        data = self._prepare_data_for_checking_load_progress(upload_task_response_data)
        if data:
            # Проверка статуса
            limit = await self.fetch_load_progress(data=data)
            # Получаем детальную информацию по задаче(
            message_to_platform = await self.fetch_load_detail(data=data, limit=limit)
            return message_to_platform
        return MsgResponseToPlatform(data=self.response_data, errors=self.errors)

    def prepare_tasks_for_request_export_prices_and_discounts(self) -> Collection[Task]:
        items = self.input_data

        if not items:
            return []
        return self._prepare_tasks_for_cycle_request(
            items=items,
            count_items_one_iteration=COUNT_ITEMS_ONE_ITERATION_CREATE_OR_UPDATE_CARDS_V2,
            func_prepare_params=self._prepare_params_for_request_export_prices_and_discounts,
            url_schema=URL_EXPORT_PRICES_AND_DISCOUNTS,
            # vendor_codes_with_error=self.vendor_codes_with_error,
        )


class CreateProductRequester(AppRequester):
    """
    >>>
    Класс должен отвечать за логику V3.0 создание КТ на маркетплейсе
    https://openapi.wb.ru/content/api/ru/#tag/Zagruzka/paths/~1content~1v2~1cards~1upload/post.

    Создание карточки товара происходит асинхронно, при отправке запроса на создание КТ
    ваш запрос становится в очередь на создание КТ.
    ПРИМЕЧАНИЕ: Карточка товара считается созданной, если успешно создалась хотя бы одна НМ.
    ВАЖНО: Если во время обработки запроса в очереди выявляются ошибки, то НМ считается ошибочной.
    За раз можно создать 100 КТ по 30 вариантов товара (НМ) в каждой.

    Порядок создания КТ:
    1. Получить список всех родительских категорий методом "Родительские категории товаров"
    2. По имени или ID родительской категории получите список всех доступных предметов методом "Список предметов"
    3. По ID предмета получите характеристики доступные для Вашего предмета, методом "Характеристики предмета"
    Для характеристик Цвет, Страна производства, Сезон, Ставка НДС, ТНВЭД
    значения необходимо брать из справочников в разделе Конфигуратор
    4. Создайте запрос и отправьте его на сервер. Если запрос на создание прошел успешно,
    а карточка не создалась, то необходимо в первую очередь
    проверить наличие карточки в методе Список несозданных НМ с ошибками.
    Если карточка попала в ответ к этому методу, то необходимо исправить описанные ошибки
    в запросе на создание карточки и отправить его повторно.
    """

    async def fetch_parent_subjects(self) -> Optional[list[ParentSubject]]:
        """
        Returns:
        Список всех родительских категорий методом Родительские категории товаров.

        """
        try:
            response = await self.single_fetch(url_params=URL_PARENT_SUBJECTS, valid_type_negative=WBResponse)
        except RequestException:
            return []
        return response.data

    async def fetch_list_of_objects(self, params: WBRequestListOfObjects) -> Optional[list[ItemListOfObjects]]:
        """
        Returns:
        Список предметов
        """
        try:
            response = await self.single_fetch(
                url_params=URL_LIST_OF_OBJECTS,
                params=params.model_dump(exclude_none=True),
                valid_type_negative=WBResponse,
            )
        except RequestException:
            return []
        return response.data

    async def fetch_object_characteristics(
        self, params: WBRequestObjectCharacteristics
    ) -> Optional[list[ObjectCharacteristics]]:
        """
        Returns:
        Характеристики предмета
        """
        try:
            response = await self.single_fetch(
                url_params=url_with_params(URL_OBJECT_CHARACTERISTICS, params.subjectId),
                params=params.model_dump(exclude_none=True),
                valid_type_negative=WBResponse,
            )
        except RequestException:
            return []
        return response.data

    async def fetch_uncreated_nms_with_errors(self, params: WBRequestLocale) -> Optional[list[WBErrorNomenclature]]:
        """
        Returns:
        Список несозданных НМ с ошибками
        """
        try:
            response = await self.single_fetch(
                url_params=URL_LIST_ERROR_NOMENCLATURES_WILDBERRIES,
                params=params.model_dump(exclude_none=True),
                valid_type_negative=WBResponse,
            )
        except RequestException:
            return []
        return response.data


class SizeGoodsRequester(AppRequester):
    async def export_size_goods_price(
        self,
    ) -> Optional[dict]:
        """Установить цены для размеров"""
        try:
            response = await self.single_fetch(
                url_params=URL_SIZE_GOODS_PRICE_UPDATE,
                params=self.request_body.data,
                valid_type_negative=WBResponse,
            )
        except RequestException:
            return {}
        return response.data

    async def import_goods_size_for_nm(self) -> Optional[dict]:
        """Получить информацию о размерах товара.
        Важно!!! В data обязательно передать query_params.

        Пример request_body:
        {
          "headers": {
            "Authorization": "<token>"
          },
          "company_id": 1,
          "marketplace_id": 1,
          "event": "import_goods_size_for_nm",
          "data": {
                  "limit": 10,
                  "offset": 0,
                  "nmID": 253
          },
          "callback": "result_import_goods_size_for_nm",
          "event_id": "1",
          "task_id": 1
        }
        """
        try:
            query_params = self._get_query_params_from_request_body(pydantic_schema=URL_LIST_GOODS_SIZE.body_schema)
            response: URL_LIST_GOODS_SIZE.response_schema = await self.single_fetch(
                url_params=URL_LIST_GOODS_SIZE,
                params=query_params.model_dump(exclude_none=True),
                valid_type_negative=WBResponse,
            )
        except RequestException:
            return {}
        return response.data.model_dump()
