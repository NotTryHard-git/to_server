"""Журнал синхронизации с 1С.

sync_log       — одна строка на каждый принятый запрос (счётчики, статус,
                 при необходимости — сырое тело запроса для разбора формата);
sync_unmatched — товары/магазины из 1С, которых нет на сайте (с числом повторов);
sync_session   — «полная выгрузка» из нескольких пачек (mode=full), чтобы после
                 последней пачки обнулить остатки товаров, которых в выгрузке не было.
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SyncLog(Base):
    __tablename__ = "sync_log"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    received_at: Mapped[datetime] = mapped_column(server_default=func.now(), index=True)
    batch_id: Mapped[str | None] = mapped_column(String(100), index=True)
    mode: Mapped[str] = mapped_column(String(10), default="delta")
    is_final: Mapped[bool] = mapped_column(Boolean, default=False)
    # ok — всё применено; partial — часть строк отклонена; error — ничего не применено
    status: Mapped[str] = mapped_column(String(10), index=True)
    items_received: Mapped[int] = mapped_column(Integer, default=0)
    items_applied: Mapped[int] = mapped_column(Integer, default=0)
    prices_inserted: Mapped[int] = mapped_column(Integer, default=0)
    prices_unchanged: Mapped[int] = mapped_column(Integer, default=0)
    zeroed: Mapped[int] = mapped_column(Integer, default=0)
    unmatched_products: Mapped[int] = mapped_column(Integer, default=0)
    unmatched_stores: Mapped[int] = mapped_column(Integer, default=0)
    rejected_count: Mapped[int] = mapped_column(Integer, default=0)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    client_ip: Mapped[str | None] = mapped_column(String(64))
    error: Mapped[str | None] = mapped_column(Text)
    rejected: Mapped[list | None] = mapped_column(JSONB)
    raw: Mapped[dict | list | str | None] = mapped_column(JSONB)


class SyncUnmatched(Base):
    __tablename__ = "sync_unmatched"
    __table_args__ = (UniqueConstraint("kind", "external_id", name="uq_sync_unmatched_kind_ext"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    kind: Mapped[str] = mapped_column(String(10))  # product | store
    external_id: Mapped[str] = mapped_column(String(200))
    first_seen_at: Mapped[datetime] = mapped_column(server_default=func.now())
    last_seen_at: Mapped[datetime] = mapped_column(server_default=func.now())
    seen_count: Mapped[int] = mapped_column(Integer, default=1)
    sample: Mapped[dict | None] = mapped_column(JSONB)


class SyncSession(Base):
    __tablename__ = "sync_session"

    batch_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    started_at: Mapped[datetime] = mapped_column(server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column()
    store_ids: Mapped[list] = mapped_column(JSONB, default=list)
