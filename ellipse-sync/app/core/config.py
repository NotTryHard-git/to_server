from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_WEAK_SECRETS = {"", "change-me", "changeme", "secret", "password", "admin"}


class Settings(BaseSettings):
    PROJECT_NAME: str = "ellipse-sync"

    # production — приложение не стартует со слабыми/дефолтными секретами
    ENVIRONMENT: str = "development"
    ENABLE_DOCS: bool = False

    # Куда пересылать запросы после нормализации — internal API основного backend
    BACKEND_BASE_URL: str = "http://backend:8000"

    # Секрет «sync -> back». Тот же, что INTERNAL_API_KEY в ellipse-back/.env
    INTERNAL_API_KEY: str = ""

    # Секрет «1С -> sync». Его выдаём специалисту 1С. ОТДЕЛЬНЫЙ от INTERNAL_API_KEY:
    # утечка ключа 1С не должна открывать доступ к internal-API backend.
    SYNC_API_KEY: str = ""

    # Ограничения на входящий запрос от 1С
    MAX_BODY_BYTES: int = 5_000_000
    MAX_ITEMS: int = 2000
    BACKEND_TIMEOUT: float = 60.0

    # Необязательный JSON-файл с дополнительными именами полей от 1С, например:
    # {"product": ["КодТовара"], "quantity": ["КолВо"]} — дополняет встроенные.
    FIELD_ALIASES_FILE: str = ""

    SENTRY_DSN: str = ""
    LOG_LEVEL: str = "INFO"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @model_validator(mode="after")
    def _check_production(self) -> "Settings":
        if not self.is_production:
            return self
        problems = []
        for name in ("INTERNAL_API_KEY", "SYNC_API_KEY"):
            value = getattr(self, name)
            if value.lower() in _WEAK_SECRETS or len(value) < 24:
                problems.append(f"{name}: нужен случайный секрет от 24 символов")
        if self.INTERNAL_API_KEY and self.INTERNAL_API_KEY == self.SYNC_API_KEY:
            problems.append("INTERNAL_API_KEY и SYNC_API_KEY должны отличаться")
        if problems:
            raise ValueError(
                "Небезопасная конфигурация для ENVIRONMENT=production:\n  - "
                + "\n  - ".join(problems)
            )
        return self

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
