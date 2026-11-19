import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.storefront import crud
from app.modules.storefront.schemas import (
    CategoryTreeNode,
    ProductDetail,
    ProductHit,
    ProductListResponse,
)

router = APIRouter(prefix="/api/products", tags=["catalog-public"])


@router.get("/categories", response_model=list[CategoryTreeNode])
async def get_categories_tree(db: AsyncSession = Depends(get_db)):
    return await crud.get_category_tree(db)


@router.get("/hits", response_model=list[ProductHit])
async def get_products_hits(db: AsyncSession = Depends(get_db)):
    return await crud.get_product_hits(db)


@router.get("", response_model=ProductListResponse)
async def get_products_catalog(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    search: str | None = None,
    category_id: uuid.UUID | None = None,
    brand_id: uuid.UUID | None = None,
    is_hit: bool | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    sort: str | None = Query(default=None, pattern="^(price_asc|price_desc|name)$"),
    db: AsyncSession = Depends(get_db),
):
    items, total = await crud.get_product_catalog(
        db,
        page=page,
        limit=limit,
        search=search,
        category_id=category_id,
        brand_id=brand_id,
        is_hit=is_hit,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
    )
    pages = (total + limit - 1) // limit if total else 0
    return {"page": page, "pages": pages, "total": total, "items": items}


@router.get("/{product_id}", response_model=ProductDetail)
async def get_product_detail(product_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    product = await crud.get_product_detail(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product