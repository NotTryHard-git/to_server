import logging
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import require_admin_for_writes
from app.modules.catalog.router import router as catalog_router
from app.modules.promotions.router import router as promotions_router
from app.modules.storefront.router import router as storefront_router
from app.modules.stores.router import router as stores_router
from app.modules.sync.router import admin_router as sync_admin_router
from app.modules.sync.router import router as sync_router

logging.basicConfig(
    level=settings.LOG_LEVEL.upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

if settings.SENTRY_DSN:
    import sentry_sdk

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        send_default_pii=False,
        traces_sample_rate=0.0,
    )

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url=None,
    openapi_url="/openapi.json" if settings.ENABLE_DOCS else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Чтение (GET) публично, любые методы записи требуют "Authorization: Bearer <ADMIN_API_TOKEN>".
# Зависимость стоит на уровне роутера — новые POST/PATCH/DELETE защищаются автоматически.
admin_writes = [Depends(require_admin_for_writes)]
app.include_router(catalog_router, dependencies=admin_writes)
app.include_router(stores_router, dependencies=admin_writes)
app.include_router(promotions_router, dependencies=admin_writes)

app.include_router(storefront_router)  # публичный API витрины (только чтение)
app.include_router(sync_router)        # internal: ключ X-Internal-Api-Key
app.include_router(sync_admin_router)  # admin: журнал синхронизации, Bearer-токен

# При локальном хранилище отдаём файлы напрямую с диска backend-сервера.
# При STORAGE_BACKEND=s3 монтировать нечего — файлы отдаёт S3-хранилище напрямую.
if settings.STORAGE_BACKEND == "local":
    Path(settings.LOCAL_STORAGE_DIR).mkdir(parents=True, exist_ok=True)
    app.mount("/media", StaticFiles(directory=settings.LOCAL_STORAGE_DIR), name="media")


@app.get("/health")
async def health_check() -> dict:
    """Процесс жив (для балансировщика/мониторинга)."""
    return {"status": "ok"}


@app.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)) -> dict:
    """Процесс жив И база отвечает (для healthcheck в docker-compose)."""
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail="database unavailable") from exc
    return {"status": "ready"}
