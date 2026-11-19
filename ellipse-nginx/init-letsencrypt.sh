#!/usr/bin/env bash
# Первый запуск: выпускает сертификаты Let's Encrypt и переводит nginx на HTTPS.
# Выполняется ОДИН раз; дальше сертификаты продлевает контейнер certbot.
#
# Перед запуском: DNS уже указывает на сервер, порты 80/443 открыты,
# сеть ellipse-network существует (запущен ellipse-back), .env заполнен.
set -euo pipefail
cd "$(dirname "$0")"

[ -f .env ] || { echo "Нет .env — скопируйте .env.example и заполните" >&2; exit 1; }
set -a; . ./.env; set +a
: "${DOMAIN:?}" "${LETSENCRYPT_EMAIL:?}"

mkdir -p "${FRONTEND_DIST_PATH:-./frontend-dist}"
[ -f "${FRONTEND_DIST_PATH:-./frontend-dist}/index.html" ] \
  || echo "Внимание: сайт ещё не собран (./build-frontend.sh) — пока будет пустая страница"

echo "### 1. Временный конфиг (только HTTP) ###"
export NGINX_TEMPLATES=./nginx/templates/bootstrap
docker compose up -d --force-recreate nginx

echo "### 2. Запрашиваем сертификат для $DOMAIN, www, api, sync ###"
STAGING_ARG=""
[ "${LETSENCRYPT_STAGING:-0}" = "1" ] && STAGING_ARG="--staging"

docker compose run --rm --entrypoint certbot certbot certonly \
  --webroot -w /var/www/certbot \
  -d "$DOMAIN" -d "www.$DOMAIN" -d "api.$DOMAIN" -d "sync.$DOMAIN" \
  --email "$LETSENCRYPT_EMAIL" --agree-tos --no-eff-email --non-interactive \
  $STAGING_ARG

echo "### 3. Рабочий конфиг (HTTPS) ###"
export NGINX_TEMPLATES=./nginx/templates/full
docker compose up -d --force-recreate nginx
docker compose up -d certbot

echo "### Готово: https://$DOMAIN  https://api.$DOMAIN/health  https://sync.$DOMAIN/health ###"
echo "Дальше обычные запуски:  docker compose up -d"
