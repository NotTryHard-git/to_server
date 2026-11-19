"""
Переводит product_prices на модель "цена за магазином" — добавляет store_id.

ВАЖНО — ломающее изменение данных:
Старые записи product_prices были привязаны только к товару (без магазина).
При новой концепции "у каждого магазина своя цена" эти записи не несут
корректного смысла — непонятно, какому магазину они принадлежали.

Этот скрипт:
    1. Добавляет колонку store_id (FK -> stores.id) в product_prices.
    2. УДАЛЯЕТ все существующие строки product_prices (они не привязаны
       к магазину и больше не соответствуют новой модели данных).
    3. Делает store_id обязательным полем (NOT NULL) и добавляет индекс
       на (product_id, store_id) для быстрого поиска цены.

После миграции цены нужно завести заново — по одному товару на магазин,
например через доработанный import_products.py / отдельный CSV с ценами
по магазинам (это отдельная задача, дай знать, если нужно её сделать).

Запуск (из корня проекта):
    python scripts/migrate_prices_to_stores.py
"""
import asyncio
import sys
from pathlib import Path

from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import engine

STATEMENTS = [
    # Добавляем колонку как nullable — иначе ALTER упадёт на существующих строках
    "ALTER TABLE product_prices ADD COLUMN IF NOT EXISTS store_id UUID REFERENCES stores(id);",
    # Старые цены без привязки к магазину больше не валидны — удаляем
    "DELETE FROM product_prices WHERE store_id IS NULL;",
    # Теперь можно сделать поле обязательным
    "ALTER TABLE product_prices ALTER COLUMN store_id SET NOT NULL;",
    "CREATE INDEX IF NOT EXISTS ix_product_prices_product_store "
    "ON product_prices (product_id, store_id);",
]


async def migrate() -> None:
    async with engine.begin() as conn:
        for statement in STATEMENTS:
            await conn.execute(text(statement))
    print("Готово: product_prices теперь привязана к store_id. Старые цены (без магазина) удалены.")


if __name__ == "__main__":
    asyncio.run(migrate())