from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class InventoryPriceUpdateItem(BaseModel):
    """Одна строка от 1С в каноническом виде (после нормализации в ellipse-sync).

    quantity или price может отсутствовать: тогда обновляется только то, что пришло
    (например, 1С прислала только цены — остатки не трогаем).
    """

    product_external_id: str = Field(min_length=1, max_length=100)
    store_external_id: str = Field(min_length=1, max_length=100)
    quantity: int | None = Field(default=None, ge=0, le=10_000_000)
    price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    old_price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    currency: str = Field(default="RUB", min_length=3, max_length=3)

    @field_validator("product_external_id", "store_external_id")
    @classmethod
    def _strip(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("пустой идентификатор")
        return v

    @model_validator(mode="after")
    def _something_to_update(self) -> "InventoryPriceUpdateItem":
        if self.quantity is None and self.price is None:
            raise ValueError("нужно хотя бы одно из полей: quantity, price")
        return self


class RejectedRow(BaseModel):
    """Строка, отклонённая при нормализации/валидации (не попала в базу)."""

    index: int | None = None
    reason: str
    row: Any | None = None


class InventoryPriceUpdateBatch(BaseModel):
    items: list[InventoryPriceUpdateItem]

    # Необязательные служебные поля. Без них пачка = обычное «дельта»-обновление,
    # то есть старый формат {"items": [...]} продолжает работать как раньше.
    batch_id: str | None = Field(default=None, max_length=100)
    mode: Literal["delta", "full"] = "delta"
    # Последняя пачка полной выгрузки: после неё остатки товаров, которых в выгрузке
    # не было, обнуляются (только для магазинов, участвовавших в выгрузке)
    final: bool = False
    # Магазины, которые покрывает полная выгрузка (если у магазина вообще нет строк —
    # весь его остаток должен обнулиться — его всё равно нужно перечислить здесь)
    stores: list[str] = Field(default_factory=list)

    # Заполняет ellipse-sync: что не удалось разобрать + исходное тело запроса
    rejected: list[RejectedRow] = Field(default_factory=list)
    raw: Any | None = None
    error: str | None = None
    client_ip: str | None = None

    @model_validator(mode="after")
    def _full_needs_batch_id(self) -> "InventoryPriceUpdateBatch":
        if self.mode == "full" and not self.batch_id:
            raise ValueError("для mode=full обязателен batch_id (общий для всех пачек выгрузки)")
        return self


class InventoryPriceUpdateResult(BaseModel):
    status: Literal["ok", "partial", "error"] = "ok"
    batch_id: str | None = None
    received: int = 0
    updated: int  # строк применено (остаток и/или цена)
    prices_inserted: int = 0  # новых записей цены (цена изменилась)
    prices_unchanged: int = 0  # цена та же — запись не создавалась
    zeroed: int = 0  # остатков обнулено по итогам полной выгрузки
    unmatched_products: list[str]
    unmatched_stores: list[str]
    rejected: list[RejectedRow] = Field(default_factory=list)
