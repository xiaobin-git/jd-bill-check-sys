from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CostBase(BaseModel):
    shop_name: str
    sku: str
    product_name: Optional[str] = None
    cost: float = 0.0
    packaging_fee: float = 0.5


class CostCreate(CostBase):
    pass


class CostUpdate(CostBase):
    pass


class Cost(CostBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
