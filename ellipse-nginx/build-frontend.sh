#!/usr/bin/env bash
# Собирает Vue-сайт (../ellipse-front) в ./frontend-dist через временный контейнер node —
# ставить Node на сервер не нужно. Запускать при каждом обновлении фронта.
set -euo pipefail
cd "$(dirname "$0")"
[ -f .env ] || { echo "Нет .env" >&2; exit 1; }
set -a; . ./.env; set +a

FRONT_DIR="${FRONT_DIR:-../ellipse-front}"
OUT="${FRONTEND_DIST_PATH:-./frontend-dist}"
API_URL="${VITE_API_BASE_URL:-https://api.${DOMAIN}}"

docker run --rm \
  -v "$(cd "$FRONT_DIR" && pwd)":/app -w /app \
  -e VITE_API_BASE_URL="$API_URL" \
  -e VITE_2GIS_API_KEY="${VITE_2GIS_API_KEY:-}" \
  node:22-alpine sh -c "npm ci && npm run build"

rm -rf "$OUT" && mkdir -p "$OUT"
cp -r "$FRONT_DIR"/dist/. "$OUT"/
echo "Сайт собран в $OUT (API: $API_URL). nginx подхватывает файлы без перезапуска."
