"""
Восстанавливает физически отсутствующие файлы изображений товаров.

В отличие от migrate_images.py (который решает "перенесено/не перенесено"
по ФОРМАТУ ссылки — начинается ли она с http://), этот скрипт проверяет
РЕАЛЬНОЕ наличие файла на диске LOCAL_STORAGE_DIR. Актуально для ситуации,
когда ссылки в БД уже правильные (http://.../media/имя.jpg), но сам файл
физически пропал — например, контейнер backend пересобирался без
постоянного volume для LOCAL_STORAGE_DIR, и диск сбросился к состоянию
образа.

Работает только при STORAGE_BACKEND=local (для S3 эта проблема
в принципе невозможна — там нет "диска контейнера").

Ссылки в БД НЕ ИЗМЕНЯЮТСЯ — файл просто кладётся туда, куда ссылка уже
указывает, найденный по имени файла в исходной папке.

Запуск (из корня проекта):
    python scripts/repair_missing_local_images.py путь/до/папки/с/фото
    python scripts/repair_missing_local_images.py путь/до/папки --dry-run
"""
import argparse
import asyncio
import shutil
import sys
from pathlib import Path

from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.core.database import async_session_maker
from app.modules.catalog.models import ProductImage


async def repair_missing_local_images(source_dir: Path, dry_run: bool) -> None:
    if settings.STORAGE_BACKEND != "local":
        raise SystemExit(
            f"STORAGE_BACKEND={settings.STORAGE_BACKEND!r}, а не 'local' — "
            f"этот скрипт актуален только для локального хранилища."
        )

    base_url = settings.LOCAL_STORAGE_BASE_URL.rstrip("/")
    storage_dir = Path(settings.LOCAL_STORAGE_DIR)
    storage_dir.mkdir(parents=True, exist_ok=True)

    # индекс файлов в исходной папке по имени (basename)
    file_index: dict[str, Path] = {}
    duplicates: set[str] = set()
    for path in source_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.name in file_index:
            duplicates.add(path.name)
        else:
            file_index[path.name] = path

    print(f"Найдено файлов в {source_dir}: {len(file_index) + len(duplicates)}")
    if duplicates:
        print(f"⚠ Неоднозначных имён (пропущены): {len(duplicates)}")

    placed = 0
    already_ok = 0
    missing_source = 0
    not_local_url = 0
    ambiguous = 0

    async with async_session_maker() as db:
        rows = (await db.execute(select(ProductImage))).scalars().all()
        print(f"Всего строк product_images: {len(rows)}")

        for image in rows:
            if not image.image_url.startswith(base_url + "/"):
                not_local_url += 1
                continue

            rel_path = image.image_url[len(base_url) + 1:]
            dest = storage_dir / rel_path
            filename = Path(rel_path).name

            if dest.exists():
                already_ok += 1
                continue

            if filename in duplicates:
                ambiguous += 1
                print(f"⚠ Неоднозначное имя (пропущено): {filename}")
                continue

            source_path = file_index.get(filename)
            if source_path is None:
                missing_source += 1
                continue

            if not dry_run:
                dest.parent.mkdir(parents=True, exist_ok=True)
                await asyncio.to_thread(shutil.copy2, source_path, dest)
            placed += 1

    print(
        f"\n{'Будет восстановлено' if dry_run else 'Восстановлено'}: {placed}\n"
        f"Уже на месте (файл был): {already_ok}\n"
        f"Не найдено в исходной папке: {missing_source}\n"
        f"Ссылка не локальная (пропущено): {not_local_url}\n"
        f"Неоднозначных имён: {ambiguous}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Восстановление недостающих файлов изображений товаров")
    parser.add_argument("source_dir", type=Path, help="Папка со скачанными/имеющимися фото товаров")
    parser.add_argument("--dry-run", action="store_true", help="Показать, что будет сделано, ничего не меняя")
    args = parser.parse_args()

    if not args.source_dir.exists():
        raise SystemExit(f"Папка не найдена: {args.source_dir}")

    asyncio.run(repair_missing_local_images(args.source_dir, args.dry_run))