import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class StoreBase(BaseModel):
    city: str | None = None
    address: str | None = None
    phone: str | None = None
    working_hours: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None


class StoreCreate(StoreBase):
    external_id: str | None = None


class StoreUpdate(BaseModel):
    city: str | None = None
    address: str | None = None
    phone: str | None = None
    working_hours: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None


class StoreRead(StoreBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    external_id: str | None = None
    images: list[str] = []


class StoreImageBase(BaseModel):
    image_url: str
    sort_order: int = 0


class StoreImageCreate(StoreImageBase):
    store_id: uuid.UUID


class StoreImageUpdate(BaseModel):
    image_url: str | None = None
    sort_order: int | None = None


class StoreImageRead(StoreImageBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    store_id: uuid.UUID