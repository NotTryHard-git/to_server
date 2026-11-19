"""Проверки доступа: админ-токен для записи и общий ключ для internal-API."""
import secrets

from fastapi import Header, HTTPException, Request

from app.core.config import settings

WRITE_METHODS = {"POST", "PATCH", "PUT", "DELETE"}


def _bearer(authorization: str | None) -> str:
    scheme, _, value = (authorization or "").partition(" ")
    return value.strip() if scheme.lower() == "bearer" else ""


def _same(a: str, b: str) -> bool:
    return secrets.compare_digest(a.encode(), b.encode())


async def require_admin(authorization: str | None = Header(default=None)) -> None:
    """Проверяет "Authorization: Bearer <ADMIN_API_TOKEN>"."""
    if not settings.ADMIN_API_TOKEN:
        raise HTTPException(
            status_code=503, detail="Запись отключена: ADMIN_API_TOKEN не настроен"
        )
    if not _same(_bearer(authorization), settings.ADMIN_API_TOKEN):
        raise HTTPException(
            status_code=401,
            detail="Нужен токен администратора",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_admin_for_writes(
    request: Request, authorization: str | None = Header(default=None)
) -> None:
    """Зависимость на уровне роутера: GET остаётся публичным, любые методы записи
    требуют админ-токен. Новые POST/PATCH/DELETE-роуты защищаются автоматически."""
    if request.method in WRITE_METHODS:
        await require_admin(authorization)


async def verify_internal_api_key(
    x_internal_api_key: str | None = Header(default=None),
) -> None:
    if not settings.INTERNAL_API_KEY:
        raise HTTPException(
            status_code=503, detail="Internal API отключён: INTERNAL_API_KEY не настроен"
        )
    if not _same(x_internal_api_key or "", settings.INTERNAL_API_KEY):
        raise HTTPException(status_code=401, detail="Invalid internal API key")
