from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base


class ReceiptItem(Base):
    __tablename__ = "receipt_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id", ondelete="CASCADE"))
    label: Mapped[str] = mapped_column(String)
    qty: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[float] = mapped_column(Float)
    subtotal: Mapped[float] = mapped_column(Float)
    is_override: Mapped[bool] = mapped_column(default=False)

    session: Mapped["Session"] = relationship(back_populates="receipt_items")