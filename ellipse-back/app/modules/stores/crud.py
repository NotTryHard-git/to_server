import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.stores.models import Store, StoreImage
from app.modules.stores.schemas import (
    StoreCreate,
    StoreImageCreate,
    StoreImageUpdate,
    StoreUpdate,
)


async def get_store(db: AsyncSession, store_id: uuid.UUID) -> Store | None:
    return await db.get(Store, store_id)


async def get_stores(db: AsyncSession) -> list[Store]:
    result = await db.execute(select(Store).order_by(Store.city))
    return list(result.scalars().all())


async def get_stores_list(db: AsyncSession) -> list[dict]:
    """Для чтения (GET /stores/) — с уже встроенными фото, без N+1 запросов."""
    stores = await get_stores(db)
    store_ids = [s.id for s in stores]

    images_by_store: dict[uuid.UUID, list[str]] = {sid: [] for sid in store_ids}
    if store_ids:
        rows = (
            await db.execute(
                select(StoreImage.store_id, StoreImage.image_url)
                .where(StoreImage.store_id.in_(store_ids))
                .order_by(StoreImage.store_id, StoreImage.sort_order)
            )
        ).all()
        for store_id, image_url in rows:
            images_by_store[store_id].append(image_url)

    return [_store_to_dict(store, images_by_store.get(store.id, [])) for store in stores]


async def get_store_detail(db: AsyncSession, store_id: uuid.UUID) -> dict | None:
    """Для чтения (GET /stores/{id}) — с уже встроенными фото."""
    store = await get_store(db, store_id)
    if store is None:
        return None
    images = await get_store_images(db, store_id)
    return _store_to_dict(store, [image.image_url for image in images])


def _store_to_dict(store: Store, images: list[str]) -> dict:
    return {
        "id": store.id,
        "external_id": store.external_id,
        "city": store.city,
        "address": store.address,
        "phone": store.phone,
        "working_hours": store.working_hours,
        "latitude": store.latitude,
        "longitude": store.longitude,
        "images": images,
    }


async def create_store(db: AsyncSession, data: StoreCreate) -> Store:
    store = Store(**data.model_dump())
    db.add(store)
    await db.commit()
    await db.refresh(store)
    return store


async def update_store(db: AsyncSession, store: Store, data: StoreUpdate) -> Store:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(store, field, value)
    await db.commit()
    await db.refresh(store)
    return store


async def delete_store(db: AsyncSession, store: Store) -> None:
    await db.delete(store)
    await db.commit()


async def get_store_image(db: AsyncSession, image_id: uuid.UUID) -> StoreImage | None:
    return await db.get(StoreImage, image_id)


async def get_store_images(db: AsyncSession, store_id: uuid.UUID) -> list[StoreImage]:
    query = (
        select(StoreImage)
        .where(StoreImage.store_id == store_id)
        .order_by(StoreImage.sort_order)
    )
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_store_image(db: AsyncSession, data: StoreImageCreate) -> StoreImage:
    image = StoreImage(**data.model_dump())
    db.add(image)
    await db.commit()
    await db.refresh(image)
    return image


async def update_store_image(
    db: AsyncSession, image: StoreImage, data: StoreImageUpdate
) -> StoreImage:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(image, field, value)
    await db.commit()
    await db.refresh(image)
    return image


async def delete_store_image(db: AsyncSession, image: StoreImage) -> None:
    await db.delete(image)
    await db.commit()