"""
Наполняет БД тестовыми данными для разработки.

Все созданные записи помечаются префиксом SEED_PREFIX в поле external_id —
это позволяет скрипту scripts/clear_seed_data.py безопасно удалить именно
эти данные, не затрагивая ничего другого.

Запуск (из корня проекта, с активным venv/зависимостями):
    python scripts/seed_data.py
"""
import asyncio
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

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


async def seed() -> None:
    async with async_session_maker() as db:
        # --- Бренды ---
        brands = [
            Brand(external_id=f"{SEED_PREFIX}brand-1", name="Aravia", description="Профессиональная косметика"),
            Brand(external_id=f"{SEED_PREFIX}brand-2", name="FarmStay", description="Корейская косметика"),
            Brand(external_id=f"{SEED_PREFIX}brand-3", name="Mixit", description="Уходовая косметика"),
        ]
        db.add_all(brands)
        await db.flush()

        # --- Категории (дерево: 2 корня, у каждого по 2 подкатегории) ---
        face_care = Category(external_id=f"{SEED_PREFIX}cat-face", name="Уход за лицом", sort_order=1)
        body_care = Category(external_id=f"{SEED_PREFIX}cat-body", name="Уход за телом", sort_order=2)
        db.add_all([face_care, body_care])
        await db.flush()

        serums = Category(external_id=f"{SEED_PREFIX}cat-serums", name="Сыворотки", parent_id=face_care.id, sort_order=1)
        creams = Category(external_id=f"{SEED_PREFIX}cat-creams", name="Кремы", parent_id=face_care.id, sort_order=2)
        scrubs = Category(external_id=f"{SEED_PREFIX}cat-scrubs", name="Скрабы", parent_id=body_care.id, sort_order=1)
        db.add_all([serums, creams, scrubs])
        await db.flush()

        # --- Магазины ---
        stores = [
            Store(
                external_id=f"{SEED_PREFIX}store-1",
                city="Томск",
                address="проспект Ленина, 1",
                phone="+7 (3822) 00-00-01",
                working_hours="Ежедневно 10:00–20:00",
                latitude=Decimal("56.4977"),
                longitude=Decimal("84.9744"),
            ),
            Store(
                external_id=f"{SEED_PREFIX}store-2",
                city="Кемерово",
                address="проспект Кузнецкий, 33",
                phone="+7 (3842) 00-00-02",
                working_hours="Ежедневно 10:00–21:00",
                latitude=Decimal("55.3547"),
                longitude=Decimal("86.0873"),
            ),
        ]
        db.add_all(stores)
        await db.flush()

        # --- Товары ---
        products_data = [
            dict(name="Сыворотка с гиалуроновой кислотой", brand=brands[0], category=serums, is_hit=True, price=Decimal("1490.00")),
            dict(name="Крем для лица увлажняющий", brand=brands[1], category=creams, is_hit=True, price=Decimal("1290.00")),
            dict(name="Крем для лица ночной", brand=brands[2], category=creams, is_hit=False, price=Decimal("1150.00")),
            dict(name="Сыворотка с витамином C", brand=brands[0], category=serums, is_hit=False, price=Decimal("1690.00")),
            dict(name="Скраб для тела кофейный", brand=brands[0], category=scrubs, is_hit=True, price=Decimal("750.00")),
            dict(name="Скраб для тела солевой", brand=brands[1], category=scrubs, is_hit=False, price=Decimal("690.00")),
        ]

        products = []
        for i, data in enumerate(products_data, start=1):
            product = Product(
                external_id=f"{SEED_PREFIX}product-{i}",
                article=f"ART-{1000 + i}",
                name=data["name"],
                description=f"Тестовое описание товара «{data['name']}».",
                brand_id=data["brand"].id,
                category_id=data["category"].id,
                is_hit=data["is_hit"],
                is_active=True,
            )
            products.append((product, data["price"]))
            db.add(product)
        await db.flush()

        # --- Цены и картинки товаров ---
        for product, price in products:
            # Цена теперь за пару (товар, магазин): тестовая цена одинакова во всех магазинах
            for store in stores:
                db.add(
                    ProductPrice(
                        product_id=product.id,
                        store_id=store.id,
                        price=price,
                        old_price=price + Decimal("200.00") if product.is_hit else None,
                        currency="RUB",
                    )
                )
            db.add(
                ProductImage(
                    product_id=product.id,
                    image_url=f"/images/seed/{product.external_id}.jpg",
                    sort_order=0,
                )
            )

        # --- Остатки по магазинам ---
        for product, _ in products:
            for store in stores:
                db.add(Inventory(product_id=product.id, store_id=store.id, quantity=10))

        # --- Акции ---
        today = date.today()
        permanent_promo = Promotion(
            external_id=f"{SEED_PREFIX}promo-1",
            title="Скидка в день рождения",
            short_description="Празднуйте вместе с нами.",
            description="Персональная скидка в день рождения и три дня до/после него.",
            type="permanent",
            is_active=True,
        )
        temporary_promo = Promotion(
            external_id=f"{SEED_PREFIX}promo-2",
            title="Скидка 20% на уход за лицом",
            short_description="Только до конца месяца.",
            description="Скидка 20% на все средства по уходу за лицом.",
            type="temporary",
            start_date=today,
            end_date=today + timedelta(days=30),
            is_active=True,
        )
        db.add_all([permanent_promo, temporary_promo])
        await db.flush()

        # Первые два товара — участники временной акции
        for product, _ in products[:2]:
            db.add(PromotionProduct(promotion_id=temporary_promo.id, product_id=product.id))

        await db.commit()
        print(f"Готово: {len(brands)} брендов, {5} категорий, {len(stores)} магазинов, "
              f"{len(products)} товаров, 2 акции.")


if __name__ == "__main__":
    asyncio.run(seed())