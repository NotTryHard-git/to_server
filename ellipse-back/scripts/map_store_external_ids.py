"""
Привязка магазинов сайта к складам 1С: заполняет stores.external_id.

Без этого синхронизация с 1С не сможет записать ни одного остатка: 1С присылает
GUID склада, а у магазинов на сайте external_id пока пустой.

Порядок:
    1. Выгрузить шаблон:
           python scripts/map_store_external_ids.py --export stores_map.csv
       Получится CSV: id, city, address, external_id (external_id пустой или текущий).
    2. Передать файл специалисту 1С / заполнить колонку external_id самим —
       GUID склада (или подразделения), соответствующего магазину.
    3. Проверить без записи:
           python scripts/map_store_external_ids.py --apply stores_map.csv --dry-run
    4. Применить:
           python scripts/map_store_external_ids.py --apply stores_map.csv

Строки с пустым external_id пропускаются. Если external_id уже занят другим
магазином — строка отклоняется (в базе стоит уникальный индекс), остальные применяются.
GUID приводится к нижнему регистру (как это делает ellipse-sync).
"""
import argparse
import asyncio
import csv
import re
import sys
from pathlib import Path

from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import async_session_maker
from app.modules.stores.models import Store

UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


def normalize(value: str) -> str:
    value = (value or "").strip().strip("{}").strip()
    return value.lower() if UUID_RE.match(value) else value


async def export(path: Path) -> None:
    async with async_session_maker() as db:
        stores = (await db.execute(select(Store).order_by(Store.city, Store.address))).scalars().all()
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "city", "address", "external_id"])
        for s in stores:
            writer.writerow([s.id, s.city or "", s.address or "", s.external_id or ""])
    print(f"Выгружено магазинов: {len(stores)} -> {path}")


async def apply(path: Path, dry_run: bool) -> None:
    updated = skipped = rejected = 0
    async with async_session_maker() as db:
        stores = {str(s.id): s for s in (await db.execute(select(Store))).scalars().all()}
        owners = {s.external_id: str(s.id) for s in stores.values() if s.external_id}
        with open(path, encoding="utf-8-sig", newline="") as f:
            for line, row in enumerate(csv.DictReader(f), start=2):
                store = stores.get((row.get("id") or "").strip())
                ext = normalize(row.get("external_id") or "")
                if store is None:
                    print(f"  строка {line}: магазин с id={row.get('id')!r} не найден")
                    rejected += 1
                    continue
                if not ext or ext == store.external_id:
                    skipped += 1
                    continue
                if owners.get(ext) not in (None, str(store.id)):
                    print(f"  строка {line}: external_id {ext} уже у другого магазина")
                    rejected += 1
                    continue
                if store.external_id:
                    owners.pop(store.external_id, None)
                store.external_id = ext
                owners[ext] = str(store.id)
                updated += 1
                print(f"  {store.city}, {store.address} -> {ext}")
        if dry_run:
            await db.rollback()
        else:
            await db.commit()
    mode = "ПРОБНЫЙ ПРОГОН (ничего не записано)" if dry_run else "записано"
    print(f"Готово, {mode}: обновлено {updated}, без изменений {skipped}, отклонено {rejected}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--export", type=Path, metavar="CSV")
    group.add_argument("--apply", type=Path, metavar="CSV")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    asyncio.run(export(args.export) if args.export else apply(args.apply, args.dry_run))


if __name__ == "__main__":
    main()
