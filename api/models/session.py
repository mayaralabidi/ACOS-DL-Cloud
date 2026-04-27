import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Float, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base


class SessionStatus(str, enum.Enum):
    processing = "processing"
    ready = "ready"
    confirmed = "confirmed"
    cancelled = "cancelled"


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status: Mapped[SessionStatus] = mapped_column(Enum(SessionStatus), default=SessionStatus.processing)
    video_path: Mapped[str | None] = mapped_column(String, nullable=True)
    receipt_raw: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    receipt_final: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    total: Mapped[float] = mapped_column(Float, default=0.0)
    frame_count: Mapped[int] = mapped_column(Integer, default=0)
    model_version: Mapped[str] = mapped_column(String, default="unknown")
    error: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    receipt_items: Mapped[list["ReceiptItem"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )