from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from app.models.jd_bill import JDBill, JDBillItem
from app.schemas.jd_bill import JDBillCreate, JDBillUpdate, JDBillItemCreate, JDBillItemUpdate


class JDBillService:
    def __init__(self, db: Session):
        self.db = db

    def get_bills(
        self,
        skip: int = 0,
        limit: int = 100,
        date_range: Optional[str] = None,
        shop_name: Optional[str] = None,
    ) -> List[JDBill]:
        query = self.db.query(JDBill)
        if date_range:
            query = query.filter(JDBill.date_range == date_range)
        if shop_name:
            query = query.filter(JDBill.shop_name.contains(shop_name))
        return query.order_by(JDBill.id.desc()).offset(skip).limit(limit).all()

    def count_bills(self, date_range: Optional[str] = None, shop_name: Optional[str] = None) -> int:
        query = self.db.query(JDBill)
        if date_range:
            query = query.filter(JDBill.date_range == date_range)
        if shop_name:
            query = query.filter(JDBill.shop_name.contains(shop_name))
        return query.count()

    def get_distinct_shop_names(self) -> List[str]:
        rows = (
            self.db.query(JDBill.shop_name)
            .filter(JDBill.shop_name.isnot(None), JDBill.shop_name != "")
            .distinct()
            .all()
        )
        return sorted([row[0] for row in rows if row[0]])

    def get_bill(self, bill_id: int) -> Optional[JDBill]:
        return self.db.query(JDBill).filter(JDBill.id == bill_id).first()

    def create_bill(self, bill: JDBillCreate) -> JDBill:
        db_bill = JDBill(**bill.model_dump())
        self.db.add(db_bill)
        self.db.commit()
        self.db.refresh(db_bill)
        return db_bill

    def update_bill(self, bill_id: int, bill: JDBillUpdate) -> Optional[JDBill]:
        db_bill = self.get_bill(bill_id)
        if db_bill:
            for key, value in bill.model_dump().items():
                setattr(db_bill, key, value)
            self.db.commit()
            self.db.refresh(db_bill)
        return db_bill

    def delete_bill(self, bill_id: int) -> bool:
        db_bill = self.get_bill(bill_id)
        if db_bill:
            self.db.delete(db_bill)
            self.db.commit()
            return True
        return False

    def get_items(
        self,
        bill_id: int,
        skip: int = 0,
        limit: int = 100,
        order_no: Optional[str] = None,
        product_no: Optional[str] = None,
        fee_name: Optional[str] = None,
        direction: Optional[str] = None,
        product_name: Optional[str] = None,
    ) -> List[JDBillItem]:
        query = self.db.query(JDBillItem).filter(JDBillItem.jd_bill_id == bill_id)
        if order_no:
            query = query.filter(JDBillItem.order_no.contains(order_no))
        if product_no:
            query = query.filter(JDBillItem.product_no.contains(product_no))
        if fee_name:
            query = query.filter(JDBillItem.fee_name == fee_name)
        if direction:
            query = query.filter(JDBillItem.direction == direction)
        if product_name:
            query = query.filter(JDBillItem.product_name.contains(product_name))
        return query.order_by(JDBillItem.id.desc()).offset(skip).limit(limit).all()

    def count_items(
        self,
        bill_id: int,
        order_no: Optional[str] = None,
        product_no: Optional[str] = None,
        fee_name: Optional[str] = None,
        direction: Optional[str] = None,
        product_name: Optional[str] = None,
    ) -> int:
        query = self.db.query(JDBillItem).filter(JDBillItem.jd_bill_id == bill_id)
        if order_no:
            query = query.filter(JDBillItem.order_no.contains(order_no))
        if product_no:
            query = query.filter(JDBillItem.product_no.contains(product_no))
        if fee_name:
            query = query.filter(JDBillItem.fee_name == fee_name)
        if direction:
            query = query.filter(JDBillItem.direction == direction)
        if product_name:
            query = query.filter(JDBillItem.product_name.contains(product_name))
        return query.count()

    def get_item_filter_options(self, bill_id: int) -> Dict[str, List[str]]:
        fee_name_rows = (
            self.db.query(JDBillItem.fee_name)
            .filter(
                JDBillItem.jd_bill_id == bill_id,
                JDBillItem.fee_name.isnot(None),
                JDBillItem.fee_name != "",
            )
            .distinct()
            .all()
        )
        direction_rows = (
            self.db.query(JDBillItem.direction)
            .filter(
                JDBillItem.jd_bill_id == bill_id,
                JDBillItem.direction.isnot(None),
                JDBillItem.direction != "",
            )
            .distinct()
            .all()
        )
        return {
            "fee_names": sorted([row[0] for row in fee_name_rows if row[0]]),
            "directions": sorted([row[0] for row in direction_rows if row[0]]),
        }

    def create_item(self, bill_id: int, item: JDBillItemCreate) -> JDBillItem:
        db_item = JDBillItem(jd_bill_id=bill_id, **item.model_dump())
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def create_items_batch(self, bill_id: int, items: List[JDBillItemCreate]) -> List[JDBillItem]:
        db_items = [JDBillItem(jd_bill_id=bill_id, **item.model_dump()) for item in items]
        self.db.add_all(db_items)
        self.db.commit()
        for item in db_items:
            self.db.refresh(item)
        return db_items

    def update_item(self, item_id: int, item: JDBillItemUpdate) -> Optional[JDBillItem]:
        db_item = self.db.query(JDBillItem).filter(JDBillItem.id == item_id).first()
        if db_item:
            for key, value in item.model_dump().items():
                setattr(db_item, key, value)
            self.db.commit()
            self.db.refresh(db_item)
        return db_item

    def delete_item(self, item_id: int) -> bool:
        db_item = self.db.query(JDBillItem).filter(JDBillItem.id == item_id).first()
        if db_item:
            self.db.delete(db_item)
            self.db.commit()
            return True
        return False
