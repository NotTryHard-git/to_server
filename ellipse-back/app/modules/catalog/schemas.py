import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    name: str
    parent_id: uuid.UUID | None = None
    image: str | None = None
    sort_order: int = 0


class CategoryCreate(CategoryBase):
    external_id: str | None = None


class CategoryUpdate(BaseModel):
    name: str | None = None
    parent_id: uuid.UUID | None = None
    image: str | None = None
    sort_order: int | None = None


class CategoryRead(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    external_id: str | None = None


class BrandBase(BaseModel):
    name: str
    description: str | None = None
    logo: str | None = None


class BrandCreate(BrandBase):
    external_id: str | None = None


class BrandUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    logo: str | None = None


class BrandRead(BrandBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    external_id: str | None = None


class ProductBase(BaseModel):
    name: str
    barcode: str | None = None
    article: str | None = None
    description: str | None = None
    brand_id: uuid.UUID | None = None
    category_id: uuid.UUID | None = None
    is_hit: bool = False
    is_active: bool = True


class ProductCreate(ProductBase):
    external_id: str | None = None


class ProductUpdate(BaseModel):
    name: str | None = None
    barcode: str | None = None
    article: str | None = None
    description: str | None = None
    brand_id: uuid.UUID | None = None
    category_id: uuid.UUID | None = None
    is_hit: bool | None = None
    is_active: bool | None = None


class ProductRead(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    external_id: str | None = None
    created_at: datetime
    updated_at: datetime


class ProductImageBase(BaseModel):
    image_url: str
    sort_order: int = 0


class ProductImageCreate(ProductImageBase):
    product_id: uuid.UUID


class ProductImageUpdate(BaseModel):
    image_url: str | None = None
    sort_order: int | None = None


class ProductImageRead(ProductImageBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID


class ProductPriceBase(BaseModel):
    price: Decimal
    old_price: Decimal | None = None
    currency: str = "RUB"


class ProductPriceCreate(ProductPriceBase):
    product_id: uuid.UUID


class ProductPriceUpdate(BaseModel):
    price: Decimal | None = None
    old_price: Decimal | None = None
    currency: str | None = None


class ProductPriceRead(ProductPriceBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID
    updated_at: datetime


class InventoryBase(BaseModel):
    quantity: int = 0


class InventoryCreate(InventoryBase):
    product_id: uuid.UUID
    store_id: uuid.UUID


class InventoryUpdate(BaseModel):
    quantity: int


class InventoryRead(InventoryBase):
    model_config = ConfigDict(from_attributes=True)

    product_id: uuid.UUID
    store_id: uuid.UUID
    updated_at: datetime