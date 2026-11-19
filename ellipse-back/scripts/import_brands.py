"""
Импортирует бренды из CSV-выгрузки старого сайта (формат Bitrix).

Ожидаемые колонки CSV: ID, UF_NAME, UF_XML_ID, UF_LINK, UF_DESCRIPTION,
UF_FULL_DESCRIPTION, UF_SORT, UF_FILE, UF_DEF.

Сопоставление с моделью Brand:
    external_id <- UF_XML_ID  (глобальный идентификатор, не внутренний Bitrix ID)
    name        <- UF_NAME
    description <- UF_FULL_DESCRIPTION, если пусто — UF_DESCRIPTION
    logo        <- UF_FILE

Идемпотентен: если бренд с таким external_id уже есть — обновляет его поля,
а не создаёт дубликат. Можно запускать повторно с обновлённой выгрузкой.

Запуск (из корня проекта):
    python scripts/import_brands.py path/to/brands.csv
"""
import argparse
import asyncio
import csv
import sys
from pathlib import Path

from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import async_session_maker
from app.modules.catalog.models import Brand


async def import_brands(csv_path: Path) -> None:
    created = 0
    updated = 0
    skipped = 0

    async with async_session_maker() as db:
        with open(csv_path, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                external_id = (row.get("UF_XML_ID") or "").strip()
                name = (row.get("UF_NAME") or "").strip()

                if not external_id or not name:
                    skipped += 1
                    continue

                description = (row.get("UF_FULL_DESCRIPTION") or "").strip() or (
                    row.get("UF_DESCRIPTION") or ""
                ).strip() or None
                logo = (row.get("UF_FILE") or "").strip() or None

                existing = (
                    await db.execute(select(Brand).where(Brand.external_id == external_id))
                ).scalar_one_or_none()

                if existing:
                    existing.name = name
                    existing.description = description
                    existing.logo = logo
                    updated += 1
                else:
                    db.add(
                        Brand(
                            external_id=external_id,
                            name=name,
                            description=description,
                            logo=logo,
                        )
                    )
                    created += 1

        await db.commit()

    print(f"Готово: создано {created}, обновлено {updated}, пропущено (пустые поля) {skipped}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Импорт брендов из CSV-выгрузки старого сайта")
    parser.add_argument("csv_path", type=Path, help="Путь до CSV-файла с брендами")
    args = parser.parse_args()

    if not args.csv_path.exists():
        raise SystemExit(f"Файл не найден: {args.csv_path}")

    asyncio.run(import_brands(args.csv_path))