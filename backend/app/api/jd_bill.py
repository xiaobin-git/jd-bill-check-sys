from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.jd_bill import JDBill, JDBillCreate, JDBillUpdate, JDBillItem, JDBillItemCreate, JDBillItemUpdate
from app.services.jd_bill_service import JDBillService
from app.utils.csv_parser import parse_jd_bill_file

router = APIRouter(prefix="/api/jd-bills", tags=["京东账单"])


@router.get("", response_model=List[JDBill])
def get_bills(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = JDBillService(db)
    return service.get_bills(skip=skip, limit=limit)


@router.get("/{bill_id}", response_model=JDBill)
def get_bill(bill_id: int, db: Session = Depends(get_db)):
    service = JDBillService(db)
    bill = service.get_bill(bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="账单不存在")
    return bill


@router.post("", response_model=JDBill)
def create_bill(bill: JDBillCreate, db: Session = Depends(get_db)):
    service = JDBillService(db)
    return service.create_bill(bill)


@router.put("/{bill_id}", response_model=JDBill)
def update_bill(bill_id: int, bill: JDBillUpdate, db: Session = Depends(get_db)):
    service = JDBillService(db)
    updated = service.update_bill(bill_id, bill)
    if not updated:
        raise HTTPException(status_code=404, detail="账单不存在")
    return updated


@router.delete("/{bill_id}")
def delete_bill(bill_id: int, db: Session = Depends(get_db)):
    service = JDBillService(db)
    success = service.delete_bill(bill_id)
    if not success:
        raise HTTPException(status_code=404, detail="账单不存在")
    return {"message": "删除成功"}


@router.get("/{bill_id}/items", response_model=List[JDBillItem])
def get_items(bill_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = JDBillService(db)
    return service.get_items(bill_id, skip=skip, limit=limit)


@router.post("/{bill_id}/items", response_model=JDBillItem)
def create_item(bill_id: int, item: JDBillItemCreate, db: Session = Depends(get_db)):
    service = JDBillService(db)
    return service.create_item(bill_id, item)


@router.post("/{bill_id}/items/upload")
async def upload_items(bill_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    try:
        items_data = parse_jd_bill_file(content, file.filename or "")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    
    service = JDBillService(db)
    items = [JDBillItemCreate(**item) for item in items_data]
    created = service.create_items_batch(bill_id, items)
    
    return {"count": len(created), "items": created}


@router.put("/items/{item_id}", response_model=JDBillItem)
def update_item(item_id: int, item: JDBillItemUpdate, db: Session = Depends(get_db)):
    service = JDBillService(db)
    updated = service.update_item(item_id, item)
    if not updated:
        raise HTTPException(status_code=404, detail="明细不存在")
    return updated


@router.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    service = JDBillService(db)
    success = service.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="明细不存在")
    return {"message": "删除成功"}
