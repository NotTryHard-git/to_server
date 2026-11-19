#!/bin/sh
# Восстановление базы из дампа. ВНИМАНИЕ: полностью заменяет содержимое базы.
#
#   docker compose run --rm --entrypoint sh backup /scripts/restore.sh /backups/ellipse-20261118-030000.dump
#
# Перед восстановлением остановите backend:  docker compose stop backend
set -eu

file="${1:?Укажите файл дампа: restore.sh /backups/ellipse-....dump}"
[ -f "$file" ] || { echo "Нет файла $file" >&2; exit 1; }

echo "Восстанавливаю $file в базу $PGDATABASE на $PGHOST (текущие данные будут заменены)"
pg_restore --clean --if-exists --no-owner --dbname "$PGDATABASE" "$file"
echo "Готово. Запустите backend:  docker compose start backend"
