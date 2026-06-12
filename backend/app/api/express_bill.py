from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.express_bill import ExpressBill, ExpressBillCreate, ExpressBillUpdate
from app.services.express_bill_service import ExpressBillService
from app.utils.csv_parser import parse_generic_file

router = APIRouter(prefix="/api/express-bills", tags=["快递账单"])


@router.get("", response_model=List[ExpressBill])
def get_bills(skip: int = 0, limit: int = 100, carrier: Optional[str] = None, db: Session = Depends(get_db)):
    service = ExpressBillService(db)
    return service.get_bills(skip=skip, limit=limit, carrier=carrier)


@router.get("/{bill_id}", response_model=ExpressBill)
def get_bill(bill_id: int, db: Session = Depends(get_db)):
    service = ExpressBillService(db)
    bill = service.get_bill(bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="账单不存在")
    return bill


@router.post("", response_model=ExpressBill)
def create_bill(bill: ExpressBillCreate, db: Session = Depends(get_db)):
    service = ExpressBillService(db)
    return service.create_bill(bill)


@router.post("/upload")
async def upload_bills(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    try:
        data = parse_generic_file(content, file.filename or "")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    
    service = ExpressBillService(db)
    bills = []
    for item in data:
        mapped = {
            "express_no": item.get("快递单号") or item.get("express_no"),
            "address": item.get("收货地址") or item.get("address"),
            "weight": item.get("重量") or item.get("weight"),
            "freight": item.get("运费") or item.get("freight"),
            "carrier": item.get("承运商") or item.get("carrier")
        }
        if mapped["express_no"]:
            bills.append(ExpressBillCreate(**mapped))
    
    created = service.create_bills_batch(bills)
    return {"count": len(created), "bills": created}


@router.put("/{bill_id}", response_model=ExpressBill)
def update_bill(bill_id: int, bill: ExpressBillUpdate, db: Session = Depends(get_db)):
    service = ExpressBillService(db)
    updated = service.update_bill(bill_id, bill)
    if not updated:
        raise HTTPException(status_code=404, detail="账单不存在")
    return updated


@router.delete("/{bill_id}")
def delete_bill(bill_id: int, db: Session = Depends(get_db)):
    service = ExpressBillService(db)
    success = service.delete_bill(bill_id)
    if not success:
        raise HTTPException(status_code=404, detail="账单不存在")
    return {"message": "删除成功"}
