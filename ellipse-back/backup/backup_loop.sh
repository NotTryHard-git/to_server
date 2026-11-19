#!/bin/sh
# Ежедневный дамп PostgreSQL. Работает как «cron» внутри контейнера.
#
# Переменные (из .env):
#   PGHOST/PGUSER/PGPASSWORD/PGDATABASE — задаются docker-compose
#   BACKUP_HOUR (03), BACKUP_KEEP_DAYS (14), BACKUP_ON_START (0)
#   BACKUP_S3_* — если задан BACKUP_S3_BUCKET, каждый дамп дополнительно уходит в S3
#
# Файлы: /backups/ellipse-YYYYmmdd-HHMMSS.dump (формат pg_dump -Fc, восстановление — restore.sh)
set -eu

BACKUP_DIR="${BACKUP_DIR:-/backups}"
BACKUP_HOUR="${BACKUP_HOUR:-03}"
KEEP_DAYS="${BACKUP_KEEP_DAYS:-14}"
mkdir -p "$BACKUP_DIR"

do_backup() {
    stamp=$(date +%Y%m%d-%H%M%S)
    file="$BACKUP_DIR/ellipse-$stamp.dump"
    echo "[backup] $(date -Iseconds) dump -> $file"
    if ! pg_dump -Fc -f "$file.tmp"; then
        echo "[backup] ОШИБКА: pg_dump не удался" >&2
        rm -f "$file.tmp"
        return 1
    fi
    # Проверяем, что архив читается, и только потом считаем его готовым
    if ! pg_restore -l "$file.tmp" > /dev/null; then
        echo "[backup] ОШИБКА: дамп повреждён" >&2
        rm -f "$file.tmp"
        return 1
    fi
    mv "$file.tmp" "$file"
    echo "[backup] готово: $(du -h "$file" | cut -f1)"

    if [ -n "${BACKUP_S3_BUCKET:-}" ]; then
        python3 /scripts/upload_s3.py "$file" || echo "[backup] ПРЕДУПРЕЖДЕНИЕ: загрузка в S3 не удалась" >&2
    fi

    # Удаляем локальные дампы старше KEEP_DAYS суток
    find "$BACKUP_DIR" -name 'ellipse-*.dump' -mtime +"$KEEP_DAYS" -print -delete
}

if [ "${BACKUP_ON_START:-0}" = "1" ] || [ "${1:-}" = "--once" ]; then
    do_backup || true
    [ "${1:-}" = "--once" ] && exit 0
fi

while true; do
    now=$(date +%s)
    target=$(date -d "today ${BACKUP_HOUR}:00" +%s)
    if [ "$target" -le "$now" ]; then
        target=$(date -d "tomorrow ${BACKUP_HOUR}:00" +%s)
    fi
    wait_s=$((target - now))
    echo "[backup] следующий дамп через ${wait_s} с (в ${BACKUP_HOUR}:00)"
    sleep "$wait_s"
    do_backup || true
done
