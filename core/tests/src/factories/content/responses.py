from core.apps.basic.types import WBNomenclature
from core.apps.basic.types.types import (
    WBCharacteristicValue,
    WBErrorNomenclature,
    WBCardProductSize,
    WBCursorNomenclature,
)
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory import Use


class WBNomenclatureFactory(ModelFactory[WBNomenclature]):
    nmId = Use(ModelFactory.__random__.randint, 1, 10000)
    imtID = Use(ModelFactory.__random__.randint, 1, 10000)
    subjectID = Use(ModelFactory.__random__.randint, 1, 10000)
    vendorCode = "123453559000"
    brand = "Тест"

    characteristics = [WBCharacteristicValue(id=1, name="test", value=["красно-сиреневый"]).model_dump()]
    sizes = [WBCardProductSize(chrtID=252, techSize="S", wbSize="42", skus=["88005553535"]).model_dump()]

    mediaFiles = None
    colors = None
    photos = None
    video = None


class WBCursorNomenclatureFactory(ModelFactory[WBCursorNomenclature]):
    __allow_none_optionals__ = False
    nmID = Use(ModelFactory.__random__.randint, 0, 5)


class WBErrorNomenclatureFactory(ModelFactory[WBErrorNomenclature]):
    objectID = Use(ModelFactory.__random__.randint, 1, 10000)
