"""
Импортирует товары из CSV-выгрузки.

Ожидаемые колонки CSV:
    id, external_id, barcode, article, name, description,
    brand_external_id, is_active, is_hit, image_url, category_id

Сопоставление с моделью Product:
    id                  — игнорируется (наш первичный ключ генерируется сам)
    external_id         — ключ идемпотентности (upsert)
    barcode, article    — как есть
    name, description   — как есть
    brand_external_id   — ищется Brand.external_id -> Product.brand_id
                          (бренды должны быть импортированы заранее, см. import_brands.py)
    category_id         — это уже наш внутренний UUID категории в БД, не external_id
    is_active, is_hit   — булевы поля в формате "Y" / пусто
    image_url           — если указан, создаётся/обновляется первая картинка
                          товара (product_images, sort_order=0)

Идемпотентен: товар с уже существующим external_id обновляется, а не дублируется.

Запуск (из корня проекта):
    python scripts/import_products.py path/to/products.csv
"""
import argparse
import asyncio
import csv
import sys
import uuid
from pathlib import Path

from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import async_session_maker
from app.modules.catalog.models import Brand, Category, Product, ProductImage


def parse_bool(value: str) -> bool:
    return (value or "").strip().upper() == "Y"


async def import_products(csv_path: Path) -> None:
    created = 0
    updated = 0
    skipped_no_key = 0
    unmatched_brand = 0
    unmatched_category = 0

    async with async_session_maker() as db:
        brand_by_external_id = {
            external_id: brand_id
            for brand_id, external_id in (
                await db.execute(
                    select(Brand.id, Brand.external_id).where(Brand.external_id.is_not(None))
                )
            ).all()
        }
        valid_category_ids = set(
            (await db.execute(select(Category.id))).scalars().all()
        )

        with open(csv_path, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                external_id = (row.get("external_id") or "").strip()
                name = (row.get("name") or "").strip()

                if not external_id or not name:
                    skipped_no_key += 1
                    continue

                brand_external_id = (row.get("brand_external_id") or "").strip()
                brand_id = brand_by_external_id.get(brand_external_id) if brand_external_id else None
                if brand_external_id and brand_id is None:
                    unmatched_brand += 1

                category_id = None
                raw_category_id = (row.get("category_id") or "").strip()
                if raw_category_id:
                    try:
                        parsed = uuid.UUID(raw_category_id)
                    except ValueError:
                        parsed = None
                    if parsed in valid_category_ids:
                        category_id = parsed
                    else:
                        unmatched_category += 1

                existing = (
                    await db.execute(select(Product).where(Product.external_id == external_id))
                ).scalar_one_or_none()

                if existing:
                    product = existing
                    updated += 1
                else:
                    product = Product(external_id=external_id)
                    db.add(product)
                    created += 1

                product.barcode = (row.get("barcode") or "").strip() or None
                product.article = (row.get("article") or "").strip() or None
                product.name = name
                product.description = (row.get("description") or "").strip() or None
                product.brand_id = brand_id
                product.category_id = category_id
                product.is_active = parse_bool(row.get("is_active"))
                product.is_hit = parse_bool(row.get("is_hit"))

                await db.flush()

                image_url = (row.get("image_url") or "").strip()
                if image_url:
                    existing_image = (
                        await db.execute(
                            select(ProductImage).where(
                                ProductImage.product_id == product.id,
                                ProductImage.sort_order == 0,
                            )
                        )
                    ).scalar_one_or_none()
                    if existing_image:
                        existing_image.image_url = image_url
                    else:
                        db.add(
                            ProductImage(
                                product_id=product.id, image_url=image_url, sort_order=0
                            )
                        )

        await db.commit()

    print(
        f"Готово: создано {created}, обновлено {updated}, "
        f"пропущено без ключа {skipped_no_key}, бренд не найден {unmatched_brand}, "
        f"категория не найдена {unmatched_category}."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Импорт товаров из CSV")
    parser.add_argument("csv_path", type=Path, help="Путь до CSV-файла с товарами")
    args = parser.parse_args()

    if not args.csv_path.exists():
        raise SystemExit(f"Файл не найден: {args.csv_path}")

    asyncio.run(import_products(args.csv_path))