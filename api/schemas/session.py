from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class SessionStatus(str, Enum):
    processing = "processing"
    ready = "ready"
    confirmed = "confirmed"
    cancelled = "cancelled"


class ReceiptItemSchema(BaseModel):
    label: str
    qty: int
    unit_price: float
    subtotal: float
    is_override: bool = False
    confidence: float | None = None


class SessionResponse(BaseModel):
    id: str
    status: SessionStatus
    total: float
    frame_count: int
    model_version: str
    receipt_raw: dict | None = None
    receipt_items: list[ReceiptItemSchema] = []
    error: str | None = None
    created_at: datetime
    confirmed_at: datetime | None = None

    class Config:
        from_attributes = True


class OverrideRequest(BaseModel):
    action: str
    label: str
    qty: int = 1


class ConfirmRequest(BaseModel):
    session_id: str