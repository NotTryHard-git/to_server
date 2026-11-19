import json
import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from app.core.auth import require_client_key
from app.core.config import settings
from app.modules.inventory_prices.normalizer import Normalizer

logger = logging.getLogger("ellipse-sync")

router = APIRouter(prefix="/sync", tags=["inventory-prices"], dependencies=[Depends(require_client_key)])

normalizer = Normalizer.from_file(settings.FIELD_ALIASES_FILE)


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()[:64]
    return request.client.host[:64] if request.client else None


def _decode(body: bytes) -> str:
    """1С на Windows иногда шлёт cp1251, хотя заявляет UTF-8."""
    for encoding in ("utf-8-sig", "cp1251"):
        try:
            return body.decode(encoding)
        except UnicodeDecodeError:
            continue
    return body.decode("utf-8", errors="replace")


def _backend_headers() -> dict[str, str]:
    return {"X-Internal-Api-Key": settings.INTERNAL_API_KEY}


async def _post_backend(payload: dict) -> dict:
    transport = httpx.AsyncHTTPTransport(retries=2)  # повторы только при ошибках соединения
    async with httpx.AsyncClient(timeout=settings.BACKEND_TIMEOUT, transport=transport) as client:
        try:
            response = await client.post(
                f"{settings.BACKEND_BASE_URL}/internal/sync/inventory-prices",
                json=payload,
                headers=_backend_headers(),
            )
        except httpx.RequestError as exc:
            logger.error("backend unreachable: %s", exc)
            raise HTTPException(status_code=502, detail="Backend недоступен, повторите позже") from exc

    if response.status_code == 413:
        raise HTTPException(status_code=413, detail=response.json().get("detail", "Пачка слишком большая"))
    if response.status_code >= 400:
        # 401/503/422 здесь = ошибка конфигурации или баг, а не вина 1С: детали — в логах
        logger.error("backend returned %s: %s", response.status_code, response.text[:500])
        raise HTTPException(status_code=502, detail="Backend не принял данные, повторите позже")
    return response.json()


@router.post("/inventory-prices")
async def sync_inventory_prices(request: Request):
    """Принимает пачку остатков/цен от 1С, приводит к каноническому виду и пересылает
    в ellipse-back. Сама в БД не пишет — этим занимается backend."""
    body = await request.body()
    if len(body) > settings.MAX_BODY_BYTES:
        raise HTTPException(status_code=413, detail=f"Тело запроса больше {settings.MAX_BODY_BYTES} байт")

    text = _decode(body)
    client_ip = _client_ip(request)

    try:
        parsed = json.loads(text)
    except ValueError as exc:
        # Всё равно отправляем в backend — чтобы сырое тело попало в журнал для разбора
        await _post_backend(
            {"items": [], "error": f"Тело не является JSON: {exc}", "raw": text[:100_000], "client_ip": client_ip}
        )
        raise HTTPException(status_code=400, detail=f"Тело запроса не является корректным JSON: {exc}") from exc

    normalized = normalizer.normalize(parsed, settings.MAX_ITEMS)

    payload = {
        "items": normalized.items,
        "rejected": normalized.rejected[:1000],
        "batch_id": normalized.batch_id,
        "mode": normalized.mode,
        "final": normalized.final,
        "stores": normalized.stores,
        "raw": parsed,
        "client_ip": client_ip,
    }
    if normalized.error:
        payload.update(items=[], error=normalized.error)
        await _post_backend(payload)
        raise HTTPException(status_code=422, detail=normalized.error)

    result = await _post_backend(payload)
    result["warnings"] = dict(normalized.warnings)

    # Ни одна строка не принята, а отклонённые есть — это ошибка запроса, а не частичный успех
    if result.get("status") == "error" and normalized.rejected:
        return JSONResponse(status_code=422, content=result)
    return result


@router.get("/status")
async def sync_status():
    """Когда была последняя успешная синхронизация, сколько ошибок за сутки и т. д."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.get(
                f"{settings.BACKEND_BASE_URL}/internal/sync/status", headers=_backend_headers()
            )
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail="Backend недоступен") from exc
    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail="Backend не отдал статус")
    return response.json()
