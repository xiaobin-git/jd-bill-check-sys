from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.cost import Cost, CostCreate, CostUpdate
from app.services.cost_service import CostService
from app.utils.csv_parser import parse_generic_file

router = APIRouter(prefix="/api/costs", tags=["成本管理"])


@router.get("", response_model=List[Cost])
def get_costs(skip: int = 0, limit: int = 100, shop_name: Optional[str] = None, db: Session = Depends(get_db)):
    service = CostService(db)
    return service.get_costs(skip=skip, limit=limit, shop_name=shop_name)


@router.get("/{cost_id}", response_model=Cost)
def get_cost(cost_id: int, db: Session = Depends(get_db)):
    service = CostService(db)
    cost = service.get_cost(cost_id)
    if not cost:
        raise HTTPException(status_code=404, detail="成本不存在")
    return cost


@router.post("", response_model=Cost)
def create_cost(cost: CostCreate, db: Session = Depends(get_db)):
    service = CostService(db)
    return service.create_cost(cost)


@router.post("/upload")
async def upload_costs(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    try:
        data = parse_generic_file(content, file.filename or "")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    
    service = CostService(db)
    costs = []
    for item in data:
        mapped = {
            "shop_name": item.get("店铺名称") or item.get("shop_name"),
            "sku": item.get("sku") or item.get("SKU") or item.get("商品编号"),
            "product_name": item.get("商品名称") or item.get("product_name"),
            "cost": item.get("成本") or item.get("cost") or 0
        }
        if mapped["shop_name"] and mapped["sku"]:
            costs.append(CostCreate(**mapped))
    
    created = service.create_costs_batch(costs)
    return {"count": len(created), "costs": created}


@router.post("/sync")
def sync_from_jd_bills(shop_name: Optional[str] = None, db: Session = Depends(get_db)):
    service = CostService(db)
    count = service.sync_from_jd_bills(shop_name=shop_name)
    return {"synced": count, "message": f"同步了 {count} 条成本数据"}


@router.put("/{cost_id}", response_model=Cost)
def update_cost(cost_id: int, cost: CostUpdate, db: Session = Depends(get_db)):
    service = CostService(db)
    updated = service.update_cost(cost_id, cost)
    if not updated:
        raise HTTPException(status_code=404, detail="成本不存在")
    return updated


@router.delete("/{cost_id}")
def delete_cost(cost_id: int, db: Session = Depends(get_db)):
    service = CostService(db)
    success = service.delete_cost(cost_id)
    if not success:
        raise HTTPException(status_code=404, detail="成本不存在")
    return {"message": "删除成功"}
