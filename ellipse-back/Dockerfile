FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Не от root: каталог медиа создаём заранее, чтобы том media_data унаследовал владельца
RUN useradd --system --uid 10001 --home-dir /app app \
    && mkdir -p /mnt/media \
    && chown -R app:app /app /mnt/media
USER app

EXPOSE 8000

# Перед запуском применяет миграции (отключается RUN_MIGRATIONS=0)
ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]
# Без --reload: это боевой режим. Локально команда переопределяется в docker-compose.override.yml
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=*"]
