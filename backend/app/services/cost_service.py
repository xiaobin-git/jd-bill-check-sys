from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.cost import Cost
from app.models.jd_bill import JDBillItem
from app.schemas.cost import CostCreate, CostUpdate


class CostService:
    def __init__(self, db: Session):
        self.db = db

    def _build_query(self, shop_name: Optional[str] = None, product_name: Optional[str] = None):
        query = self.db.query(Cost)
        if shop_name:
            query = query.filter(Cost.shop_name.contains(shop_name))
        if product_name:
            query = query.filter(Cost.product_name.contains(product_name))
        return query

    def get_costs(
        self,
        skip: int = 0,
        limit: int = 100,
        shop_name: Optional[str] = None,
        product_name: Optional[str] = None,
    ) -> List[Cost]:
        query = self._build_query(shop_name=shop_name, product_name=product_name)
        return query.order_by(Cost.id.desc()).offset(skip).limit(limit).all()

    def count_costs(self, shop_name: Optional[str] = None, product_name: Optional[str] = None) -> int:
        return self._build_query(shop_name=shop_name, product_name=product_name).count()

    def list_costs(self, shop_name: Optional[str] = None, product_name: Optional[str] = None) -> List[Cost]:
        return self._build_query(shop_name=shop_name, product_name=product_name).order_by(Cost.id.desc()).all()

    def get_cost(self, cost_id: int) -> Optional[Cost]:
        return self.db.query(Cost).filter(Cost.id == cost_id).first()

    def get_cost_by_sku(self, shop_name: str, sku: str) -> Optional[Cost]:
        return self.db.query(Cost).filter(Cost.shop_name == shop_name, Cost.sku == sku).first()

    def get_cost_by_global_sku(self, sku: str) -> Optional[Cost]:
        return self.db.query(Cost).filter(Cost.sku == sku).order_by(Cost.id.asc()).first()

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

    def import_costs_batch(self, costs: List[CostCreate]) -> List[Cost]:
        self._dedupe_existing_costs_by_sku()
        result = []
        for cost in costs:
            existing = self.get_cost_by_global_sku(cost.sku)
            if existing:
                existing.product_name = cost.product_name
                existing.cost = cost.cost
                existing.packaging_fee = cost.packaging_fee
                result.append(existing)
            else:
                db_cost = Cost(**cost.model_dump())
                self.db.add(db_cost)
                result.append(db_cost)
        self.db.commit()
        for item in result:
            self.db.refresh(item)
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

    def _dedupe_existing_costs_by_sku(self) -> None:
        rows = self.db.query(Cost).filter(Cost.sku.isnot(None), Cost.sku != "").order_by(Cost.sku.asc(), Cost.id.asc()).all()
        groups = {}
        for row in rows:
            groups.setdefault(row.sku, []).append(row)

        for sku_rows in groups.values():
            if len(sku_rows) <= 1:
                continue
            preferred = next((row for row in sku_rows if (row.cost or 0) > 0), sku_rows[0])
            for row in sku_rows:
                if row.id != preferred.id:
                    self.db.delete(row)

    def sync_from_jd_bills(self, shop_name: Optional[str] = None) -> int:
        self._dedupe_existing_costs_by_sku()
        query = self.db.query(JDBillItem)
        if shop_name:
            query = query.join(JDBillItem.bill).filter(JDBillItem.bill.has(shop_name=shop_name))

        items = query.order_by(JDBillItem.id.desc()).all()
        synced = 0
        existing_skus = {row[0] for row in self.db.query(Cost.sku).filter(Cost.sku.isnot(None), Cost.sku != "").all()}

        for item in items:
            sku = (item.product_no or "").strip() if item.product_no else ""
            if sku and item.bill and sku not in existing_skus:
                cost = Cost(
                    shop_name=item.bill.shop_name,
                    sku=sku,
                    product_name=item.product_name,
                    cost=0.0,
                    packaging_fee=0.5,
                )
                self.db.add(cost)
                existing_skus.add(sku)
                synced += 1

        self.db.commit()
        return synced
