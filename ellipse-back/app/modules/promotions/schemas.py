import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict


class PromotionBase(BaseModel):
    title: str
    short_description: str | None = None
    description: str | None = None
    banner: str | None = None
    type: str
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool = True


class PromotionCreate(PromotionBase):
    external_id: str | None = None


class PromotionUpdate(BaseModel):
    title: str | None = None
    short_description: str | None = None
    description: str | None = None
    banner: str | None = None
    type: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool | None = None


class PromotionRead(PromotionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    external_id: str | None = None


class PromotionProductCreate(BaseModel):
    product_id: uuid.UUID


class PromotionProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    promotion_id: uuid.UUID
    product_id: uuid.UUID