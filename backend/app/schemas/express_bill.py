from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ExpressBillBase(BaseModel):
    express_no: str
    address: Optional[str] = None
    weight: Optional[float] = None
    freight: Optional[float] = None
    carrier: Optional[str] = None


class ExpressBillCreate(ExpressBillBase):
    pass


class ExpressBillUpdate(ExpressBillBase):
    pass


class ExpressBill(ExpressBillBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
