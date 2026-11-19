# Развёртывание e'llipse на сервере

Всё работает в Docker. Нужен Linux-сервер (Ubuntu 22.04+, 2 vCPU / 2–4 ГБ RAM / 20+ ГБ диска достаточно), домен и доступ по SSH.

Структура на сервере (папки лежат рядом):

```
/opt/ellipse/
├── ellipse-back/    ├── ellipse-sync/    ├── ellipse-front/    └── ellipse-nginx/
```

## 0. Подготовка

1. Установите Docker и compose-плагин: <https://docs.docker.com/engine/install/ubuntu/>.
2. В DNS домена создайте A-записи на IP сервера: `example.com`, `www`, `api`, `sync` (вместо `example.com` — ваш домен).
3. Откройте порты 80 и 443 (`ufw allow 80,443/tcp`; 22 — для SSH). Порты 8000/8001/5432 наружу открывать **не нужно**.
4. Скопируйте проект на сервер в `/opt/ellipse`.

Сгенерировать секрет: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"` (нужно 4 разных: `INTERNAL_API_KEY`, `ADMIN_API_TOKEN`, `SYNC_API_KEY`, пароль БД).

## 1. ellipse-back (создаёт общую сеть `ellipse-network`)

```bash
cd /opt/ellipse/ellipse-back
cp .env.example .env && nano .env
```

Обязательно для продакшена:

| Переменная | Значение |
|---|---|
| `ENVIRONMENT` | `production` |
| `ENABLE_DOCS` | `false` |
| `POSTGRES_PASSWORD` | случайный пароль |
| `CORS_ORIGINS` | `["https://example.com","https://www.example.com"]` |
| `LOCAL_STORAGE_BASE_URL` | `https://api.example.com/media` |
| `INTERNAL_API_KEY`, `ADMIN_API_TOKEN` | разные случайные секреты ≥ 24 символов |
| `SYNC_STORE_RAW` | `all` на время запуска, потом `errors` |

С `ENVIRONMENT=production` приложение **не запустится** со слабыми секретами или localhost в настройках — в логе будет список проблем.

```bash
docker compose -f docker-compose.yml up -d --build
docker compose -f docker-compose.yml logs -f backend     # «alembic upgrade head», затем uvicorn
```

(`-f docker-compose.yml` обязателен: без него подмешается `docker-compose.override.yml` с `--reload` и открытыми портами — это для локальной разработки.)

Миграции применяются при старте контейнера автоматически.

## 2. ellipse-sync

```bash
cd /opt/ellipse/ellipse-sync
cp .env.example .env && nano .env
```

- `ENVIRONMENT=production`, `ENABLE_DOCS=false`
- `INTERNAL_API_KEY` — **тот же**, что в `ellipse-back/.env`
- `SYNC_API_KEY` — новый секрет; его вы передаёте специалисту 1С

```bash
docker compose -f docker-compose.yml up -d --build
```

## 3. Данные

Первичное наполнение (один раз; запускать внутри контейнера backend):

```bash
cd /opt/ellipse/ellipse-back
docker compose -f docker-compose.yml exec backend python scripts/seed_categories.py
docker compose -f docker-compose.yml exec backend python scripts/import_brands.py /app/scripts/brands.csv
# товары: подготовьте products_ready.csv пайплайном scripts/preprocess (см. scripts/preprocess/README.md)
docker compose -f docker-compose.yml cp products_ready.csv backend:/tmp/products_ready.csv
docker compose -f docker-compose.yml exec backend python scripts/import_products.py /tmp/products_ready.csv
```

GUID магазинов из 1С (нужны, чтобы остатки находили свой магазин):

```bash
docker compose -f docker-compose.yml exec backend python scripts/map_store_external_ids.py --export /tmp/stores.csv
docker compose -f docker-compose.yml cp backend:/tmp/stores.csv ./stores.csv
# заполните колонку external_id GUID-ами из 1С, затем:
docker compose -f docker-compose.yml cp ./stores.csv backend:/tmp/stores.csv
docker compose -f docker-compose.yml exec backend python scripts/map_store_external_ids.py --apply /tmp/stores.csv --dry-run
docker compose -f docker-compose.yml exec backend python scripts/map_store_external_ids.py --apply /tmp/stores.csv
```

## 4. Фронтенд и nginx (HTTPS)

```bash
cd /opt/ellipse/ellipse-nginx
cp .env.example .env && nano .env        # DOMAIN, LETSENCRYPT_EMAIL
./build-frontend.sh                       # собирает ../ellipse-front в ./frontend-dist
./init-letsencrypt.sh                     # один раз: выпуск сертификата и переход на HTTPS
```

Рекомендуется сначала `LETSENCRYPT_STAGING=1` (тестовый выпуск без лимитов), затем вернуть `0` и повторить — иначе можно упереться в лимиты Let's Encrypt.

Проверка:

```bash
curl -s https://api.example.com/health/ready
curl -s https://sync.example.com/health
curl -s -o /dev/null -w "%{http_code}\n" -X POST https://api.example.com/brands/   # ожидается 401 (нет токена)
```

## 5. Подключение 1С

Передайте программисту 1С: адрес `https://sync.example.com/sync/inventory-prices`, ключ `SYNC_API_KEY` и файл `docs/1C_INTEGRATION.md`. Проверка поступления: 

```bash
curl -H "Authorization: Bearer $ADMIN_API_TOKEN" https://api.example.com/admin/sync/status
curl -H "Authorization: Bearer $ADMIN_API_TOKEN" "https://api.example.com/admin/sync/unmatched"
```

`unmatched` показывает товары/склады, которые 1С прислала, а в базе их нет — сначала разберите их. Пока формат 1С уточняется, держите `SYNC_STORE_RAW=all` — в журнале сохраняется сырое тело запроса.

## 6. Обновление

```bash
cd /opt/ellipse/ellipse-back && git pull && docker compose -f docker-compose.yml up -d --build
cd ../ellipse-sync          && git pull && docker compose -f docker-compose.yml up -d --build
cd ../ellipse-nginx         && git -C ../ellipse-front pull && ./build-frontend.sh
```

Перед обновлением backend с миграциями сделайте бэкап (раздел 7).

## 7. Резервные копии

Сервис `backup` в compose backend делает `pg_dump` каждый день в `BACKUP_HOUR`:00, проверяет читаемость архива и хранит `BACKUP_KEEP_DAYS` дней в томе `db_backups`. Если заполнить `BACKUP_S3_*`, копия уходит ещё и в S3 (используйте **отдельный** бакет).

```bash
docker compose -f docker-compose.yml run --rm backup --once                       # дамп прямо сейчас
docker compose -f docker-compose.yml run --rm --entrypoint ls backup -lh /backups  # список

# Восстановление (заменяет текущие данные!)
docker compose -f docker-compose.yml stop backend
docker compose -f docker-compose.yml run --rm --entrypoint sh backup /scripts/restore.sh /backups/ellipse-ГГГГММДД-ЧЧММСС.dump
docker compose -f docker-compose.yml start backend
```

Медиафайлы (`media_data`), если `STORAGE_BACKEND=local`, в дамп не входят: копируйте том отдельно или переходите на S3.

## 8. Диагностика

- `docker compose ps`, `docker compose logs --tail=200 <сервис>`
- backend не стартует с `Небезопасная конфигурация…` — исправьте перечисленные в логе переменные
- сайт открывается, но нет данных — проверьте, что фронт собран с `VITE_API_BASE_URL=https://api.example.com` (сборка без неё теперь падает) и что `CORS_ORIGINS` содержит домен сайта
- 502 от nginx — сервис не запущен или не в сети `ellipse-network` (`docker network inspect ellipse-network`)
