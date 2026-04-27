"""Receipt helpers for totals and manual override operations."""

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.product import Product
from ..models.receipt_item import ReceiptItem
from ..models.session import Session
from ..schemas.session import OverrideRequest
from pipeline.prices import PRICES


async def _unit_price(db: AsyncSession, label: str) -> float:
    """Resolve item unit price from DB product catalog or fallback prices table."""
    result = await db.execute(select(Product).where(Product.label == label))
    product = result.scalar_one_or_none()
    if product:
        return float(product.price)
    return float(PRICES.get(label, 0.0))


async def compute_receipt_items(db: AsyncSession, session: Session) -> tuple[list[ReceiptItem], float]:
    """Return persisted receipt rows and recomputed total for a session."""
    result = await db.execute(select(ReceiptItem).where(ReceiptItem.session_id == session.id))
    items = result.scalars().all()
    total = round(sum(i.subtotal for i in items), 3)
    return items, total


async def apply_override(db: AsyncSession, session: Session, body: OverrideRequest) -> None:
    """Apply add/remove override and update session total."""
    if body.action not in {"add", "remove"}:
        raise ValueError("action must be 'add' or 'remove'")
    qty = max(1, body.qty)

    result = await db.execute(
        select(ReceiptItem).where(
            ReceiptItem.session_id == session.id,
            ReceiptItem.label == body.label,
        )
    )
    item = result.scalar_one_or_none()

    if body.action == "add":
        unit = await _unit_price(db, body.label)
        if item:
            item.qty += qty
            item.subtotal = round(item.qty * item.unit_price, 3)
            item.is_override = True
        else:
            db.add(
                ReceiptItem(
                    session_id=session.id,
                    label=body.label,
                    qty=qty,
                    unit_price=unit,
                    subtotal=round(unit * qty, 3),
                    is_override=True,
                )
            )
    else:
        if not item:
            return
        item.qty -= qty
        item.is_override = True
        if item.qty <= 0:
            await db.execute(delete(ReceiptItem).where(ReceiptItem.id == item.id))
        else:
            item.subtotal = round(item.qty * item.unit_price, 3)

    _, total = await compute_receipt_items(db, session)
    session.total = total