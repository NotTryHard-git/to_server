from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

# Значения, которые нельзя оставлять в продакшене
_WEAK_SECRETS = {"", "change-me", "changeme", "secret", "password", "admin"}


class Settings(BaseSettings):
    PROJECT_NAME: str = "ellipse-back"

    # development — локальная разработка (мягкие проверки)
    # production  — сервер: приложение НЕ СТАРТУЕТ с дефолтными/слабыми секретами
    ENVIRONMENT: str = "development"

    # Swagger UI (/docs) и /openapi.json. По умолчанию выключены.
    ENABLE_DOCS: bool = False

    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 10

    # --- Хранилище изображений ---
    # "local" — файлы лежат на диске backend-сервера, отдаются через /media
    # "s3"    — файлы лежат в S3-совместимом хранилище (например, Timeweb Cloud)
    STORAGE_BACKEND: str = "local"

    # Настройки для STORAGE_BACKEND=local
    LOCAL_STORAGE_DIR: str = "/mnt/media"
    LOCAL_STORAGE_BASE_URL: str = "http://localhost:8000/media"

    # Настройки для STORAGE_BACKEND=s3 (Timeweb Cloud S3 или совместимое)
    S3_ENDPOINT_URL: str = "https://s3.twcstorage.ru"
    S3_REGION: str = "ru-1"
    S3_BUCKET: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    # Публичный базовый URL для отдачи файлов: либо технический
    # (https://s3.twcstorage.ru/имя_бакета), либо привязанный домен
    # (https://img.example.ru)
    S3_PUBLIC_BASE_URL: str = ""

    # --- Доступы ---
    # Общий секрет между ellipse-sync и ellipse-back (заголовок X-Internal-Api-Key).
    # Пусто = internal-эндпоинты отключены (503).
    INTERNAL_API_KEY: str = ""

    # Токен администратора для всех методов записи (POST/PATCH/PUT/DELETE)
    # в каталоге, магазинах и акциях: заголовок "Authorization: Bearer <токен>".
    # Пусто = запись отключена (503), чтение остаётся публичным.
    ADMIN_API_TOKEN: str = ""

    # --- Синхронизация с 1С ---
    # Жёсткий лимит строк в одной пачке (защита от случайной «выгрузки всего за раз»)
    MAX_SYNC_BATCH_ITEMS: int = 2000
    # Когда сохранять в sync_log сырое тело запроса от 1С:
    #   all    — всегда (удобно в период запуска, когда формат 1С ещё уточняется)
    #   errors — только если были отклонённые строки / ошибка (по умолчанию)
    #   none   — никогда (в журнале остаются только счётчики)
    SYNC_STORE_RAW: str = "errors"

    # Мониторинг ошибок (необязательно). Пусто = Sentry выключен.
    SENTRY_DSN: str = ""
    LOG_LEVEL: str = "INFO"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def DATABASE_URL(self) -> str:
        # URL.create сам экранирует спецсимволы в логине/пароле
        return URL.create(
            "postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB,
        ).render_as_string(hide_password=False)

    @model_validator(mode="after")
    def _check_production(self) -> "Settings":
        if self.SYNC_STORE_RAW not in {"all", "errors", "none"}:
            raise ValueError("SYNC_STORE_RAW должен быть all, errors или none")
        if not self.is_production:
            return self

        problems: list[str] = []
        if self.INTERNAL_API_KEY.lower() in _WEAK_SECRETS or len(self.INTERNAL_API_KEY) < 24:
            problems.append("INTERNAL_API_KEY: нужен случайный секрет от 24 символов")
        if self.ADMIN_API_TOKEN.lower() in _WEAK_SECRETS or len(self.ADMIN_API_TOKEN) < 24:
            problems.append("ADMIN_API_TOKEN: нужен случайный секрет от 24 символов")
        if self.INTERNAL_API_KEY and self.INTERNAL_API_KEY == self.ADMIN_API_TOKEN:
            problems.append("INTERNAL_API_KEY и ADMIN_API_TOKEN должны отличаться")
        if self.POSTGRES_PASSWORD.lower() in _WEAK_SECRETS | {"ellipse"}:
            problems.append("POSTGRES_PASSWORD: слабый пароль базы данных")
        if any("localhost" in o or "127.0.0.1" in o for o in self.CORS_ORIGINS):
            problems.append("CORS_ORIGINS: в продакшене укажите домен сайта, а не localhost")
        if self.STORAGE_BACKEND == "local" and "localhost" in self.LOCAL_STORAGE_BASE_URL:
            problems.append("LOCAL_STORAGE_BASE_URL: укажите публичный адрес, а не localhost")
        if self.STORAGE_BACKEND == "s3" and not (
            self.S3_BUCKET and self.S3_ACCESS_KEY and self.S3_SECRET_KEY and self.S3_PUBLIC_BASE_URL
        ):
            problems.append("S3_*: для STORAGE_BACKEND=s3 заполните бакет, ключи и S3_PUBLIC_BASE_URL")
        if problems:
            raise ValueError(
                "Небезопасная конфигурация для ENVIRONMENT=production:\n  - "
                + "\n  - ".join(problems)
            )
        return self

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
