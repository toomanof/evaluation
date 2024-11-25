from core.apps.basic.types.responses import (
    WBResponseRawLoadProgress,
    WBResponseObjectProcessedLoadDetail,
    WBResponseObjectHistoryGoods,
    WBResponseRawLoadDetails,
)
from core.apps.basic.types.types import WBFilterGoodsObject, WBGoodsSizeObject, SupplierTaskMetadataBuffer
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory import Use


class SupplierTaskMetadataBufferFactory(ModelFactory[SupplierTaskMetadataBuffer]):
    uploadID = Use(ModelFactory.__random__.randint, 1, 10000)
    status = Use(ModelFactory.__random__.choice, [3, 4, 5, 6])
    uploadDate = "2022-08-21T22:00:13+02:00"
    activationDate = "2022-08-21T22:00:13+02:00"


class WBResponseRawLoadProgressFactory(ModelFactory[WBResponseRawLoadProgress]): ...


class WBResponseRawLoadDetailsFactory(ModelFactory[WBResponseRawLoadDetails]): ...


class WBResponseObjectProcessedLoadDetailFactory(ModelFactory[WBResponseObjectProcessedLoadDetail]): ...


class WBResponseObjectHistoryGoodsFactory(ModelFactory[WBResponseObjectHistoryGoods]):
    nmID = Use(ModelFactory.__random__.randint, 1, 10000)
    vendorCode = "34552332l"
    sizeID = Use(ModelFactory.__random__.randint, 1, 10000)
    price = Use(ModelFactory.__random__.randint, 1, 10000)
    discount = Use(ModelFactory.__random__.randint, 1, 20)
    techSizeName = "42"
    currencyIsoCode4217 = "RUB"
    status = 3


class WBFilterGoodsObjectFactory(ModelFactory[WBFilterGoodsObject]):
    nmID = Use(ModelFactory.__random__.randint, 1, 10000)
    vendorCode = "34552332l"
    currencyIsoCode4217 = "RUB"
    discount = Use(ModelFactory.__random__.randint, 1, 20)


class WBGoodsSizeObjectFactory(ModelFactory[WBGoodsSizeObject]):
    nmID = Use(ModelFactory.__random__.randint, 1, 10000)
    sizeID = Use(ModelFactory.__random__.randint, 1, 10000)
    vendorCode = "34552332l"
    currencyIsoCode4217 = "RUB"
    discount = Use(ModelFactory.__random__.randint, 1, 20)
    discountedPrice = Use(ModelFactory.__random__.uniform, 1, 20000)
