from pydantic import BaseModel


class ProductResponse(BaseModel):
    label: str
    name: str
    price: float
    active: bool
    category: str

    class Config:
        from_attributes = True