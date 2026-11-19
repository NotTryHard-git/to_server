import time
from types import SimpleNamespace

import pytest
from sqlalchemy import func, select

from app.core.config import settings
from app.modules.catalog.models import Inventory, Product, ProductPrice
from app.modules.stores.models import Store
from app.modules.sync.models import SyncLog, SyncUnmatched
from tests.conftest import ADMIN, INTERNAL

URL = "/internal/sync/inventory-prices"


async def make_store(db, ext="store-1", city="Томск"):
    store = Store(external_id=ext, city=city, address=f"ул. {ext}")
    db.add(store)
    await db.commit()
    return SimpleNamespace(id=store.id)  # не ORM-объект: не «протухает» после expire_all


async def make_product(db, ext="prod-1", name="Крем"):
    product = Product(external_id=ext, name=name, is_hit=False, is_active=True)
    db.add(product)
    await db.commit()
    return SimpleNamespace(id=product.id)


def item(product="prod-1", store="store-1", **kw):
    return {"product_external_id": product, "store_external_id": store, **kw}


async def post(client, items=None, **extra):
    r = await client.post(URL, json={"items": items or [], **extra}, headers=INTERNAL)
    return r


async def qty(db, product, store):
    pid, sid = product.id, store.id  # до expire_all: после него атрибуты ORM-объектов «протухают»
    db.expire_all()
    row = (await db.execute(select(Inventory).where(Inventory.product_id == pid, Inventory.store_id == sid))).scalar_one_or_none()
    return None if row is None else row.quantity


async def price_rows(db, product, store):
    pid, sid = product.id, store.id
    db.expire_all()
    rows = (await db.execute(
        select(ProductPrice).where(ProductPrice.product_id == pid, ProductPrice.store_id == sid)
        .order_by(ProductPrice.updated_at)
    )).scalars().all()
    return rows


async def test_basic_update_and_old_payload_format(client, db):
    store, product = await make_store(db), await make_product(db)
    # «Старый» формат без batch_id/mode — как слал первый вариант sync-сервиса
    r = await post(client, [item(quantity=7, price="1290.50", old_price="1490.00", currency="RUB")])
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok" and data["updated"] == 1 and data["prices_inserted"] == 1
    assert data["unmatched_products"] == [] and data["unmatched_stores"] == []
    assert await qty(db, product, store) == 7
    rows = await price_rows(db, product, store)
    assert len(rows) == 1 and str(rows[0].price) == "1290.50" and str(rows[0].old_price) == "1490.00"


async def test_price_history_only_on_change(client, db):
    store, product = await make_store(db), await make_product(db)
    payload = [item(quantity=1, price="100.00")]
    assert (await post(client, payload)).json()["prices_inserted"] == 1
    again = (await post(client, payload)).json()
    assert again["prices_inserted"] == 0 and again["prices_unchanged"] == 1
    assert len(await price_rows(db, product, store)) == 1

    assert (await post(client, [item(quantity=1, price="110.00")])).json()["prices_inserted"] == 1
    assert (await post(client, [item(quantity=1, price="110.00", old_price="150.00")])).json()["prices_inserted"] == 1
    assert len(await price_rows(db, product, store)) == 3


async def test_partial_updates_do_not_touch_other_field(client, db):
    store, product = await make_store(db), await make_product(db)
    await post(client, [item(quantity=5, price="100.00")])

    await post(client, [item(price="120.00")])          # только цена
    assert await qty(db, product, store) == 5
    await post(client, [item(quantity=9)])               # только остаток
    assert await qty(db, product, store) == 9
    assert len(await price_rows(db, product, store)) == 2

    bad = await client.post(URL, json={"items": [item()]}, headers=INTERNAL)  # ни того ни другого
    assert bad.status_code == 422


async def test_unmatched_are_reported_and_tracked(client, db):
    store = await make_store(db)
    r = await post(client, [item("ghost", quantity=1), item("ghost", quantity=2), item("prod-x", store="no-store", quantity=1)])
    data = r.json()
    assert data["updated"] == 0 and data["unmatched_products"] == ["ghost", "prod-x"] and data["unmatched_stores"] == ["no-store"]

    await post(client, [item("ghost", quantity=1)])
    listing = (await client.get("/admin/sync/unmatched", headers=ADMIN)).json()
    assert listing["totals"] == {"product": 2, "store": 1}
    top = listing["items"][0]
    assert top["external_id"] == "ghost" and top["seen_count"] == 2 and top["sample"]["quantity"] == 1

    # Товар появился на сайте — «неизвестным» быть перестал
    await make_product(db, "ghost", "Появился")
    assert (await client.get("/admin/sync/unmatched?kind=product", headers=ADMIN)).json()["totals"]["product"] == 1
    # ...и после следующей синхронизации запись удаляется совсем
    await post(client, [item("ghost", quantity=3)])
    db.expire_all()
    assert (await db.execute(select(func.count()).select_from(SyncUnmatched).where(SyncUnmatched.external_id == "ghost"))).scalar_one() == 0
    _ = store


async def test_duplicates_in_batch_last_wins(client, db):
    store, product = await make_store(db), await make_product(db)
    r = await post(client, [item(quantity=1, price="10.00"), item(quantity=8, price="20.00")])
    assert r.json()["updated"] == 1
    assert await qty(db, product, store) == 8
    assert str((await price_rows(db, product, store))[0].price) == "20.00"


async def test_full_sync_zeroes_missing_only_after_final(client, db):
    s1, s2 = await make_store(db, "s1"), await make_store(db, "s2")
    a, b, c = [await make_product(db, f"p{i}") for i in "abc"]
    await post(client, [item("pa", "s1", quantity=5), item("pb", "s1", quantity=5), item("pc", "s1", quantity=5),
                        item("pa", "s2", quantity=4)])

    # Выгрузка из двух пачек для магазина s1: pa и pb; pc не приходит
    first = await post(client, [item("pa", "s1", quantity=6)], batch_id="F1", mode="full")
    assert first.json()["zeroed"] == 0
    assert await qty(db, c, s1) == 5  # пока не final — ничего не обнуляем

    last = await post(client, [item("pb", "s1", quantity=7)], batch_id="F1", mode="full", final=True)
    assert last.json()["zeroed"] == 1
    assert await qty(db, a, s1) == 6 and await qty(db, b, s1) == 7
    assert await qty(db, c, s1) == 0        # отсутствовал в выгрузке
    assert await qty(db, a, s2) == 4        # другой магазин не затронут


async def test_full_sync_same_values_still_counts_as_seen(client, db):
    """Остаток не изменился — но товар в выгрузке был, обнулять его нельзя."""
    s1, p = await make_store(db, "s1"), await make_product(db, "pa")
    await post(client, [item("pa", "s1", quantity=5)])
    time.sleep(0.05)
    r = await post(client, [item("pa", "s1", quantity=5)], batch_id="F2", mode="full", final=True)
    assert r.json()["zeroed"] == 0 and await qty(db, p, s1) == 5


async def test_full_sync_empty_store_listed_explicitly(client, db):
    s1, p = await make_store(db, "s1"), await make_product(db, "pa")
    await post(client, [item("pa", "s1", quantity=5)])
    r = await post(client, [], batch_id="F3", mode="full", final=True, stores=["s1"])
    assert r.json()["zeroed"] == 1 and await qty(db, p, s1) == 0


async def test_full_mode_requires_batch_id(client):
    assert (await post(client, [], mode="full")).status_code == 422


async def test_batch_size_limit(client, db, monkeypatch):
    await make_store(db)
    monkeypatch.setattr(settings, "MAX_SYNC_BATCH_ITEMS", 2)
    r = await post(client, [item(f"p{i}", quantity=1) for i in range(3)])
    assert r.status_code == 413


async def test_log_counts_and_raw_policy(client, db, monkeypatch):
    await make_store(db), await make_product(db)
    raw = {"items": [{"x": 1}]}
    rejected = [{"index": 3, "reason": "нет поля товара", "row": {"x": 1}}]

    # Без проблем и политика "errors": сырое тело не пишем
    await post(client, [item(quantity=1)], raw=raw, batch_id="L1")
    # С отклонённой строкой — пишем
    await post(client, [item(quantity=2)], raw=raw, rejected=rejected, batch_id="L2")

    logs = {l["batch_id"]: l for l in (await client.get("/admin/sync/log", headers=ADMIN)).json()}
    assert logs["L1"]["status"] == "ok" and logs["L2"]["status"] == "partial"
    assert logs["L2"]["rejected_count"] == 1 and logs["L1"]["items_applied"] == 1

    full = (await client.get(f"/admin/sync/log/{logs['L2']['id']}", headers=ADMIN)).json()
    assert full["raw"] == raw and full["rejected"][0]["reason"] == "нет поля товара"
    assert (await client.get(f"/admin/sync/log/{logs['L1']['id']}", headers=ADMIN)).json()["raw"] is None

    monkeypatch.setattr(settings, "SYNC_STORE_RAW", "all")
    await post(client, [item(quantity=3)], raw=raw, batch_id="L3")
    monkeypatch.setattr(settings, "SYNC_STORE_RAW", "none")
    await post(client, [item(quantity=4)], raw=raw, rejected=rejected, batch_id="L4")
    logs = {l["batch_id"]: l for l in (await client.get("/admin/sync/log", headers=ADMIN)).json()}
    assert (await client.get(f"/admin/sync/log/{logs['L3']['id']}", headers=ADMIN)).json()["raw"] == raw
    assert (await client.get(f"/admin/sync/log/{logs['L4']['id']}", headers=ADMIN)).json()["raw"] is None


async def test_adapter_error_is_logged_as_error(client):
    r = await client.post(URL, json={"items": [], "error": "Тело не является JSON", "raw": "<xml/>"}, headers=INTERNAL)
    assert r.status_code == 200 and r.json()["status"] == "error"
    log = (await client.get("/admin/sync/log?status=error", headers=ADMIN)).json()[0]
    assert log["error"].startswith("Тело не является JSON")
    full = (await client.get(f"/admin/sync/log/{log['id']}", headers=ADMIN)).json()
    assert full["raw"] == "<xml/>"


async def test_all_rows_rejected_status_error(client):
    r = await post(client, [], rejected=[{"index": 0, "reason": "битая"}, {"index": 1, "reason": "битая"}])
    # ничего не применено, всё отклонено — это error, а не «ok»/«partial»
    assert r.json()["status"] == "error"


async def test_exception_is_logged_and_returns_500(client, db, monkeypatch):
    await make_store(db), await make_product(db)
    from app.modules.sync import crud

    async def boom(*a, **k):
        raise RuntimeError("упало")

    monkeypatch.setattr(crud, "_record_unmatched", boom)
    r = await post(client, [item(quantity=1)], batch_id="E1")
    assert r.status_code == 500
    db.expire_all()
    log = (await db.execute(select(SyncLog).where(SyncLog.batch_id == "E1"))).scalar_one()
    assert log.status == "error" and "упало" in log.error
    # откат: остаток из упавшей пачки не должен сохраниться
    assert (await db.execute(select(func.count()).select_from(Inventory))).scalar_one() == 0


async def test_status_endpoint(client, db):
    await make_store(db), await make_product(db)
    empty = (await client.get("/internal/sync/status", headers=INTERNAL)).json()
    assert empty["last_success_at"] is None and empty["last_24h"]["batches"] == 0

    await post(client, [item(quantity=1, price="5.00")], batch_id="S1")
    await post(client, [item("ghost", quantity=1)], batch_id="S2")
    status = (await client.get("/internal/sync/status", headers=INTERNAL)).json()
    assert status["minutes_since_last_success"] == 0
    assert status["last_24h"]["batches"] == 2 and status["last_24h"]["items_applied"] == 1
    assert status["unmatched"] == {"product": 1, "store": 0}


async def test_unique_external_id_enforced(db):
    from sqlalchemy.exc import IntegrityError

    await make_product(db, "dup")
    db.add(Product(external_id="dup", name="Дубль", is_hit=False, is_active=True))
    with pytest.raises(IntegrityError):
        await db.commit()
    await db.rollback()
    # Несколько товаров без external_id — можно
    db.add_all([Product(name="a", is_hit=False, is_active=True), Product(name="b", is_hit=False, is_active=True)])
    await db.commit()


async def test_large_batch_is_fast(client, db):
    store = await make_store(db)
    db.add_all([Product(external_id=f"bulk-{i}", name=f"Товар {i}", is_hit=False, is_active=True) for i in range(1500)])
    await db.commit()
    items = [item(f"bulk-{i}", quantity=i % 20, price=f"{100 + i}.00") for i in range(1500)]
    started = time.perf_counter()
    r = await post(client, items)
    elapsed = time.perf_counter() - started
    assert r.json()["updated"] == 1500 and r.json()["prices_inserted"] == 1500
    assert elapsed < 8, f"пачка из 1500 строк обработана за {elapsed:.1f} с"
    # повтор — ничего нового не пишется
    again = (await post(client, items)).json()
    assert again["prices_inserted"] == 0 and again["prices_unchanged"] == 1500
    _ = store
