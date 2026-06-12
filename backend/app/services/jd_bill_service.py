from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.jd_bill import JDBill, JDBillItem
from app.schemas.jd_bill import JDBillCreate, JDBillUpdate, JDBillItemCreate, JDBillItemUpdate


class JDBillService:
    def __init__(self, db: Session):
        self.db = db

    def get_bills(self, skip: int = 0, limit: int = 100) -> List[JDBill]:
        return self.db.query(JDBill).offset(skip).limit(limit).all()

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

    def get_items(self, bill_id: int, skip: int = 0, limit: int = 100) -> List[JDBillItem]:
        return self.db.query(JDBillItem).filter(JDBillItem.jd_bill_id == bill_id).offset(skip).limit(limit).all()

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
