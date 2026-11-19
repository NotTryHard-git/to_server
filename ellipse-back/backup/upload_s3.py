"""Загружает файл дампа в S3 и удаляет в бакете копии старше BACKUP_KEEP_DAYS.

Переменные: BACKUP_S3_ENDPOINT_URL, BACKUP_S3_BUCKET, BACKUP_S3_ACCESS_KEY,
BACKUP_S3_SECRET_KEY, BACKUP_S3_PREFIX (по умолчанию "ellipse-db/"), BACKUP_KEEP_DAYS.
"""
import datetime as dt
import os
import sys

import boto3

path = sys.argv[1]
bucket = os.environ["BACKUP_S3_BUCKET"]
prefix = os.environ.get("BACKUP_S3_PREFIX", "ellipse-db/")
keep_days = int(os.environ.get("BACKUP_KEEP_DAYS", "14"))

s3 = boto3.client(
    "s3",
    endpoint_url=os.environ.get("BACKUP_S3_ENDPOINT_URL") or None,
    aws_access_key_id=os.environ["BACKUP_S3_ACCESS_KEY"],
    aws_secret_access_key=os.environ["BACKUP_S3_SECRET_KEY"],
    region_name=os.environ.get("BACKUP_S3_REGION", "ru-1"),
)

key = prefix + os.path.basename(path)
s3.upload_file(path, bucket, key)
print(f"[backup] загружено в s3://{bucket}/{key}")

cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=keep_days)
paginator = s3.get_paginator("list_objects_v2")
for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
    for obj in page.get("Contents", []):
        if obj["LastModified"] < cutoff:
            s3.delete_object(Bucket=bucket, Key=obj["Key"])
            print(f"[backup] удалён старый дамп s3://{bucket}/{obj['Key']}")
