"""
Включает поиск товаров по словоформам и опечаткам:
    - full-text search (to_tsvector/ts_rank) — встроен в PostgreSQL,
      ничего дополнительно устанавливать не нужно;
    - pg_trgm — расширение PostgreSQL для поиска "по похожести"
      (прощает опечатки вида "тоналный" -> "тональный").

Создаёт два индекса на products.name, чтобы поиск не тормозил на большом
каталоге:
    - GIN по to_tsvector('russian', name) — под полнотекстовый поиск словоформ
    - GIN по name с gin_trgm_ops — под триграммный поиск (опечатки)

Идемпотентен — можно запускать сколько угодно раз (везде IF NOT EXISTS).

Запуск (из корня проекта):
    python scripts/setup_search.py
"""
import asyncio
import sys
from pathlib import Path

from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import engine

STATEMENTS = [
    "CREATE EXTENSION IF NOT EXISTS pg_trgm;",
    "CREATE INDEX IF NOT EXISTS ix_products_name_fts "
    "ON products USING gin (to_tsvector('russian', name));",
    "CREATE INDEX IF NOT EXISTS ix_products_name_trgm "
    "ON products USING gin (name gin_trgm_ops);",
]


async def setup_search() -> None:
    async with engine.begin() as conn:
        for statement in STATEMENTS:
            await conn.execute(text(statement))
    print("Готово: pg_trgm включён, индексы для поиска по товарам созданы.")


if __name__ == "__main__":
    asyncio.run(setup_search())