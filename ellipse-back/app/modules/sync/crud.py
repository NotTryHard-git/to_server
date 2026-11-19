import json
import time
import uuid
from collections import OrderedDict
from decimal import Decimal

from sqlalchemy import and_, delete, exists, func, or_, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.catalog.models import Inventory, Product, ProductPrice
from app.modules.stores.models import Store
from app.modules.sync.models import SyncLog, SyncSession, SyncUnmatched
from app.modules.sync.schemas import (
    InventoryPriceUpdateBatch,
    InventoryPriceUpdateItem,
)

CHUNK = 1000          # строк на один SQL-запрос
REPORT_LIMIT = 200    # сколько unmatched возвращать в ответе (в журнале — счётчики полностью)
UNMATCHED_STORE_LIMIT = 500  # сколько unmatched записывать в sync_unmatched за одну пачку
RAW_MAX_BYTES = 2_000_000
CENT = Decimal("0.01")


def _chunks(seq: list, size: int = CHUNK):
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


async def _resolve(db: AsyncSession, model, external_ids: set[str]) -> dict[str, uuid.UUID]:
    """external_id -> внутренний UUID, одним-двумя запросами по индексу."""
    found: dict[str, uuid.UUID] = {}
    for part in _chunks(sorted(external_ids)):
        rows = await db.execute(
            select(model.external_id, model.id).where(model.external_id.in_(part))
        )
        found.update({ext: pk for ext, pk in rows.all()})
    return found


def _q(value: Decimal | None) -> Decimal | None:
    return None if value is None else Decimal(value).quantize(CENT)


async def process_batch(db: AsyncSession, batch: InventoryPriceUpdateBatch) -> dict:
    started = time.perf_counter()

    # Пачка, которую ellipse-sync не смог разобрать: только пишем в журнал
    if batch.error:
        return await _finish(db, batch, started, status="error", error=batch.error)

    # Одна пара (товар, магазин) в пачке несколько раз — действует последняя строка
    unique: OrderedDict[tuple[str, str], InventoryPriceUpdateItem] = OrderedDict()
    for item in batch.items:
        unique[(item.product_external_id, item.store_external_id)] = item
    items = list(unique.values())

    products = await _resolve(db, Product, {i.product_external_id for i in items})
    stores = await _resolve(
        db, Store, {i.store_external_id for i in items} | set(batch.stores)
    )

    unmatched_products: OrderedDict[str, dict] = OrderedDict()
    unmatched_stores: OrderedDict[str, dict] = OrderedDict()
    matched: list[tuple[uuid.UUID, uuid.UUID, InventoryPriceUpdateItem]] = []
    for item in items:
        product_id = products.get(item.product_external_id)
        store_id = stores.get(item.store_external_id)
        if product_id is None:
            unmatched_products.setdefault(
                item.product_external_id, item.model_dump(mode="json")
            )
        if store_id is None:
            unmatched_stores.setdefault(item.store_external_id, item.model_dump(mode="json"))
        if product_id is not None and store_id is not None:
            matched.append((product_id, store_id, item))

    # --- Остатки: один INSERT ... ON CONFLICT на пачку; updated_at обновляем ВСЕГДА,
    #     даже если число не изменилось (это отметка «товар присутствовал в выгрузке»)
    inv_rows = [
        {"product_id": p, "store_id": s, "quantity": it.quantity}
        for p, s, it in matched
        if it.quantity is not None
    ]
    for part in _chunks(inv_rows):
        stmt = pg_insert(Inventory).values(part)
        await db.execute(
            stmt.on_conflict_do_update(
                index_elements=[Inventory.product_id, Inventory.store_id],
                set_={"quantity": stmt.excluded.quantity, "updated_at": func.now()},
            )
        )

    # --- Цены: новая запись только если цена (или старая цена/валюта) изменилась ---
    price_items = [(p, s, it) for p, s, it in matched if it.price is not None]
    inserted = unchanged = 0
    if price_items:
        latest: dict[tuple[uuid.UUID, uuid.UUID], tuple] = {}
        pids = sorted({p for p, _, _ in price_items})
        sids = sorted({s for _, s, _ in price_items})
        for pid_part in _chunks(pids):
            rows = await db.execute(
                select(
                    ProductPrice.product_id,
                    ProductPrice.store_id,
                    ProductPrice.price,
                    ProductPrice.old_price,
                    ProductPrice.currency,
                )
                .distinct(ProductPrice.product_id, ProductPrice.store_id)
                .where(ProductPrice.product_id.in_(pid_part), ProductPrice.store_id.in_(sids))
                .order_by(
                    ProductPrice.product_id, ProductPrice.store_id, ProductPrice.updated_at.desc()
                )
            )
            for pid, sid, price, old_price, currency in rows.all():
                latest[(pid, sid)] = (_q(price), _q(old_price), currency)

        new_rows = []
        for p, s, it in price_items:
            candidate = (_q(it.price), _q(it.old_price), it.currency)
            if latest.get((p, s)) == candidate:
                unchanged += 1
                continue
            new_rows.append(
                {
                    "product_id": p,
                    "store_id": s,
                    "price": candidate[0],
                    "old_price": candidate[1],
                    "currency": candidate[2],
                }
            )
        for part in _chunks(new_rows):
            await db.execute(pg_insert(ProductPrice).values([{**r, "id": uuid.uuid4()} for r in part]))
        inserted = len(new_rows)

    # --- Журнал «неизвестных» товаров/магазинов (чтобы их можно было разобрать) ---
    await _record_unmatched(db, "product", unmatched_products)
    await _record_unmatched(db, "store", unmatched_stores)
    matched_product_ext = [e for e in products if e not in unmatched_products]
    for part in _chunks(matched_product_ext):
        await db.execute(
            delete(SyncUnmatched).where(
                SyncUnmatched.kind == "product", SyncUnmatched.external_id.in_(part)
            )
        )
    matched_store_ext = list(stores)
    for part in _chunks(matched_store_ext):
        await db.execute(
            delete(SyncUnmatched).where(
                SyncUnmatched.kind == "store", SyncUnmatched.external_id.in_(part)
            )
        )

    # --- Полная выгрузка из нескольких пачек: обнуляем отсутствовавшее после последней ---
    zeroed = 0
    if batch.mode == "full":
        touched = {str(s) for _, s, _ in matched} | {
            str(stores[e]) for e in batch.stores if e in stores
        }
        session = await db.get(SyncSession, batch.batch_id)
        if session is None:
            session = SyncSession(batch_id=batch.batch_id, store_ids=sorted(touched))
            db.add(session)
            await db.flush()
            await db.refresh(session)
        else:
            session.store_ids = sorted(set(session.store_ids) | touched)
        if batch.final:
            if session.store_ids:
                result = await db.execute(
                    update(Inventory)
                    .where(
                        Inventory.store_id.in_([uuid.UUID(x) for x in session.store_ids]),
                        Inventory.quantity > 0,
                        Inventory.updated_at < session.started_at,
                    )
                    .values(quantity=0, updated_at=func.now())
                )
                zeroed = result.rowcount or 0
            session.finished_at = func.now()

    applied = len(matched)
    rejected = batch.rejected
    # ok — отклонённых нет; partial — часть строк применена; error — отклонено всё
    status = "ok" if not rejected else ("partial" if applied else "error")
    return await _finish(
        db,
        batch,
        started,
        status=status,
        applied=applied,
        inserted=inserted,
        unchanged=unchanged,
        zeroed=zeroed,
        unmatched_products=unmatched_products,
        unmatched_stores=unmatched_stores,
        received=len(batch.items) + len(rejected),
    )


async def _record_unmatched(db: AsyncSession, kind: str, found: OrderedDict[str, dict]) -> None:
    rows = [
        {"id": uuid.uuid4(), "kind": kind, "external_id": ext[:200], "seen_count": 1, "sample": sample}
        for ext, sample in list(found.items())[:UNMATCHED_STORE_LIMIT]
    ]
    for part in _chunks(rows):
        stmt = pg_insert(SyncUnmatched).values(part)
        await db.execute(
            stmt.on_conflict_do_update(
                index_elements=[SyncUnmatched.kind, SyncUnmatched.external_id],
                set_={
                    "seen_count": SyncUnmatched.seen_count + 1,
                    "last_seen_at": func.now(),
                    "sample": stmt.excluded.sample,
                },
            )
        )


def _raw_for_log(batch: InventoryPriceUpdateBatch, status: str) -> object | None:
    policy = settings.SYNC_STORE_RAW
    if batch.raw is None or policy == "none":
        return None
    if policy == "errors" and status == "ok":
        return None
    try:
        size = len(json.dumps(batch.raw, ensure_ascii=False, default=str))
    except (TypeError, ValueError):
        return {"unserializable": True}
    if size > RAW_MAX_BYTES:
        return {"truncated": True, "size_bytes": size}
    return batch.raw


async def _finish(
    db: AsyncSession,
    batch: InventoryPriceUpdateBatch,
    started: float,
    *,
    status: str,
    applied: int = 0,
    inserted: int = 0,
    unchanged: int = 0,
    zeroed: int = 0,
    unmatched_products: OrderedDict | None = None,
    unmatched_stores: OrderedDict | None = None,
    received: int | None = None,
    error: str | None = None,
) -> dict:
    unmatched_products = unmatched_products or OrderedDict()
    unmatched_stores = unmatched_stores or OrderedDict()
    received = len(batch.items) + len(batch.rejected) if received is None else received
    rejected_dump = [r.model_dump(mode="json") for r in batch.rejected[:100]] or None

    db.add(
        SyncLog(
            batch_id=batch.batch_id,
            mode=batch.mode,
            is_final=batch.final,
            status=status,
            items_received=received,
            items_applied=applied,
            prices_inserted=inserted,
            prices_unchanged=unchanged,
            zeroed=zeroed,
            unmatched_products=len(unmatched_products),
            unmatched_stores=len(unmatched_stores),
            rejected_count=len(batch.rejected),
            duration_ms=int((time.perf_counter() - started) * 1000),
            client_ip=batch.client_ip,
            error=error,
            rejected=rejected_dump,
            raw=_raw_for_log(batch, status),
        )
    )
    await db.commit()

    return {
        "status": status,
        "batch_id": batch.batch_id,
        "received": received,
        "updated": applied,
        "prices_inserted": inserted,
        "prices_unchanged": unchanged,
        "zeroed": zeroed,
        "unmatched_products": list(unmatched_products)[:REPORT_LIMIT],
        "unmatched_stores": list(unmatched_stores)[:REPORT_LIMIT],
        "rejected": batch.rejected[:REPORT_LIMIT],
    }


async def write_error_log(
    db: AsyncSession, batch: InventoryPriceUpdateBatch, error: str, started: float
) -> None:
    """Вызывается после rollback, если обработка упала с исключением."""
    await _finish(db, batch, started, status="error", error=error[:2000])


# ----------------------------------------------------------------------
# Мониторинг / разбор
# ----------------------------------------------------------------------

async def get_status(db: AsyncSession) -> dict:
    last_ok = (
        await db.execute(
            select(SyncLog)
            .where(SyncLog.status.in_(["ok", "partial"]))
            .order_by(SyncLog.received_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    last_any = (
        await db.execute(select(SyncLog).order_by(SyncLog.received_at.desc()).limit(1))
    ).scalar_one_or_none()
    now = (await db.execute(select(func.localtimestamp()))).scalar_one()  # naive, как столбцы received_at

    day = (
        await db.execute(
            select(
                func.count(),
                func.count().filter(SyncLog.status == "ok"),
                func.count().filter(SyncLog.status == "partial"),
                func.count().filter(SyncLog.status == "error"),
                func.coalesce(func.sum(SyncLog.items_applied), 0),
                func.coalesce(func.sum(SyncLog.prices_inserted), 0),
            ).where(SyncLog.received_at > func.now() - func.make_interval(0, 0, 0, 0, 24))
        )
    ).one()

    unmatched = await list_unmatched(db, limit=0)
    minutes = None
    if last_ok is not None:
        minutes = int((now - last_ok.received_at).total_seconds() // 60)
    return {
        "last_success_at": last_ok.received_at if last_ok else None,
        "minutes_since_last_success": minutes,
        "last_batch": _log_row(last_any) if last_any else None,
        "last_24h": {
            "batches": day[0],
            "ok": day[1],
            "partial": day[2],
            "error": day[3],
            "items_applied": int(day[4]),
            "prices_inserted": int(day[5]),
        },
        "unmatched": unmatched["totals"],
    }


def _log_row(row: SyncLog, *, full: bool = False) -> dict:
    data = {
        "id": str(row.id),
        "received_at": row.received_at,
        "batch_id": row.batch_id,
        "mode": row.mode,
        "final": row.is_final,
        "status": row.status,
        "items_received": row.items_received,
        "items_applied": row.items_applied,
        "prices_inserted": row.prices_inserted,
        "prices_unchanged": row.prices_unchanged,
        "zeroed": row.zeroed,
        "unmatched_products": row.unmatched_products,
        "unmatched_stores": row.unmatched_stores,
        "rejected_count": row.rejected_count,
        "duration_ms": row.duration_ms,
        "client_ip": row.client_ip,
        "error": row.error,
    }
    if full:
        data["rejected"] = row.rejected
        data["raw"] = row.raw
    return data


async def list_logs(db: AsyncSession, limit: int = 50, status: str | None = None) -> list[dict]:
    query = select(SyncLog).order_by(SyncLog.received_at.desc()).limit(min(limit, 500))
    if status:
        query = query.where(SyncLog.status == status)
    return [_log_row(r) for r in (await db.execute(query)).scalars().all()]


async def get_log(db: AsyncSession, log_id: uuid.UUID) -> dict | None:
    row = await db.get(SyncLog, log_id)
    return _log_row(row, full=True) if row else None


def _unresolved():
    """Условие «этого товара/магазина всё ещё нет на сайте»."""
    return or_(
        and_(
            SyncUnmatched.kind == "product",
            ~exists().where(Product.external_id == SyncUnmatched.external_id),
        ),
        and_(
            SyncUnmatched.kind == "store",
            ~exists().where(Store.external_id == SyncUnmatched.external_id),
        ),
    )


async def list_unmatched(
    db: AsyncSession, kind: str | None = None, limit: int = 100
) -> dict:
    totals_rows = (
        await db.execute(
            select(SyncUnmatched.kind, func.count()).where(_unresolved()).group_by(SyncUnmatched.kind)
        )
    ).all()
    totals = {"product": 0, "store": 0, **{k: n for k, n in totals_rows}}
    items: list[dict] = []
    if limit:
        query = (
            select(SyncUnmatched)
            .where(_unresolved())
            .order_by(SyncUnmatched.seen_count.desc(), SyncUnmatched.last_seen_at.desc())
            .limit(min(limit, 1000))
        )
        if kind:
            query = query.where(SyncUnmatched.kind == kind)
        items = [
            {
                "kind": r.kind,
                "external_id": r.external_id,
                "seen_count": r.seen_count,
                "first_seen_at": r.first_seen_at,
                "last_seen_at": r.last_seen_at,
                "sample": r.sample,
            }
            for r in (await db.execute(query)).scalars().all()
        ]
    return {"totals": totals, "items": items}
