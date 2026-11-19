import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.promotions import crud
from app.modules.promotions.schemas import (
    PromotionCreate,
    PromotionProductCreate,
    PromotionProductRead,
    PromotionRead,
    PromotionUpdate,
)

router = APIRouter(prefix="/promotions", tags=["promotions"])


@router.get("/", response_model=list[PromotionRead])
async def list_promotions(db: AsyncSession = Depends(get_db)):
    return await crud.get_promotions(db)


@router.get("/{promotion_id}", response_model=PromotionRead)
async def get_promotion(promotion_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    promotion = await crud.get_promotion(db, promotion_id)
    if promotion is None:
        raise HTTPException(status_code=404, detail="Promotion not found")
    return promotion


@router.post("/", response_model=PromotionRead, status_code=201)
async def create_promotion(data: PromotionCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_promotion(db, data)


@router.patch("/{promotion_id}", response_model=PromotionRead)
async def update_promotion(
    promotion_id: uuid.UUID, data: PromotionUpdate, db: AsyncSession = Depends(get_db)
):
    promotion = await crud.get_promotion(db, promotion_id)
    if promotion is None:
        raise HTTPException(status_code=404, detail="Promotion not found")
    return await crud.update_promotion(db, promotion, data)


@router.delete("/{promotion_id}", status_code=204)
async def delete_promotion(
    promotion_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    promotion = await crud.get_promotion(db, promotion_id)
    if promotion is None:
        raise HTTPException(status_code=404, detail="Promotion not found")
    await crud.delete_promotion(db, promotion)


@router.get(
    "/{promotion_id}/products", response_model=list[PromotionProductRead]
)
async def list_promotion_products(
    promotion_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    return await crud.get_promotion_products(db, promotion_id)


@router.post(
    "/{promotion_id}/products",
    response_model=PromotionProductRead,
    status_code=201,
)
async def add_promotion_product(
    promotion_id: uuid.UUID,
    data: PromotionProductCreate,
    db: AsyncSession = Depends(get_db),
):
    promotion = await crud.get_promotion(db, promotion_id)
    if promotion is None:
        raise HTTPException(status_code=404, detail="Promotion not found")
    return await crud.add_promotion_product(db, promotion_id, data.product_id)


@router.delete("/{promotion_id}/products/{product_id}", status_code=204)
async def remove_promotion_product(
    promotion_id: uuid.UUID, product_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    link = await crud.get_promotion_product(db, promotion_id, product_id)
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    await crud.remove_promotion_product(db, link)