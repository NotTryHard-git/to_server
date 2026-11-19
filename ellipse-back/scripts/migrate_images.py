"""
Переносит уже скачанные со старого сайта изображения в активное хранилище
(STORAGE_BACKEND=local или s3 — см. .env) и обновляет image_url в БД.

В таблице product_images сейчас лежат "мёртвые" пути вида:
    /upload/iblock/02c/050058002-...jpg
Они больше никуда не ведут — файлы физически скачаны в отдельную папку.

Скрипт сопоставляет строки по ИМЕНИ ФАЙЛА (basename), а не по полному пути —
поэтому неважно, сохранили ли вы папки как на сайте (upload/iblock/02c/...)
или сложили все файлы в одну плоскую папку: скрипт найдёт файл в --source-dir
рекурсивно по имени.

Обрабатываются только строки, где image_url ещё НЕ похож на готовый URL
(не начинается с http:// или https://) — поэтому скрипт идемпотентен:
повторный запуск не трогает уже перенесённые картинки.

Запуск (из корня проекта):
    python scripts/migrate_images.py путь/до/папки/со/скачанными/картинками
    python scripts/migrate_images.py путь/до/папки --dry-run   # без изменений, только отчёт
"""
import argparse
import asyncio
import sys
from pathlib import Path

from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import async_session_maker
from app.core.storage import get_storage
from app.modules.catalog.models import ProductImage


def build_file_index(source_dir: Path) -> tuple[dict[str, Path], set[str]]:
    """Индекс filename -> путь. Возвращает также набор неоднозначных имён
    (встретились дважды и более) — их трогать не будем, слишком рискованно."""
    index: dict[str, Path] = {}
    duplicates: set[str] = set()

    for path in source_dir.rglob("*"):
        if not path.is_file():
            continue
        name = path.name
        if name in index:
            duplicates.add(name)
        else:
            index[name] = path

    return index, duplicates


async def migrate_images(source_dir: Path, dry_run: bool) -> None:
    file_index, duplicate_names = build_file_index(source_dir)
    print(f"Найдено файлов в {source_dir}: {len(file_index) + len(duplicate_names)}")
    if duplicate_names:
        print(f"⚠ Неоднозначных имён (пропущены): {len(duplicate_names)}")

    storage = get_storage()

    migrated = 0
    missing = 0
    ambiguous = 0
    already_done = 0

    async with async_session_maker() as db:
        rows = (
            await db.execute(
                select(ProductImage).where(
                    ProductImage.image_url.not_like("http://%"),
                    ProductImage.image_url.not_like("https://%"),
                )
            )
        ).scalars().all()

        print(f"Строк с ещё не перенесёнными картинками: {len(rows)}")

        for image in rows:
            filename = Path(image.image_url).name

            if filename in duplicate_names:
                ambiguous += 1
                continue

            local_path = file_index.get(filename)
            if local_path is None:
                missing += 1
                continue

            if dry_run:
                migrated += 1
                continue

            new_url = await storage.save_file(local_path, filename=filename)
            image.image_url = new_url
            migrated += 1

        if not dry_run:
            await db.commit()

    print(
        f"{'Будет перенесено' if dry_run else 'Перенесено'}: {migrated}, "
        f"не найдено локально: {missing}, неоднозначных: {ambiguous}, "
        f"уже перенесённых (пропущены заранее): {already_done}."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Перенос скачанных картинок в активное хранилище")
    parser.add_argument("source_dir", type=Path, help="Папка со скачанными со старого сайта картинками")
    parser.add_argument("--dry-run", action="store_true", help="Показать, что будет сделано, ничего не меняя")
    args = parser.parse_args()

    if not args.source_dir.exists():
        raise SystemExit(f"Папка не найдена: {args.source_dir}")

    asyncio.run(migrate_images(args.source_dir, args.dry_run))