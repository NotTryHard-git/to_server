"""
Абстракция над хранением изображений — можно переключаться между локальным
диском и S3-совместимым хранилищем (например, Timeweb Cloud) через
переменную окружения STORAGE_BACKEND, не меняя код, который загружает файлы.
"""
import asyncio
import shutil
import uuid
from abc import ABC, abstractmethod
from pathlib import Path

from app.core.config import settings


class ImageStorage(ABC):
    @abstractmethod
    async def save_file(self, local_source_path: Path, filename: str | None = None) -> str:
        """Сохраняет файл в хранилище и возвращает публичный URL."""
        raise NotImplementedError


class LocalStorage(ImageStorage):
    """Хранит файлы на диске backend-сервера, отдаются через /media (см. main.py)."""

    def __init__(self, storage_dir: str, base_url: str):
        self.storage_dir = Path(storage_dir)
        self.base_url = base_url.rstrip("/")
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    async def save_file(self, local_source_path: Path, filename: str | None = None) -> str:
        filename = filename or local_source_path.name
        # На случай совпадения имён — не перезатираем чужой файл молча
        dest = self.storage_dir / filename
        if dest.exists() and dest.resolve() != local_source_path.resolve():
            filename = f"{uuid.uuid4().hex[:8]}-{filename}"
            dest = self.storage_dir / filename

        await asyncio.to_thread(shutil.copy2, local_source_path, dest)
        return f"{self.base_url}/{filename}"


class S3Storage(ImageStorage):
    """Хранит файлы в S3-совместимом хранилище (Timeweb Cloud и т.п.)."""

    def __init__(
        self,
        endpoint_url: str,
        region: str,
        bucket: str,
        access_key: str,
        secret_key: str,
        public_base_url: str,
    ):
        import boto3

        self.bucket = bucket
        self.public_base_url = public_base_url.rstrip("/")
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

    async def save_file(self, local_source_path: Path, filename: str | None = None) -> str:
        filename = filename or local_source_path.name
        key = f"products/{filename}"

        await asyncio.to_thread(
            self.client.upload_file,
            str(local_source_path),
            self.bucket,
            key,
            ExtraArgs={"ACL": "public-read"},
        )
        return f"{self.public_base_url}/{key}"


def get_storage() -> ImageStorage:
    if settings.STORAGE_BACKEND == "s3":
        return S3Storage(
            endpoint_url=settings.S3_ENDPOINT_URL,
            region=settings.S3_REGION,
            bucket=settings.S3_BUCKET,
            access_key=settings.S3_ACCESS_KEY,
            secret_key=settings.S3_SECRET_KEY,
            public_base_url=settings.S3_PUBLIC_BASE_URL,
        )
    return LocalStorage(
        storage_dir=settings.LOCAL_STORAGE_DIR,
        base_url=settings.LOCAL_STORAGE_BASE_URL,
    )