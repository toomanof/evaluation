from apps.basic.types import DataExportStock
from apps.basic.types.from_platform import RelationProduct, ResponseChangeStatusOrderFromMs
from apps.basic.types.responses import WBResponseOrdersStatus, WBResponseWarehouse, WBResponseWBStockFBO, WBStockFBO
from apps.basic.types.types import SupplyOrder, WBListProductInPlatform, WBProductInPlatform
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory import Use
import uuid
from core.tests.src.factories import TEST_PRODUCTS_IDS_RANGE


class RelationProductFactory(ModelFactory[RelationProduct]):
    idMp = lambda: ModelFactory.__random__.choice([str(num) for num in TEST_PRODUCTS_IDS_RANGE])


class SupplyOrderFactory(ModelFactory[SupplyOrder]):
    id = Use(ModelFactory.__random__.randint, 1, 10000)
    rid = str(uuid.uuid4())
    warehouseId = Use(ModelFactory.__random__.randint, 1, 10000)
    nmId = lambda: ModelFactory.__random__.choice(TEST_PRODUCTS_IDS_RANGE)
    chrtId = Use(ModelFactory.__random__.randint, 1, 10000)
    cargoType = Use(ModelFactory.__random__.randint, 1, 3)


class WBResponseOrdersStatusFactory(ModelFactory[WBResponseOrdersStatus]): ...


class WBResponseWarehouseFactory(ModelFactory[WBResponseWarehouse]): ...


class WBStockFBOFactory(ModelFactory[WBStockFBO]):
    __allow_none_optionals__ = False
    nmId = lambda: ModelFactory.__random__.choice(TEST_PRODUCTS_IDS_RANGE)


class WBResponseWBStockFBOFactory(ModelFactory[WBResponseWBStockFBO]):
    root = Use(WBStockFBOFactory.batch, size=10)


class WBProductInPlatformFactory(ModelFactory[WBProductInPlatform]):
    __allow_none_optionals__ = False


class WBListProductInPlatformFactory(ModelFactory[WBListProductInPlatform]):
    items = Use(WBProductInPlatformFactory.batch, size=10)


class DataExportStockFactory(ModelFactory[DataExportStock]):
    __allow_none_optionals__ = False


class ResponseChangeStatusOrderFromMsFactory(ModelFactory[ResponseChangeStatusOrderFromMs]):
    __allow_none_optionals__ = False
