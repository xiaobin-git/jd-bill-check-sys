from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import List, Optional


class JDBillItemBase(BaseModel):
    order_no: str
    order_status: Optional[str] = None
    order_time: Optional[datetime] = None
    product_no: Optional[str] = None
    product_name: Optional[str] = None
    quantity: Optional[int] = None
    commission_type: Optional[str] = None
    commission_rate: Optional[float] = None
    fee_name: Optional[str] = None
    settlement_amount: Optional[float] = None
    currency: Optional[str] = None
    direction: Optional[str] = None
    settlement_status: Optional[str] = None
    fee_meaning: Optional[str] = None
    fee_description: Optional[str] = None


class JDBillItemCreate(JDBillItemBase):
    pass


class JDBillItemUpdate(JDBillItemBase):
    pass


class JDBillItem(JDBillItemBase):
    id: int
    jd_bill_id: int

    class Config:
        from_attributes = True


class JDBillBase(BaseModel):
    date_range: str
    shop_name: str

    @field_validator("date_range", "shop_name")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("不能为空")
        return value


class JDBillCreate(JDBillBase):
    pass


class JDBillUpdate(JDBillBase):
    pass


class JDBill(JDBillBase):
    id: int
    created_at: datetime
    items: List[JDBillItem] = []

    class Config:
        from_attributes = True
