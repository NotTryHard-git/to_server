import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.catalog.models import (
    Brand,
    Category,
    Inventory,
    Product,
    ProductImage,
    ProductPrice,
)
from app.modules.catalog.schemas import (
    BrandCreate,
    BrandUpdate,
    CategoryCreate,
    CategoryUpdate,
    InventoryCreate,
    InventoryUpdate,
    ProductCreate,
    ProductImageCreate,
    ProductImageUpdate,
    ProductPriceCreate,
    ProductPriceUpdate,
    ProductUpdate,
)


async def get_category(db: AsyncSession, category_id: uuid.UUID) -> Category | None:
    return await db.get(Category, category_id)


async def get_categories(db: AsyncSession) -> list[Category]:
    result = await db.execute(select(Category).order_by(Category.sort_order))
    return list(result.scalars().all())

async def create_category(db: AsyncSession, data: CategoryCreate) -> Category:
    category = Category(**data.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def update_category(
    db: AsyncSession, category: Category, data: CategoryUpdate
) -> Category:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    await db.commit()
    await db.refresh(category)
    return category


async def delete_category(db: AsyncSession, category: Category) -> None:
    await db.delete(category)
    await db.commit()


async def get_brand(db: AsyncSession, brand_id: uuid.UUID) -> Brand | None:
    return await db.get(Brand, brand_id)


async def get_brands(db: AsyncSession) -> list[Brand]:
    result = await db.execute(select(Brand).order_by(Brand.name))
    return list(result.scalars().all())


async def create_brand(db: AsyncSession, data: BrandCreate) -> Brand:
    brand = Brand(**data.model_dump())
    db.add(brand)
    await db.commit()
    await db.refresh(brand)
    return brand


async def update_brand(db: AsyncSession, brand: Brand, data: BrandUpdate) -> Brand:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(brand, field, value)
    await db.commit()
    await db.refresh(brand)
    return brand


async def delete_brand(db: AsyncSession, brand: Brand) -> None:
    await db.delete(brand)
    await db.commit()


async def get_product(db: AsyncSession, product_id: uuid.UUID) -> Product | None:
    return await db.get(Product, product_id)


async def get_products(
    db: AsyncSession,
    category_id: uuid.UUID | None = None,
    brand_id: uuid.UUID | None = None,
) -> list[Product]:
    query = select(Product)
    if category_id is not None:
        query = query.where(Product.category_id == category_id)
    if brand_id is not None:
        query = query.where(Product.brand_id == brand_id)
    result = await db.execute(query.order_by(Product.name))
    return list(result.scalars().all())


async def create_product(db: AsyncSession, data: ProductCreate) -> Product:
    product = Product(**data.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


async def update_product(
    db: AsyncSession, product: Product, data: ProductUpdate
) -> Product:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    await db.commit()
    await db.refresh(product)
    return product


async def delete_product(db: AsyncSession, product: Product) -> None:
    await db.delete(product)
    await db.commit()


async def get_product_image(
    db: AsyncSession, image_id: uuid.UUID
) -> ProductImage | None:
    return await db.get(ProductImage, image_id)


async def get_product_images(
    db: AsyncSession, product_id: uuid.UUID
) -> list[ProductImage]:
    query = (
        select(ProductImage)
        .where(ProductImage.product_id == product_id)
        .order_by(ProductImage.sort_order)
    )
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_product_image(
    db: AsyncSession, data: ProductImageCreate
) -> ProductImage:
    image = ProductImage(**data.model_dump())
    db.add(image)
    await db.commit()
    await db.refresh(image)
    return image


async def update_product_image(
    db: AsyncSession, image: ProductImage, data: ProductImageUpdate
) -> ProductImage:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(image, field, value)
    await db.commit()
    await db.refresh(image)
    return image


async def delete_product_image(db: AsyncSession, image: ProductImage) -> None:
    await db.delete(image)
    await db.commit()


async def get_product_price(
    db: AsyncSession, price_id: uuid.UUID
) -> ProductPrice | None:
    return await db.get(ProductPrice, price_id)


async def get_product_prices(
    db: AsyncSession, product_id: uuid.UUID
) -> list[ProductPrice]:
    query = select(ProductPrice).where(ProductPrice.product_id == product_id)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_product_price(
    db: AsyncSession, data: ProductPriceCreate
) -> ProductPrice:
    price = ProductPrice(**data.model_dump())
    db.add(price)
    await db.commit()
    await db.refresh(price)
    return price


async def update_product_price(
    db: AsyncSession, price: ProductPrice, data: ProductPriceUpdate
) -> ProductPrice:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(price, field, value)
    await db.commit()
    await db.refresh(price)
    return price


async def delete_product_price(db: AsyncSession, price: ProductPrice) -> None:
    await db.delete(price)
    await db.commit()


async def get_inventory_item(
    db: AsyncSession, product_id: uuid.UUID, store_id: uuid.UUID
) -> Inventory | None:
    return await db.get(Inventory, (product_id, store_id))


async def get_inventory(
    db: AsyncSession,
    product_id: uuid.UUID | None = None,
    store_id: uuid.UUID | None = None,
) -> list[Inventory]:
    query = select(Inventory)
    if product_id is not None:
        query = query.where(Inventory.product_id == product_id)
    if store_id is not None:
        query = query.where(Inventory.store_id == store_id)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_inventory_item(db: AsyncSession, data: InventoryCreate) -> Inventory:
    item = Inventory(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def update_inventory_item(
    db: AsyncSession, item: Inventory, data: InventoryUpdate
) -> Inventory:
    item.quantity = data.quantity
    await db.commit()
    await db.refresh(item)
    return item


async def delete_inventory_item(db: AsyncSession, item: Inventory) -> None:
    await db.delete(item)
    await db.commit()