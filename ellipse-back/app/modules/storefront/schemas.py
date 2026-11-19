import uuid
from decimal import Decimal

from pydantic import BaseModel


class ProductListItem(BaseModel):
    id: uuid.UUID
    name: str
    brand: str | None = None
    image: str | None = None
    is_hit: bool
    # Цены больше нет здесь: она теперь за магазином, а не за товаром.
    # На маленькой карточке фронт показывает статичную фразу
    # "Узнать цену и количество" вместо числа.


class ProductListResponse(BaseModel):
    page: int
    pages: int
    total: int
    items: list[ProductListItem]


class ProductHit(BaseModel):
    id: uuid.UUID
    name: str
    image: str | None = None
    brand: str | None = None


class BrandShort(BaseModel):
    id: uuid.UUID
    name: str


class CategoryShort(BaseModel):
    id: uuid.UUID
    name: str


class StorePriceInfo(BaseModel):
    """Одна строка таблицы наличия/цены на странице товара — цена и остаток
    в конкретном магазине."""

    store_id: uuid.UUID
    store_name: str | None = None
    price: Decimal | None = None
    currency: str | None = None
    quantity: int


class ProductPromotionShort(BaseModel):
    id: uuid.UUID
    title: str


class ProductDetail(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    barcode: str | None = None
    brand: BrandShort | None = None
    category: CategoryShort | None = None
    category_path: list[CategoryShort] = []
    # Объединённая таблица "наличие + цена по магазинам" — раньше это были
    # два отдельных поля (price + availability), теперь цена без магазина
    # не имеет смысла, поэтому они слиты в одно
    store_prices: list[StorePriceInfo]
    images: list[str]
    promotions: list[ProductPromotionShort]


class CategoryTreeNode(BaseModel):
    id: uuid.UUID
    name: str
    children: list["CategoryTreeNode"] = []