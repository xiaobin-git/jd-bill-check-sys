from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.cost import Cost
from app.models.jd_bill import JDBillItem
from app.schemas.cost import CostCreate, CostUpdate


class CostService:
    def __init__(self, db: Session):
        self.db = db

    def get_costs(self, skip: int = 0, limit: int = 100, shop_name: Optional[str] = None) -> List[Cost]:
        query = self.db.query(Cost)
        if shop_name:
            query = query.filter(Cost.shop_name == shop_name)
        return query.offset(skip).limit(limit).all()

    def get_cost(self, cost_id: int) -> Optional[Cost]:
        return self.db.query(Cost).filter(Cost.id == cost_id).first()

    def get_cost_by_sku(self, shop_name: str, sku: str) -> Optional[Cost]:
        return self.db.query(Cost).filter(Cost.shop_name == shop_name, Cost.sku == sku).first()

    def create_cost(self, cost: CostCreate) -> Cost:
        existing = self.get_cost_by_sku(cost.shop_name, cost.sku)
        if existing:
            return existing
        db_cost = Cost(**cost.model_dump())
        self.db.add(db_cost)
        self.db.commit()
        self.db.refresh(db_cost)
        return db_cost

    def create_costs_batch(self, costs: List[CostCreate]) -> List[Cost]:
        result = []
        for cost in costs:
            result.append(self.create_cost(cost))
        return result

    def update_cost(self, cost_id: int, cost: CostUpdate) -> Optional[Cost]:
        db_cost = self.get_cost(cost_id)
        if db_cost:
            for key, value in cost.model_dump().items():
                setattr(db_cost, key, value)
            self.db.commit()
            self.db.refresh(db_cost)
        return db_cost

    def delete_cost(self, cost_id: int) -> bool:
        db_cost = self.get_cost(cost_id)
        if db_cost:
            self.db.delete(db_cost)
            self.db.commit()
            return True
        return False

    def sync_from_jd_bills(self, shop_name: Optional[str] = None) -> int:
        query = self.db.query(JDBillItem)
        if shop_name:
            query = query.join(JDBillItem.bill).filter(JDBillItem.bill.has(shop_name=shop_name))
        
        items = query.all()
        synced = 0
        
        for item in items:
            if item.product_no and item.bill:
                existing = self.get_cost_by_sku(item.bill.shop_name, item.product_no)
                if not existing:
                    cost = Cost(
                        shop_name=item.bill.shop_name,
                        sku=item.product_no,
                        product_name=item.product_name,
                        cost=0.0
                    )
                    self.db.add(cost)
                    synced += 1
        
        self.db.commit()
        return synced
