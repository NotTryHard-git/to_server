import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import require_admin, verify_internal_api_key
from app.modules.sync import crud
from app.modules.sync.schemas import InventoryPriceUpdateBatch, InventoryPriceUpdateResult

# Для ellipse-sync (общий секрет X-Internal-Api-Key)
router = APIRouter(
    prefix="/internal/sync", tags=["sync"], dependencies=[Depends(verify_internal_api_key)]
)
# Для администратора (Bearer-токен): журнал синхронизации и разбор «неизвестных» товаров
admin_router = APIRouter(
    prefix="/admin/sync", tags=["sync-admin"], dependencies=[Depends(require_admin)]
)


@router.post("/inventory-prices", response_model=InventoryPriceUpdateResult)
async def update_inventory_and_prices(
    batch: InventoryPriceUpdateBatch, db: AsyncSession = Depends(get_db)
):
    if len(batch.items) > settings.MAX_SYNC_BATCH_ITEMS:
        raise HTTPException(
            status_code=413,
            detail=f"В пачке {len(batch.items)} строк, максимум {settings.MAX_SYNC_BATCH_ITEMS}. "
            "Разбейте выгрузку на несколько запросов.",
        )
    started = time.perf_counter()
    try:
        return await crud.process_batch(db, batch)
    except Exception as exc:
        await db.rollback()
        # Сбой не должен пройти бесследно: фиксируем в журнале и отдаём 500
        try:
            await crud.write_error_log(db, batch, f"{type(exc).__name__}: {exc}", started)
        except Exception:  # noqa: BLE001 — журнал вторичен, исходная ошибка важнее
            await db.rollback()
        raise


@router.get("/status")
async def sync_status(db: AsyncSession = Depends(get_db)):
    return await crud.get_status(db)


@admin_router.get("/status")
async def admin_status(db: AsyncSession = Depends(get_db)):
    return await crud.get_status(db)


@admin_router.get("/log")
async def admin_log(
    limit: int = Query(50, ge=1, le=500),
    status: str | None = Query(None, pattern="^(ok|partial|error)$"),
    db: AsyncSession = Depends(get_db),
):
    return await crud.list_logs(db, limit=limit, status=status)


@admin_router.get("/log/{log_id}")
async def admin_log_item(log_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    row = await crud.get_log(db, log_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Запись журнала не найдена")
    return row


@admin_router.get("/unmatched")
async def admin_unmatched(
    kind: str | None = Query(None, pattern="^(product|store)$"),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    return await crud.list_unmatched(db, kind=kind, limit=limit)
