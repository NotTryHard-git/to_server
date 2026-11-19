# Тот же major, что и у базы (postgres:17), чтобы pg_dump/pg_restore были совместимы
FROM postgres:17

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3-boto3 \
    && rm -rf /var/lib/apt/lists/*

COPY backup_loop.sh upload_s3.py restore.sh /scripts/

ENTRYPOINT ["sh", "/scripts/backup_loop.sh"]
