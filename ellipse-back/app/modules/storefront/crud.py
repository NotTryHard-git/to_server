import uuid
from decimal import Decimal

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.modules.catalog.models import (
    Brand,
    Category,
    Inventory,
    Product,
    ProductImage,
    ProductPrice,
)
from app.modules.promotions.models import Promotion, PromotionProduct
from app.modules.stores.models import Store

# storefront — сборочный модуль: агрегирует данные catalog, stores и promotions
# для готовых ответов фронтенду, поэтому кросс-модульные импорты здесь ожидаемы


def _first_image_subquery():
    """Первая картинка товара по sort_order."""
    return (
        select(ProductImage.product_id, ProductImage.image_url)
        .distinct(ProductImage.product_id)
        .order_by(ProductImage.product_id, ProductImage.sort_order)
        .subquery()
    )


def _latest_price_per_store_subquery():
    """Последняя цена по каждой паре (товар, магазин) — цена теперь за
    магазином, а не за товаром глобально."""
    return (
        select(
            ProductPrice.product_id,
            ProductPrice.store_id,
            ProductPrice.price,
            ProductPrice.currency,
        )
        .distinct(ProductPrice.product_id, ProductPrice.store_id)
        .order_by(
            ProductPrice.product_id,
            ProductPrice.store_id,
            ProductPrice.updated_at.desc(),
        )
        .subquery()
    )


async def get_descendant_category_ids(
    db: AsyncSession, root_id: uuid.UUID
) -> list[uuid.UUID]:
    """Id самой категории + всех её потомков на любую глубину (обход по уровням)."""
    ids: set[uuid.UUID] = {root_id}
    frontier = [root_id]

    while frontier:
        rows = (
            await db.execute(select(Category.id).where(Category.parent_id.in_(frontier)))
        ).scalars().all()
        new_ids = [row for row in rows if row not in ids]
        if not new_ids:
            break
        ids.update(new_ids)
        frontier = new_ids

    return list(ids)


async def _get_category_path(db: AsyncSession, category: Category | None) -> list[dict]:
    """Цепочка категорий от корня к текущей (включая её саму)."""
    path: list[dict] = []
    current = category

    while current is not None:
        path.append({"id": current.id, "name": current.name})
        if current.parent_id is None:
            break
        current = (
            await db.execute(select(Category).where(Category.id == current.parent_id))
        ).scalar_one_or_none()

    path.reverse()
    return path


async def get_product_catalog(
    db: AsyncSession,
    page: int,
    limit: int,
    search: str | None,
    category_id: uuid.UUID | None,
    brand_id: uuid.UUID | None,
    is_hit: bool | None,
    min_price: Decimal | None,
    max_price: Decimal | None,
    sort: str | None,
) -> tuple[list[dict], int]:
    image_subq = _first_image_subquery()

    select_columns = [
        Product.id,
        Product.name,
        Product.is_hit,
        Brand.name.label("brand_name"),
        image_subq.c.image_url,
    ]

    search_rank = None
    if search:
        tsvector = func.to_tsvector("russian", Product.name)
        tsquery = func.plainto_tsquery("russian", search)
        trgm_similarity = func.similarity(Product.name, search)

        search_rank = (
            func.coalesce(func.ts_rank(tsvector, tsquery), 0.0) + trgm_similarity
        ).label("search_rank")
        select_columns.append(search_rank)

    base_query = (
        select(*select_columns)
        .outerjoin(Brand, Product.brand_id == Brand.id)
        .outerjoin(image_subq, image_subq.c.product_id == Product.id)
        .where(Product.is_active.is_(True))
    )

    if search:
        base_query = base_query.where(
            or_(tsvector.op("@@")(tsquery), trgm_similarity > 0.15)
        )
    if category_id is not None:
        category_ids = await get_descendant_category_ids(db, category_id)
        base_query = base_query.where(Product.category_id.in_(category_ids))
    if brand_id is not None:
        base_query = base_query.where(Product.brand_id == brand_id)
    if is_hit is not None:
        base_query = base_query.where(Product.is_hit.is_(is_hit))
    if min_price is not None or max_price is not None:
        # Цена теперь за магазином: товар подходит, если ХОТЯ БЫ в одном
        # магазине его текущая цена попадает в диапазон.
        price_subq = _latest_price_per_store_subquery()
        conditions = [price_subq.c.product_id == Product.id]
        if min_price is not None:
            conditions.append(price_subq.c.price >= min_price)
        if max_price is not None:
            conditions.append(price_subq.c.price <= max_price)
        base_query = base_query.where(
            select(1).select_from(price_subq).where(and_(*conditions)).exists()
        )

    count_query = select(func.count()).select_from(base_query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    if search:
        base_query = base_query.order_by(search_rank.desc())
    else:
        base_query = base_query.order_by(Product.name)

    base_query = base_query.offset((page - 1) * limit).limit(limit)

    rows = (await db.execute(base_query)).all()
    items = [
        {
            "id": row.id,
            "name": row.name,
            "brand": row.brand_name,
            "image": row.image_url,
            "is_hit": row.is_hit,
        }
        for row in rows
    ]
    return items, total


async def get_product_hits(db: AsyncSession) -> list[dict]:
    image_subq = _first_image_subquery()

    query = (
        select(
            Product.id,
            Product.name,
            Brand.name.label("brand_name"),
            image_subq.c.image_url,
        )
        .outerjoin(Brand, Product.brand_id == Brand.id)
        .outerjoin(image_subq, image_subq.c.product_id == Product.id)
        .where(Product.is_active.is_(True), Product.is_hit.is_(True))
        .order_by(Product.name)
    )
    rows = (await db.execute(query)).all()
    return [
        {
            "id": row.id,
            "name": row.name,
            "image": row.image_url,
            "brand": row.brand_name,
        }
        for row in rows
    ]


async def get_product_detail(db: AsyncSession, product_id: uuid.UUID) -> dict | None:
    product_query = (
        select(Product)
        .options(joinedload(Product.brand), joinedload(Product.category))
        .where(Product.id == product_id)
    )
    product = (await db.execute(product_query)).unique().scalar_one_or_none()
    if product is None:
        return None

    images_query = (
        select(ProductImage.image_url)
        .where(ProductImage.product_id == product_id)
        .order_by(ProductImage.sort_order)
    )
    images = list((await db.execute(images_query)).scalars().all())

    # Объединённая таблица наличие+цена по магазинам: строим от Inventory
    # (магазин должен физически иметь товар в наличии, чтобы попасть в
    # таблицу), с подтягиванием актуальной цены этого магазина через LEFT
    # JOIN — если цену для магазина ещё не завели, будет просто null.
    price_subq = _latest_price_per_store_subquery()
    store_prices_query = (
        select(
            Inventory.store_id,
            Store.city,
            Store.address,
            Inventory.quantity,
            price_subq.c.price,
            price_subq.c.currency,
        )
        .select_from(Inventory)
        .join(Store, Store.id == Inventory.store_id)
        .outerjoin(
            price_subq,
            and_(
                price_subq.c.product_id == Inventory.product_id,
                price_subq.c.store_id == Inventory.store_id,
            ),
        )
        .where(Inventory.product_id == product_id, Inventory.quantity > 0)
    )
    store_prices_rows = (await db.execute(store_prices_query)).all()
    store_prices = [
        {
            "store_id": row.store_id,
            "store_name": ", ".join(part for part in (row.city, row.address) if part),
            "price": row.price,
            "currency": row.currency,
            "quantity": row.quantity,
        }
        for row in store_prices_rows
    ]

    promotions_query = (
        select(Promotion.id, Promotion.title)
        .join(PromotionProduct, PromotionProduct.promotion_id == Promotion.id)
        .where(
            PromotionProduct.product_id == product_id,
            Promotion.is_active.is_(True),
        )
    )
    promotions_rows = (await db.execute(promotions_query)).all()
    promotions = [{"id": row.id, "title": row.title} for row in promotions_rows]

    category_path = await _get_category_path(db, product.category)

    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "barcode": product.barcode,
        "brand": {"id": product.brand.id, "name": product.brand.name}
        if product.brand
        else None,
        "category": {"id": product.category.id, "name": product.category.name}
        if product.category
        else None,
        "category_path": category_path,
        "store_prices": store_prices,
        "images": images,
        "promotions": promotions,
    }


async def get_category_tree(db: AsyncSession) -> list[dict]:
    query = select(Category).order_by(Category.sort_order)
    categories = list((await db.execute(query)).scalars().all())

    nodes: dict[uuid.UUID, dict] = {
        c.id: {"id": c.id, "name": c.name, "children": []} for c in categories
    }
    roots: list[dict] = []

    for category in categories:
        node = nodes[category.id]
        if category.parent_id and category.parent_id in nodes:
            nodes[category.parent_id]["children"].append(node)
        else:
            roots.append(node)

    return roots