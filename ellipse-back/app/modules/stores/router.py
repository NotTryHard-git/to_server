import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.stores import crud
from app.modules.stores.schemas import (
    StoreCreate,
    StoreImageCreate,
    StoreImageRead,
    StoreImageUpdate,
    StoreRead,
    StoreUpdate,
)

router = APIRouter(prefix="/stores", tags=["stores"])


@router.get("/", response_model=list[StoreRead])
async def list_stores(db: AsyncSession = Depends(get_db)):
    return await crud.get_stores_list(db)


@router.get("/{store_id}", response_model=StoreRead)
async def get_store(store_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    store = await crud.get_store_detail(db, store_id)
    if store is None:
        raise HTTPException(status_code=404, detail="Store not found")
    return store


@router.post("/", response_model=StoreRead, status_code=201)
async def create_store(data: StoreCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_store(db, data)


@router.patch("/{store_id}", response_model=StoreRead)
async def update_store(
    store_id: uuid.UUID, data: StoreUpdate, db: AsyncSession = Depends(get_db)
):
    store = await crud.get_store(db, store_id)
    if store is None:
        raise HTTPException(status_code=404, detail="Store not found")
    return await crud.update_store(db, store, data)


@router.delete("/{store_id}", status_code=204)
async def delete_store(store_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    store = await crud.get_store(db, store_id)
    if store is None:
        raise HTTPException(status_code=404, detail="Store not found")
    await crud.delete_store(db, store)


@router.get(
    "/{store_id}/images", response_model=list[StoreImageRead], tags=["store-images"]
)
async def list_store_images(store_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await crud.get_store_images(db, store_id)


@router.post(
    "/{store_id}/images",
    response_model=StoreImageRead,
    status_code=201,
    tags=["store-images"],
)
async def create_store_image(
    store_id: uuid.UUID, data: StoreImageCreate, db: AsyncSession = Depends(get_db)
):
    if data.store_id != store_id:
        raise HTTPException(status_code=400, detail="store_id mismatch")
    return await crud.create_store_image(db, data)


@router.patch(
    "/images/{image_id}", response_model=StoreImageRead, tags=["store-images"]
)
async def update_store_image(
    image_id: uuid.UUID, data: StoreImageUpdate, db: AsyncSession = Depends(get_db)
):
    image = await crud.get_store_image(db, image_id)
    if image is None:
        raise HTTPException(status_code=404, detail="Store image not found")
    return await crud.update_store_image(db, image, data)


@router.delete("/images/{image_id}", status_code=204, tags=["store-images"])
async def delete_store_image(image_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    image = await crud.get_store_image(db, image_id)
    if image is None:
        raise HTTPException(status_code=404, detail="Store image not found")
    await crud.delete_store_image(db, image)