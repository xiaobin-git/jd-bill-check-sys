from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ERPOrderBase(BaseModel):
    jd_order_no: str
    shop_name: str
    platform_type: Optional[str] = None
    express_no: Optional[str] = None
    system_order_no: Optional[str] = None
    order_status: Optional[str] = None
    refund_status: Optional[str] = None
    customer_note: Optional[str] = None
    payment_time: Optional[datetime] = None
    shipping_time: Optional[datetime] = None
    estimated_weight: Optional[float] = None
    actual_receipt: Optional[float] = None
    express_company: Optional[str] = None
    package_count: Optional[int] = None


class ERPOrderCreate(ERPOrderBase):
    pass


class ERPOrderUpdate(ERPOrderBase):
    pass


class ERPOrder(ERPOrderBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
