from typing import Literal
from pydantic import BaseModel, Field
from .types import BarcodeType


class WBFilterGoodsQueryParams(BaseModel):
    limit: int = Field(
        description="Сколько элементов вывести на одной странице (пагинация). Максимум 1 000 элементов", default=10
    )
    offset: int = Field(description="Сколько элементов пропустить", default=0)
    filterNmID: int = Field(description="Артикул Wildberries, по которому искать товар")


class WBGoodsSizeQueryParams(BaseModel):
    limit: int = Field(
        description="Сколько элементов вывести на одной странице (пагинация). Максимум 1 000 элементов", default=10
    )
    offset: int = Field(description="Сколько элементов пропустить", default=0)
    nmID: int = Field(description="Артикул Wildberries")


class WBLoadProgressQueryParams(BaseModel):
    uploadID: int = Field(description="ID загрузки")


class WBOrdersStickersQueryParams(BaseModel):
    type: BarcodeType = Field(description="Тип этикетки", default="svg")
    width: Literal[58, 40] = Field(description="Ширина этикетки", default=58)
    height: Literal[40, 30] = Field(description="Высота этикетки", default=40)
