"""Интеграционные тесты на настоящем PostgreSQL.

Нужен доступный сервер Postgres: по умолчанию localhost:5433 (как в docker-compose.override.yml),
пользователь/пароль ellipse/ellipse. Тесты сами создают БД ellipse_test, накатывают на неё
`alembic upgrade head` (заодно проверяя миграции) и чистят таблицы между тестами.
Переопределить подключение можно переменными TEST_POSTGRES_HOST/PORT/USER/PASSWORD.
"""
import asyncio
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import asyncpg
import pytest

ROOT = Path(__file__).resolve().parent.parent
PG = {
    "host": os.environ.get("TEST_POSTGRES_HOST", "localhost"),
    "port": int(os.environ.get("TEST_POSTGRES_PORT", "5433")),
    "user": os.environ.get("TEST_POSTGRES_USER", "ellipse"),
    "password": os.environ.get("TEST_POSTGRES_PASSWORD", "ellipse"),
}
TEST_DB = "ellipse_test"

os.environ.update(
    POSTGRES_HOST=PG["host"],
    POSTGRES_PORT=str(PG["port"]),
    POSTGRES_USER=PG["user"],
    POSTGRES_PASSWORD=PG["password"],
    POSTGRES_DB=TEST_DB,
    ENVIRONMENT="development",
    ADMIN_API_TOKEN="test-admin-token",
    INTERNAL_API_KEY="test-internal-key",
    STORAGE_BACKEND="local",
    LOCAL_STORAGE_DIR=tempfile.mkdtemp(prefix="ellipse-media-"),
    SYNC_STORE_RAW="errors",
)


async def _recreate_db() -> None:
    conn = await asyncpg.connect(database="postgres", **PG)
    try:
        await conn.execute(f'DROP DATABASE IF EXISTS "{TEST_DB}" WITH (FORCE)')
        await conn.execute(f'CREATE DATABASE "{TEST_DB}"')
    finally:
        await conn.close()


@pytest.fixture(scope="session", autouse=True)
def _database():
    try:
        asyncio.run(_recreate_db())
    except OSError as exc:  # нет Postgres
        pytest.skip(f"PostgreSQL недоступен ({exc}); запустите контейнер postgres", allow_module_level=True)
    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=ROOT, check=True)


TABLES = (
    "sync_log, sync_unmatched, sync_session, promotion_products, promotions, product_prices, "
    "product_images, inventory, products, brands, categories, store_images, stores"
)


@pytest.fixture(autouse=True)
async def _clean():
    from app.core.database import engine
    from sqlalchemy import text

    async with engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE {TABLES} RESTART IDENTITY CASCADE"))
    yield


@pytest.fixture
async def client():
    from httpx import ASGITransport, AsyncClient

    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test"
    ) as c:
        yield c


@pytest.fixture
async def db():
    from app.core.database import async_session_maker

    async with async_session_maker() as session:
        yield session


ADMIN = {"Authorization": "Bearer test-admin-token"}
INTERNAL = {"X-Internal-Api-Key": "test-internal-key"}
