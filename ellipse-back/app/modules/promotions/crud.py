import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.promotions.models import Promotion, PromotionProduct
from app.modules.promotions.schemas import PromotionCreate, PromotionUpdate


async def get_promotion(db: AsyncSession, promotion_id: uuid.UUID) -> Promotion | None:
    return await db.get(Promotion, promotion_id)


async def get_promotions(db: AsyncSession) -> list[Promotion]:
    result = await db.execute(select(Promotion).order_by(Promotion.start_date))
    return list(result.scalars().all())


async def create_promotion(db: AsyncSession, data: PromotionCreate) -> Promotion:
    promotion = Promotion(**data.model_dump())
    db.add(promotion)
    await db.commit()
    await db.refresh(promotion)
    return promotion


async def update_promotion(
    db: AsyncSession, promotion: Promotion, data: PromotionUpdate
) -> Promotion:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(promotion, field, value)
    await db.commit()
    await db.refresh(promotion)
    return promotion


async def delete_promotion(db: AsyncSession, promotion: Promotion) -> None:
    await db.delete(promotion)
    await db.commit()


async def get_promotion_products(
    db: AsyncSession, promotion_id: uuid.UUID
) -> list[PromotionProduct]:
    query = select(PromotionProduct).where(
        PromotionProduct.promotion_id == promotion_id
    )
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_promotion_product(
    db: AsyncSession, promotion_id: uuid.UUID, product_id: uuid.UUID
) -> PromotionProduct | None:
    return await db.get(PromotionProduct, (promotion_id, product_id))


async def add_promotion_product(
    db: AsyncSession, promotion_id: uuid.UUID, product_id: uuid.UUID
) -> PromotionProduct:
    link = PromotionProduct(promotion_id=promotion_id, product_id=product_id)
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return link


async def remove_promotion_product(
    db: AsyncSession, link: PromotionProduct
) -> None:
    await db.delete(link)
    await db.commit()