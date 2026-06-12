from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.core.database import Base


class ExpressBill(Base):
    __tablename__ = "express_bills"

    id = Column(Integer, primary_key=True, index=True)
    express_no = Column(String, nullable=False, index=True)
    address = Column(String)
    created_time = Column(DateTime)
    weight = Column(Float)
    volume = Column(Float)
    freight = Column(Float)
    carrier = Column(String)
    created_at = Column(DateTime, default=datetime.now)
