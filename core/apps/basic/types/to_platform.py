from typing import Optional

from pydantic import BaseModel, Field


class ResponseToPlatformStockFBO(BaseModel):
    nmId: Optional[int] = Field(description="Артикул WB", default=None)
    quantity: Optional[int] = Field(
        description="Количество, доступное для продажи (сколько можно добавить в корзину)", default=None
    )
    # Поля для платформы
    id_platform: Optional[int] = Field(title="Идентификатор товара в платформе", default=None)
    name_platform: Optional[str] = Field(title="Наименование товара в платформе", default=None)


class ResponseOrderToPlatform(BaseModel):
    company_id: int
    marketplace_id: int
    total: float
    schema: str
    created_at: str
    currency: str
    date_reg: str
    id: int
    id_mp: str
    status: str
    posting_number: str
    all_products_matched_to_platform: bool
    json_data: dict
