import os

# Настройки для тестов — до импорта приложения
os.environ.setdefault("INTERNAL_API_KEY", "test-internal-key")
os.environ["SYNC_API_KEY"] = "test-sync-key"
os.environ["BACKEND_BASE_URL"] = "http://backend.test"
os.environ["ENVIRONMENT"] = "development"
