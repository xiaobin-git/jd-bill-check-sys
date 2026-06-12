from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.jd_bill import JDBill, JDBillCreate, JDBillUpdate, JDBillItem, JDBillItemCreate, JDBillItemUpdate
from app.services.jd_bill_service import JDBillService
from app.utils.csv_parser import parse_jd_bill_file

router = APIRouter(prefix="/api/jd-bills", tags=["京东账单"])


@router.get("")
def get_bills(
    page: int = 1,
    page_size: int = 20,
    date_range: Optional[str] = None,
    shop_name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    service = JDBillService(db)
    skip = max(page - 1, 0) * page_size
    items = service.get_bills(skip=skip, limit=page_size, date_range=date_range, shop_name=shop_name)
    total = service.count_bills(date_range=date_range, shop_name=shop_name)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/shops", response_model=List[str])
def get_shop_names(db: Session = Depends(get_db)):
    service = JDBillService(db)
    return service.get_distinct_shop_names()


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


@router.get("/{bill_id}/items")
def get_items(
    bill_id: int,
    page: int = 1,
    page_size: int = 20,
    order_no: Optional[str] = None,
    product_no: Optional[str] = None,
    fee_name: Optional[str] = None,
    direction: Optional[str] = None,
    product_name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    service = JDBillService(db)
    skip = max(page - 1, 0) * page_size
    items = service.get_items(
        bill_id,
        skip=skip,
        limit=page_size,
        order_no=order_no,
        product_no=product_no,
        fee_name=fee_name,
        direction=direction,
        product_name=product_name,
    )
    total = service.count_items(
        bill_id,
        order_no=order_no,
        product_no=product_no,
        fee_name=fee_name,
        direction=direction,
        product_name=product_name,
    )
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{bill_id}/item-filter-options")
def get_item_filter_options(bill_id: int, db: Session = Depends(get_db)):
    service = JDBillService(db)
    return service.get_item_filter_options(bill_id)


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
