import pytest
from pydantic import ValidationError

from app.core.config import Settings
from tests.conftest import ADMIN, INTERNAL


async def test_reads_are_public(client):
    for path in ("/brands/", "/categories/", "/stores/", "/promotions/", "/api/products", "/api/products/hits"):
        assert (await client.get(path)).status_code == 200, path


async def test_writes_require_admin_token(client):
    body = {"name": "Бренд"}
    assert (await client.post("/brands/", json=body)).status_code == 401
    assert (await client.post("/brands/", json=body, headers={"Authorization": "Bearer wrong"})).status_code == 401
    assert (await client.post("/brands/", json=body, headers={"Authorization": "Basic test-admin-token"})).status_code == 401

    created = await client.post("/brands/", json=body, headers=ADMIN)
    assert created.status_code == 201
    brand_id = created.json()["id"]

    assert (await client.patch(f"/brands/{brand_id}", json={"name": "Х"})).status_code == 401
    assert (await client.delete(f"/brands/{brand_id}")).status_code == 401
    assert (await client.delete(f"/brands/{brand_id}", headers=ADMIN)).status_code == 204


async def test_every_write_route_is_protected(client):
    """Обходит ВСЕ зарегистрированные маршруты: любой метод записи без учётных данных
    обязан дать 401 (а не 422/201/404). Новые роуты попадают в проверку автоматически."""
    import uuid

    from app.main import app

    checked = 0
    for route in app.routes:
        methods = (getattr(route, "methods", None) or set()) & {"POST", "PATCH", "PUT", "DELETE"}
        for method in methods:
            path = route.path
            for param in ("{product_id}", "{brand_id}", "{category_id}", "{store_id}", "{image_id}",
                          "{promotion_id}", "{price_id}", "{log_id}"):
                path = path.replace(param, str(uuid.uuid4()))
            import re

            path = re.sub(r"\{[^}]+\}", str(uuid.uuid4()), path)
            response = await client.request(method, path, json={})
            assert response.status_code == 401, f"{method} {route.path} -> {response.status_code}"
            checked += 1
    assert checked >= 25


async def test_writes_disabled_without_configured_token(client, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "ADMIN_API_TOKEN", "")
    assert (await client.post("/brands/", json={"name": "x"}, headers=ADMIN)).status_code == 503


async def test_swagger_is_off_by_default(client):
    assert (await client.get("/docs")).status_code == 404
    assert (await client.get("/openapi.json")).status_code == 404


async def test_internal_api_key(client):
    body = {"items": []}
    url = "/internal/sync/inventory-prices"
    assert (await client.post(url, json=body)).status_code == 401
    assert (await client.post(url, json=body, headers={"X-Internal-Api-Key": "nope"})).status_code == 401
    assert (await client.post(url, json=body, headers=INTERNAL)).status_code == 200


async def test_internal_disabled_without_key(client, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "INTERNAL_API_KEY", "")
    assert (await client.post("/internal/sync/inventory-prices", json={"items": []}, headers=INTERNAL)).status_code == 503


async def test_admin_sync_endpoints_need_token(client):
    for path in ("/admin/sync/status", "/admin/sync/log", "/admin/sync/unmatched"):
        assert (await client.get(path)).status_code == 401
        assert (await client.get(path, headers=ADMIN)).status_code == 200


async def test_readiness(client):
    assert (await client.get("/health")).json() == {"status": "ok"}
    assert (await client.get("/health/ready")).json() == {"status": "ready"}


GOOD = dict(
    ENVIRONMENT="production",
    POSTGRES_HOST="postgres", POSTGRES_USER="u", POSTGRES_DB="d",
    POSTGRES_PASSWORD="Xk29!sdf0-Strong",
    INTERNAL_API_KEY="a" * 32, ADMIN_API_TOKEN="b" * 32,
    CORS_ORIGINS=["https://shop.example.ru"],
    LOCAL_STORAGE_BASE_URL="https://api.shop.example.ru/media",
)


def test_production_config_accepts_good_values():
    assert Settings(_env_file=None, **GOOD).is_production


@pytest.mark.parametrize(
    "override",
    [
        {"INTERNAL_API_KEY": "change-me"},
        {"INTERNAL_API_KEY": "short"},
        {"ADMIN_API_TOKEN": ""},
        {"ADMIN_API_TOKEN": "a" * 32},  # совпадает с INTERNAL_API_KEY
        {"POSTGRES_PASSWORD": "ellipse"},
        {"CORS_ORIGINS": ["http://localhost:5173"]},
        {"LOCAL_STORAGE_BASE_URL": "http://localhost:8000/media"},
        {"STORAGE_BACKEND": "s3"},
    ],
)
def test_production_config_rejects_weak_values(override):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **{**GOOD, **override})


def test_development_config_is_lenient():
    Settings(_env_file=None, POSTGRES_HOST="h", POSTGRES_USER="u", POSTGRES_PASSWORD="p", POSTGRES_DB="d")


def test_database_url_escapes_special_chars():
    s = Settings(_env_file=None, POSTGRES_HOST="h", POSTGRES_USER="u", POSTGRES_PASSWORD="p@ss/w:rd%", POSTGRES_DB="d")
    assert "p%40ss%2Fw%3Ard%25" in s.DATABASE_URL
