"""Проверка ключа 1С. 1С умеет по-разному — принимаем три способа:

    X-Api-Key: <ключ>
    Authorization: Bearer <ключ>
    Authorization: Basic base64(любой_логин:<ключ>)    — штатный способ для HTTP-сервисов 1С
"""
import base64
import binascii
import secrets

from fastapi import Header, HTTPException

from app.core.config import settings


def _extract_key(x_api_key: str | None, authorization: str | None) -> str:
    if x_api_key:
        return x_api_key.strip()
    scheme, _, value = (authorization or "").partition(" ")
    value = value.strip()
    if scheme.lower() == "bearer":
        return value
    if scheme.lower() == "basic":
        try:
            decoded = base64.b64decode(value, validate=True).decode("utf-8")
        except (binascii.Error, UnicodeDecodeError):
            return ""
        return decoded.partition(":")[2]
    return ""


async def require_client_key(
    x_api_key: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
) -> None:
    if not settings.SYNC_API_KEY:
        raise HTTPException(status_code=503, detail="SYNC_API_KEY не настроен на сервере")
    provided = _extract_key(x_api_key, authorization)
    if not secrets.compare_digest(provided.encode(), settings.SYNC_API_KEY.encode()):
        raise HTTPException(
            status_code=401,
            detail="Неверный или отсутствующий ключ доступа",
            headers={"WWW-Authenticate": 'Basic realm="ellipse-sync", Bearer'},
        )
