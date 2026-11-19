"""
Загружает баннеры акций из папки в активное хранилище (STORAGE_BACKEND=local
или s3 — см. .env) и прописывает ссылку в promotions.banner.

Структура папки — плоская, один файл на акцию:
    source_dir/
        <id_или_external_id_акции>.jpg
        <id_или_external_id_акции>.png
        ...

Имя файла (без расширения) сопоставляется сначала с Promotion.id (если это
валидный UUID), а если нет — с Promotion.external_id.

В отличие от импорта фото товаров/магазинов, здесь не отдельная таблица,
а одно поле (banner) — поэтому скрипт просто ПЕРЕЗАПИСЫВАЕТ его значение.
Это уже само по себе идемпотентно: повторный запуск с той же папкой
просто ещё раз проставит тот же URL, ничего не задублируется.

Запуск (из корня проекта):
    python scripts/import_promotion_banners.py путь/до/папки/с/баннерами
    python scripts/import_promotion_banners.py путь/до/папки --dry-run
"""
import argparse
import asyncio
import sys
import uuid
from pathlib import Path

from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import async_session_maker
from app.core.storage import get_storage
from app.modules.promotions.models import Promotion

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def _already_uploaded(banner_url: str | None, filename: str) -> bool:
    """True, если banner уже указывает ровно на этот файл (без anti-collision
    префикса — тот добавляется ПЕРЕД именем через дефис, поэтому URL с
    префиксом никогда не совпадёт с "/{filename}" в конце — это осознанно:
    такой редкий случай лучше перезалить, чем спутать с чужим файлом)."""
    return bool(banner_url) and banner_url.endswith(f"/{filename}")


async def import_promotion_banners(source_dir: Path, dry_run: bool) -> None:
    storage = get_storage()

    updated = 0
    unmatched: list[str] = []
    skipped_non_image = 0

    async with async_session_maker() as db:
        promotions_by_id: dict[uuid.UUID, Promotion] = {}
        promotions_by_external_id: dict[str, Promotion] = {}

        for promotion in (await db.execute(select(Promotion))).scalars().all():
            promotions_by_id[promotion.id] = promotion
            if promotion.external_id:
                promotions_by_external_id[promotion.external_id] = promotion

        for file_path in sorted(source_dir.iterdir()):
            if not file_path.is_file():
                continue
            if file_path.suffix.lower() not in IMAGE_EXTENSIONS:
                skipped_non_image += 1
                continue

            stem = file_path.stem
            promotion: Promotion | None = None

            try:
                promotion = promotions_by_id.get(uuid.UUID(stem))
            except ValueError:
                pass
            if promotion is None:
                promotion = promotions_by_external_id.get(stem)

            if promotion is None:
                print(f"⚠ Не найдена акция для файла {file_path.name} (id/external_id={stem})")
                unmatched.append(file_path.name)
                continue

            if _already_uploaded(promotion.banner, file_path.name):
                # Уже загружали именно этот файл раньше — перезаливать не нужно
                updated += 1
                continue

            if dry_run:
                print(f"{file_path.name} -> акция «{promotion.title}» (id={promotion.id})")
                updated += 1
                continue

            new_url = await storage.save_file(file_path)
            promotion.banner = new_url
            updated += 1

        if not dry_run:
            await db.commit()

    print(
        f"{'Будет обновлено' if dry_run else 'Обновлено'}: {updated} баннеров. "
        f"Не сопоставлено: {len(unmatched)}, пропущено (не изображение): {skipped_non_image}."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Импорт баннеров акций из папки")
    parser.add_argument("source_dir", type=Path, help="Папка с файлами баннеров (по одному на акцию)")
    parser.add_argument("--dry-run", action="store_true", help="Показать, что будет сделано, ничего не меняя")
    args = parser.parse_args()

    if not args.source_dir.exists():
        raise SystemExit(f"Папка не найдена: {args.source_dir}")

    asyncio.run(import_promotion_banners(args.source_dir, args.dry_run))