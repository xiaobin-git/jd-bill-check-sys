from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class JDBill(Base):
    __tablename__ = "jd_bills"

    id = Column(Integer, primary_key=True, index=True)
    date_range = Column(String, nullable=False)
    shop_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    items = relationship("JDBillItem", back_populates="bill", cascade="all, delete-orphan")


class JDBillItem(Base):
    __tablename__ = "jd_bill_items"

    id = Column(Integer, primary_key=True, index=True)
    jd_bill_id = Column(Integer, ForeignKey("jd_bills.id"), nullable=False)
    order_no = Column(String, nullable=False)
    order_status = Column(String)
    order_time = Column(DateTime)
    product_no = Column(String)
    product_name = Column(String)
    quantity = Column(Integer)
    commission_type = Column(String)
    commission_rate = Column(Float)
    fee_name = Column(String)
    settlement_amount = Column(Float)
    currency = Column(String)
    direction = Column(String)
    settlement_status = Column(String)
    fee_meaning = Column(String)
    fee_description = Column(String)

    bill = relationship("JDBill", back_populates="items")
