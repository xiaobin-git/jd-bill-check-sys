from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.express_bill import ExpressBill
from app.schemas.express_bill import ExpressBillCreate, ExpressBillUpdate


class ExpressBillService:
    def __init__(self, db: Session):
        self.db = db

    def get_bills(self, skip: int = 0, limit: int = 100, carrier: Optional[str] = None) -> List[ExpressBill]:
        query = self.db.query(ExpressBill)
        if carrier:
            query = query.filter(ExpressBill.carrier.contains(carrier))
        return query.order_by(ExpressBill.id.desc()).offset(skip).limit(limit).all()

    def count_bills(self, carrier: Optional[str] = None) -> int:
        query = self.db.query(ExpressBill)
        if carrier:
            query = query.filter(ExpressBill.carrier.contains(carrier))
        return query.count()

    def get_distinct_carriers(self) -> List[str]:
        rows = (
            self.db.query(ExpressBill.carrier)
            .filter(ExpressBill.carrier.isnot(None), ExpressBill.carrier != "")
            .distinct()
            .all()
        )
        return sorted([row[0] for row in rows if row[0]])

    def get_bill(self, bill_id: int) -> Optional[ExpressBill]:
        return self.db.query(ExpressBill).filter(ExpressBill.id == bill_id).first()

    def create_bill(self, bill: ExpressBillCreate) -> ExpressBill:
        db_bill = ExpressBill(**bill.model_dump())
        self.db.add(db_bill)
        self.db.commit()
        self.db.refresh(db_bill)
        return db_bill

    def create_bills_batch(self, bills: List[ExpressBillCreate]) -> List[ExpressBill]:
        db_bills = [ExpressBill(**bill.model_dump()) for bill in bills]
        self.db.add_all(db_bills)
        self.db.commit()
        for bill in db_bills:
            self.db.refresh(bill)
        return db_bills

    def update_bill(self, bill_id: int, bill: ExpressBillUpdate) -> Optional[ExpressBill]:
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
