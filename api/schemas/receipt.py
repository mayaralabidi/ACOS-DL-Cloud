from pydantic import BaseModel


class ReceiptItemOut(BaseModel):
    label: str
    qty: int
    unit_price: float
    subtotal: float
    is_override: bool = False


class ReceiptOut(BaseModel):
    items: list[ReceiptItemOut]
    total: float