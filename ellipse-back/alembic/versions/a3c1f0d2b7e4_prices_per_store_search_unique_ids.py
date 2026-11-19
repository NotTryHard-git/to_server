"""prices per store, search indexes, unique external ids

Сводит в одну ревизию всё, что раньше применялось разовыми скриптами
(migrate_prices_to_stores.py, setup_search.py), плюс уникальность external_id
у товаров и магазинов (ключ синхронизации с 1С).

Ревизия ИДЕМПОТЕНТНА (IF NOT EXISTS / проверки): её безопасно применять и на
чистой базе, и на базе, где эти скрипты уже запускались вручную.

Revision ID: a3c1f0d2b7e4
Revises: 1f8ed7149428
Create Date: 2026-11-18 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "a3c1f0d2b7e4"
down_revision: Union[str, Sequence[str], None] = "1f8ed7149428"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _assert_no_duplicates(table: str) -> str:
    return f"""
    DO $$
    DECLARE n int;
    BEGIN
        SELECT count(*) INTO n FROM (
            SELECT external_id FROM {table}
            WHERE external_id IS NOT NULL
            GROUP BY external_id HAVING count(*) > 1
        ) d;
        IF n > 0 THEN
            RAISE EXCEPTION '{table}.external_id: найдено % повторяющихся значений - уберите дубли и повторите миграцию', n;
        END IF;
    END $$;
    """


def upgrade() -> None:
    # --- Цена за (товар, магазин) ---
    op.execute("ALTER TABLE product_prices ADD COLUMN IF NOT EXISTS store_id UUID")
    # Старые цены без магазина не имеют смысла в новой модели (как и в migrate_prices_to_stores.py)
    op.execute("DELETE FROM product_prices WHERE store_id IS NULL")
    op.execute("ALTER TABLE product_prices ALTER COLUMN store_id SET NOT NULL")
    op.execute(
        """
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'product_prices_store_id_fkey'
            ) THEN
                ALTER TABLE product_prices
                    ADD CONSTRAINT product_prices_store_id_fkey
                    FOREIGN KEY (store_id) REFERENCES stores(id);
            END IF;
        END $$;
        """
    )
    op.execute("DROP INDEX IF EXISTS ix_product_prices_product_store")
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_product_prices_latest "
        "ON product_prices (product_id, store_id, updated_at DESC)"
    )

    # --- Поиск: словоформы + опечатки ---
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_products_name_fts "
        "ON products USING gin (to_tsvector('russian', name))"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_products_name_trgm "
        "ON products USING gin (name gin_trgm_ops)"
    )

    # --- Ключ синхронизации с 1С: external_id уникален ---
    op.execute(_assert_no_duplicates("products"))
    op.execute(_assert_no_duplicates("stores"))
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_products_external_id "
        "ON products (external_id) WHERE external_id IS NOT NULL"
    )
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_stores_external_id "
        "ON stores (external_id) WHERE external_id IS NOT NULL"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_stores_external_id")
    op.execute("DROP INDEX IF EXISTS uq_products_external_id")
    op.execute("DROP INDEX IF EXISTS ix_products_name_trgm")
    op.execute("DROP INDEX IF EXISTS ix_products_name_fts")
    op.execute("DROP INDEX IF EXISTS ix_product_prices_latest")
    # Колонку store_id оставляем только если нужны данные: возврат к старой схеме
    # безвозвратно теряет привязку цен к магазинам
    op.execute("ALTER TABLE product_prices DROP CONSTRAINT IF EXISTS product_prices_store_id_fkey")
    op.execute("ALTER TABLE product_prices DROP COLUMN IF EXISTS store_id")
