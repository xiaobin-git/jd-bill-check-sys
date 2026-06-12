from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import Float
from datetime import datetime
from app.core.database import Base


class ERPOrder(Base):
    __tablename__ = "erp_orders"

    id = Column(Integer, primary_key=True, index=True)
    jd_order_no = Column(String, nullable=False, index=True)
    shop_name = Column(String, nullable=False)
    platform_type = Column(String)
    express_no = Column(String, index=True)
    system_order_no = Column(String)
    order_status = Column(String)
    refund_status = Column(String)
    customer_note = Column(String)
    payment_time = Column(DateTime)
    shipping_time = Column(DateTime)
    estimated_weight = Column(Float)
    actual_receipt = Column(Float)
    express_company = Column(String)
    package_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
