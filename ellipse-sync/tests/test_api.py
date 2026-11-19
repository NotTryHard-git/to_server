import base64
import json

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.modules.inventory_prices import router as sync_router

KEY = {"X-Api-Key": "test-sync-key"}
sent: list[dict] = []
backend_response = {"status": "ok", "updated": 1, "unmatched_products": [], "unmatched_stores": [],
                    "rejected": [], "received": 1}


@pytest.fixture(autouse=True)
def fake_backend(monkeypatch):
    sent.clear()

    async def fake_post(payload):
        sent.append(payload)
        return dict(backend_response)

    monkeypatch.setattr(sync_router, "_post_backend", fake_post)


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


async def test_auth_variants(client):
    body = {"items": [{"product_id": "p", "store_id": "s", "qty": 1}]}
    assert (await client.post("/sync/inventory-prices", json=body)).status_code == 401
    assert (await client.post("/sync/inventory-prices", json=body, headers={"X-Api-Key": "bad"})).status_code == 401
    assert (await client.post("/sync/inventory-prices", json=body, headers=KEY)).status_code == 200
    assert (await client.post("/sync/inventory-prices", json=body,
                              headers={"Authorization": "Bearer test-sync-key"})).status_code == 200
    basic = base64.b64encode("1c:test-sync-key".encode()).decode()
    assert (await client.post("/sync/inventory-prices", json=body,
                              headers={"Authorization": f"Basic {basic}"})).status_code == 200
    bad_basic = base64.b64encode("1c:wrong".encode()).decode()
    assert (await client.post("/sync/inventory-prices", json=body,
                              headers={"Authorization": f"Basic {bad_basic}"})).status_code == 401
    assert (await client.get("/health")).status_code == 200  # /health без ключа


async def test_normalized_payload_forwarded_with_raw(client):
    body = {"Остатки": [{"Номенклатура": "P1", "Склад": "S1", "Остаток": "3", "Цена": "10,5"}, {"мусор": 1}]}
    r = await client.post("/sync/inventory-prices", json=body, headers=KEY)
    assert r.status_code == 200
    payload = sent[0]
    assert payload["items"][0]["quantity"] == 3 and payload["items"][0]["price"] == "10.50"
    assert len(payload["rejected"]) == 1 and payload["raw"] == body
    assert r.json()["warnings"] == {}


async def test_not_json_is_logged_and_400(client):
    r = await client.post("/sync/inventory-prices", content=b"<xml/>", headers=KEY)
    assert r.status_code == 400
    assert sent[0]["error"].startswith("Тело не является JSON") and sent[0]["raw"] == "<xml/>"


async def test_cp1251_body_is_decoded(client):
    raw = json.dumps({"items": [{"product_id": "товар-1", "store_id": "s", "qty": 1}]}, ensure_ascii=False)
    r = await client.post("/sync/inventory-prices", content=raw.encode("cp1251"), headers=KEY)
    assert r.status_code == 200 and sent[0]["items"][0]["product_external_id"] == "товар-1"


async def test_batch_error_422_and_logged(client):
    r = await client.post("/sync/inventory-prices", json={"foo": 1}, headers=KEY)
    assert r.status_code == 422 and sent[0]["error"]


async def test_all_rows_rejected_is_422(client, monkeypatch):
    backend_response.update(status="error", updated=0)
    try:
        r = await client.post("/sync/inventory-prices", json=[{"x": 1}], headers=KEY)
        assert r.status_code == 422
    finally:
        backend_response.update(status="ok", updated=1)


async def test_body_too_large(client, monkeypatch):
    monkeypatch.setattr(sync_router.settings, "MAX_BODY_BYTES", 50)
    r = await client.post("/sync/inventory-prices", json={"items": [{"product_id": "p" * 100}]}, headers=KEY)
    assert r.status_code == 413


async def test_backend_down_is_502(client, monkeypatch):
    async def boom(payload):
        raise sync_router.HTTPException(status_code=502, detail="Backend недоступен, повторите позже")

    monkeypatch.setattr(sync_router, "_post_backend", boom)
    r = await client.post("/sync/inventory-prices", json=[{"product_id": "p", "store_id": "s", "qty": 1}], headers=KEY)
    assert r.status_code == 502
