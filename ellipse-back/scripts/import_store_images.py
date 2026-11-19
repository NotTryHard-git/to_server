"""
Импортирует фото магазинов из папки со следующей структурой:

    source_dir/
        <id_магазина_1>/
            фото1.jpg
            фото2.jpg
        <id_магазина_2>/
            фото1.jpg
            ...

Имя подпапки — это UUID магазина в нашей БД (не внешний/legacy id).

Для каждой найденной подпапки:
    1. Проверяем, что магазин с таким id существует в stores.
    2. Файлы внутри сортируются по имени — так определяется sort_order (0, 1, 2, ...).
    3. Каждый файл загружается в активное хранилище через get_storage()
       (STORAGE_BACKEND=local или s3 — см. .env), в БД сохраняется итоговый URL.

Идемпотентность: скрипт ПОЛНОСТЬЮ ЗАМЕНЯЕТ набор фото магазина при каждом
запуске — перед импортом старые store_images этого магазина удаляются,
а из папки загружается свежий набор. Так что папка — единственный источник
правды: чтобы убрать/переставить фото магазина, просто поменяйте содержимое
его подпапки и запустите скрипт заново.

Запуск (из корня проекта):
    python scripts/import_store_images.py путь/до/папки/со/фото
    python scripts/import_store_images.py путь/до/папки --dry-run   # без изменений, только отчёт
"""
import argparse
import asyncio
import sys
import uuid
from pathlib import Path

from sqlalchemy import delete, select

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import async_session_maker
from app.core.storage import get_storage
from app.modules.stores.models import Store, StoreImage

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


async def import_store_images(source_dir: Path, dry_run: bool) -> None:
    storage = get_storage()

    imported_stores = 0
    imported_images = 0
    skipped_unknown_store = 0
    skipped_empty = 0

    async with async_session_maker() as db:
        valid_store_ids = set(
            (await db.execute(select(Store.id))).scalars().all()
        )

        for folder in sorted(source_dir.iterdir()):
            if not folder.is_dir():
                continue

            try:
                store_id = uuid.UUID(folder.name)
            except ValueError:
                print(f"⚠ Пропущено: имя папки не похоже на UUID — {folder.name}")
                skipped_unknown_store += 1
                continue

            if store_id not in valid_store_ids:
                print(f"⚠ Пропущено: магазина с id={store_id} нет в БД")
                skipped_unknown_store += 1
                continue

            files = sorted(
                p for p in folder.iterdir()
                if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
            )
            if not files:
                skipped_empty += 1
                continue

            if dry_run:
                print(f"{store_id}: будет импортировано {len(files)} фото")
                imported_stores += 1
                imported_images += len(files)
                continue

            # Папка — источник правды: полностью заменяем набор фото магазина
            await db.execute(delete(StoreImage).where(StoreImage.store_id == store_id))

            for sort_order, file_path in enumerate(files):
                image_url = await storage.save_file(file_path)
                db.add(
                    StoreImage(
                        store_id=store_id,
                        image_url=image_url,
                        sort_order=sort_order,
                    )
                )

            imported_stores += 1
            imported_images += len(files)

        if not dry_run:
            await db.commit()

    print(
        f"{'Будет импортировано' if dry_run else 'Импортировано'}: "
        f"{imported_images} фото для {imported_stores} магазинов. "
        f"Пропущено (неизвестный магазин): {skipped_unknown_store}, "
        f"пропущено (пустых папок): {skipped_empty}."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Импорт фото магазинов из папок, названных по id магазина"
    )
    parser.add_argument("source_dir", type=Path, help="Папка с подпапками <id_магазина>/фото...")
    parser.add_argument("--dry-run", action="store_true", help="Показать, что будет сделано, ничего не меняя")
    args = parser.parse_args()

    if not args.source_dir.exists():
        raise SystemExit(f"Папка не найдена: {args.source_dir}")

    asyncio.run(import_store_images(args.source_dir, args.dry_run))