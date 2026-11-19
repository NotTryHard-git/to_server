import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.catalog import crud
from app.modules.catalog.schemas import (
    BrandCreate,
    BrandRead,
    BrandUpdate,
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    InventoryCreate,
    InventoryRead,
    InventoryUpdate,
    ProductCreate,
    ProductImageCreate,
    ProductImageRead,
    ProductImageUpdate,
    ProductPriceCreate,
    ProductPriceRead,
    ProductPriceUpdate,
    ProductRead,
    ProductUpdate,
)

router = APIRouter()

#КАТЕГОРИИ

@router.get("/categories/", response_model=list[CategoryRead], tags=["categories"])
async def list_categories(db: AsyncSession = Depends(get_db)):
    return await crud.get_categories(db)


@router.get("/categories/{category_id}", response_model=CategoryRead, tags=["categories"])
async def get_category(category_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    category = await crud.get_category(db, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/categories/", response_model=CategoryRead, status_code=201, tags=["categories"])
async def create_category(data: CategoryCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_category(db, data)


@router.patch("/categories/{category_id}", response_model=CategoryRead, tags=["categories"])
async def update_category(
    category_id: uuid.UUID, data: CategoryUpdate, db: AsyncSession = Depends(get_db)
):
    category = await crud.get_category(db, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return await crud.update_category(db, category, data)


@router.delete("/categories/{category_id}", status_code=204, tags=["categories"])
async def delete_category(category_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    category = await crud.get_category(db, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    await crud.delete_category(db, category)


#БРЕНДЫ

@router.get("/brands/", response_model=list[BrandRead], tags=["brands"])
async def list_brands(db: AsyncSession = Depends(get_db)):
    return await crud.get_brands(db)


@router.get("/brands/{brand_id}", response_model=BrandRead, tags=["brands"])
async def get_brand(brand_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    brand = await crud.get_brand(db, brand_id)
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand


@router.post("/brands/", response_model=BrandRead, status_code=201, tags=["brands"])
async def create_brand(data: BrandCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_brand(db, data)


@router.patch("/brands/{brand_id}", response_model=BrandRead, tags=["brands"])
async def update_brand(
    brand_id: uuid.UUID, data: BrandUpdate, db: AsyncSession = Depends(get_db)
):
    brand = await crud.get_brand(db, brand_id)
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    return await crud.update_brand(db, brand, data)


@router.delete("/brands/{brand_id}", status_code=204, tags=["brands"])
async def delete_brand(brand_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    brand = await crud.get_brand(db, brand_id)
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    await crud.delete_brand(db, brand)


#ТОВАРЫ

@router.get("/products/", response_model=list[ProductRead], tags=["products"])
async def list_products(
    category_id: uuid.UUID | None = None,
    brand_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await crud.get_products(db, category_id=category_id, brand_id=brand_id)


@router.get("/products/{product_id}", response_model=ProductRead, tags=["products"])
async def get_product(product_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    product = await crud.get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post(
    "/products/", response_model=ProductRead, status_code=201, tags=["products"]
)
async def create_product(data: ProductCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_product(db, data)


@router.patch("/products/{product_id}", response_model=ProductRead, tags=["products"])
async def update_product(
    product_id: uuid.UUID, data: ProductUpdate, db: AsyncSession = Depends(get_db)
):
    product = await crud.get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return await crud.update_product(db, product, data)


@router.delete("/products/{product_id}", status_code=204, tags=["products"])
async def delete_product(product_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    product = await crud.get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    await crud.delete_product(db, product)


#ИЗОБРАЖЕНИЯ


@router.get(
    "/products/{product_id}/images",
    response_model=list[ProductImageRead],
    tags=["product-images"],
)
async def list_product_images(
    product_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    return await crud.get_product_images(db, product_id)


@router.post(
    "/products/{product_id}/images",
    response_model=ProductImageRead,
    status_code=201,
    tags=["product-images"],
)
async def create_product_image(
    product_id: uuid.UUID,
    data: ProductImageCreate,
    db: AsyncSession = Depends(get_db),
):
    if data.product_id != product_id:
        raise HTTPException(status_code=400, detail="product_id mismatch")
    return await crud.create_product_image(db, data)


@router.patch(
    "/product-images/{image_id}",
    response_model=ProductImageRead,
    tags=["product-images"],
)
async def update_product_image(
    image_id: uuid.UUID, data: ProductImageUpdate, db: AsyncSession = Depends(get_db)
):
    image = await crud.get_product_image(db, image_id)
    if image is None:
        raise HTTPException(status_code=404, detail="Product image not found")
    return await crud.update_product_image(db, image, data)


@router.delete(
    "/product-images/{image_id}", status_code=204, tags=["product-images"]
)
async def delete_product_image(
    image_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    image = await crud.get_product_image(db, image_id)
    if image is None:
        raise HTTPException(status_code=404, detail="Product image not found")
    await crud.delete_product_image(db, image)


#ЦЕНЫ

@router.get(
    "/products/{product_id}/prices",
    response_model=list[ProductPriceRead],
    tags=["product-prices"],
)
async def list_product_prices(
    product_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    return await crud.get_product_prices(db, product_id)


@router.post(
    "/products/{product_id}/prices",
    response_model=ProductPriceRead,
    status_code=201,
    tags=["product-prices"],
)
async def create_product_price(
    product_id: uuid.UUID,
    data: ProductPriceCreate,
    db: AsyncSession = Depends(get_db),
):
    if data.product_id != product_id:
        raise HTTPException(status_code=400, detail="product_id mismatch")
    return await crud.create_product_price(db, data)


@router.patch(
    "/product-prices/{price_id}",
    response_model=ProductPriceRead,
    tags=["product-prices"],
)
async def update_product_price(
    price_id: uuid.UUID, data: ProductPriceUpdate, db: AsyncSession = Depends(get_db)
):
    price = await crud.get_product_price(db, price_id)
    if price is None:
        raise HTTPException(status_code=404, detail="Product price not found")
    return await crud.update_product_price(db, price, data)


@router.delete(
    "/product-prices/{price_id}", status_code=204, tags=["product-prices"]
)
async def delete_product_price(
    price_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    price = await crud.get_product_price(db, price_id)
    if price is None:
        raise HTTPException(status_code=404, detail="Product price not found")
    await crud.delete_product_price(db, price)


#ИНВЕНТАРЬ


@router.get("/inventory/", response_model=list[InventoryRead], tags=["inventory"])
async def list_inventory(
    product_id: uuid.UUID | None = None,
    store_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await crud.get_inventory(db, product_id=product_id, store_id=store_id)


@router.get(
    "/inventory/{product_id}/{store_id}",
    response_model=InventoryRead,
    tags=["inventory"],
)
async def get_inventory_item(
    product_id: uuid.UUID, store_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    item = await crud.get_inventory_item(db, product_id, store_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return item


@router.post(
    "/inventory/", response_model=InventoryRead, status_code=201, tags=["inventory"]
)
async def create_inventory_item(
    data: InventoryCreate, db: AsyncSession = Depends(get_db)
):
    return await crud.create_inventory_item(db, data)


@router.patch(
    "/inventory/{product_id}/{store_id}",
    response_model=InventoryRead,
    tags=["inventory"],
)
async def update_inventory_item(
    product_id: uuid.UUID,
    store_id: uuid.UUID,
    data: InventoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    item = await crud.get_inventory_item(db, product_id, store_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return await crud.update_inventory_item(db, item, data)


@router.delete(
    "/inventory/{product_id}/{store_id}", status_code=204, tags=["inventory"]
)
async def delete_inventory_item(
    product_id: uuid.UUID, store_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    item = await crud.get_inventory_item(db, product_id, store_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    await crud.delete_inventory_item(db, item)