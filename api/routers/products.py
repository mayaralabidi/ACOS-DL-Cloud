from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db
from ..models.product import Product
from ..schemas.product import ProductResponse

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductResponse])
async def list_products(db: AsyncSession = Depends(get_db)):
    """Return active product catalog from the database."""
    result = await db.execute(select(Product).where(Product.active.is_(True)).order_by(Product.label))
    return result.scalars().all()