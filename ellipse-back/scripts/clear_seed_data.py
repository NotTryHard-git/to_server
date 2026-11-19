"""
Безвозвратно удаляет тестовые данные, созданные scripts/seed_data.py.

Удаляются только записи, помеченные префиксом SEED_PREFIX в external_id
(и связанные с ними строки в таблицах без external_id — inventory,
product_images, product_prices, promotion_products). Реальные данные
(например, из синхронизации с 1С) не затрагиваются.

Запуск (из корня проекта):
    python scripts/clear_seed_data.py
"""
import asyncio
import sys
from pathlib import Path

from sqlalchemy import delete, select

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import async_session_maker
from app.modules.catalog.models import (
    Brand,
    Category,
    Inventory,
    Product,
    ProductImage,
    ProductPrice,
)
from app.modules.promotions.models import Promotion, PromotionProduct
from app.modules.stores.models import Store

SEED_PREFIX = "seed-"


async def clear() -> None:
    async with async_session_maker() as db:
        seed_filter = lambda model: model.external_id.like(f"{SEED_PREFIX}%")  # noqa: E731

        product_ids = (
            await db.execute(select(Product.id).where(seed_filter(Product)))
        ).scalars().all()
        category_rows = (
            await db.execute(
                select(Category.id, Category.parent_id).where(seed_filter(Category))
            )
        ).all()
        store_ids = (
            await db.execute(select(Store.id).where(seed_filter(Store)))
        ).scalars().all()
        brand_ids = (
            await db.execute(select(Brand.id).where(seed_filter(Brand)))
        ).scalars().all()
        promotion_ids = (
            await db.execute(select(Promotion.id).where(seed_filter(Promotion)))
        ).scalars().all()

        if not product_ids and not category_rows and not store_ids and not brand_ids and not promotion_ids:
            print("Тестовых данных не найдено — удалять нечего.")
            return

        # 1. Таблицы, зависящие от товаров/магазинов/акций
        if product_ids:
            await db.execute(delete(ProductPrice).where(ProductPrice.product_id.in_(product_ids)))
            await db.execute(delete(ProductImage).where(ProductImage.product_id.in_(product_ids)))
            await db.execute(delete(Inventory).where(Inventory.product_id.in_(product_ids)))
            await db.execute(delete(PromotionProduct).where(PromotionProduct.product_id.in_(product_ids)))
        if store_ids:
            await db.execute(delete(Inventory).where(Inventory.store_id.in_(store_ids)))
        if promotion_ids:
            await db.execute(delete(PromotionProduct).where(PromotionProduct.promotion_id.in_(promotion_ids)))

        # 2. Сами товары
        if product_ids:
            await db.execute(delete(Product).where(Product.id.in_(product_ids)))

        # 3. Категории — сначала дочерние (с parent_id), затем корневые,
        # чтобы не упереться в self-referencing FK
        if category_rows:
            child_ids = [cid for cid, parent_id in category_rows if parent_id is not None]
            root_ids = [cid for cid, parent_id in category_rows if parent_id is None]
            if child_ids:
                await db.execute(delete(Category).where(Category.id.in_(child_ids)))
            if root_ids:
                await db.execute(delete(Category).where(Category.id.in_(root_ids)))

        # 4. Бренды, магазины, акции
        if brand_ids:
            await db.execute(delete(Brand).where(Brand.id.in_(brand_ids)))
        if store_ids:
            await db.execute(delete(Store).where(Store.id.in_(store_ids)))
        if promotion_ids:
            await db.execute(delete(Promotion).where(Promotion.id.in_(promotion_ids)))

        await db.commit()
        print(
            f"Удалено: {len(product_ids)} товаров, {len(category_rows)} категорий, "
            f"{len(brand_ids)} брендов, {len(store_ids)} магазинов, {len(promotion_ids)} акций."
        )


if __name__ == "__main__":
    asyncio.run(clear())