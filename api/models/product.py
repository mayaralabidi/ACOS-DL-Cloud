from sqlalchemy import Boolean, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base


class Product(Base):
    __tablename__ = "products"

    label: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    price: Mapped[float] = mapped_column(Float)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    category: Mapped[str] = mapped_column(String, default="general")