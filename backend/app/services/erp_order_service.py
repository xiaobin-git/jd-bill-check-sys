from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.erp_order import ERPOrder
from app.schemas.erp_order import ERPOrderCreate, ERPOrderUpdate


class ERPOrderService:
    def __init__(self, db: Session):
        self.db = db

    def get_orders(self, skip: int = 0, limit: int = 100, shop_name: Optional[str] = None) -> List[ERPOrder]:
        query = self.db.query(ERPOrder)
        if shop_name:
            query = query.filter(ERPOrder.shop_name.contains(shop_name))
        return query.order_by(ERPOrder.id.desc()).offset(skip).limit(limit).all()

    def count_orders(self, shop_name: Optional[str] = None) -> int:
        query = self.db.query(ERPOrder)
        if shop_name:
            query = query.filter(ERPOrder.shop_name.contains(shop_name))
        return query.count()

    def get_order(self, order_id: int) -> Optional[ERPOrder]:
        return self.db.query(ERPOrder).filter(ERPOrder.id == order_id).first()

    def create_order(self, order: ERPOrderCreate) -> ERPOrder:
        db_order = ERPOrder(**order.model_dump())
        self.db.add(db_order)
        self.db.commit()
        self.db.refresh(db_order)
        return db_order

    def create_orders_batch(self, orders: List[ERPOrderCreate]) -> List[ERPOrder]:
        db_orders = [ERPOrder(**order.model_dump()) for order in orders]
        self.db.add_all(db_orders)
        self.db.commit()
        for order in db_orders:
            self.db.refresh(order)
        return db_orders

    def update_order(self, order_id: int, order: ERPOrderUpdate) -> Optional[ERPOrder]:
        db_order = self.get_order(order_id)
        if db_order:
            for key, value in order.model_dump().items():
                setattr(db_order, key, value)
            self.db.commit()
            self.db.refresh(db_order)
        return db_order

    def delete_order(self, order_id: int) -> bool:
        db_order = self.get_order(order_id)
        if db_order:
            self.db.delete(db_order)
            self.db.commit()
            return True
        return False
