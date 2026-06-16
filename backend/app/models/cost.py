from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.core.database import Base


class Cost(Base):
    __tablename__ = "costs"

    id = Column(Integer, primary_key=True, index=True)
    shop_name = Column(String, nullable=False)
    sku = Column(String, nullable=False, index=True)
    product_name = Column(String)
    cost = Column(Float, default=0.0)
    packaging_fee = Column(Float, default=0.5)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
