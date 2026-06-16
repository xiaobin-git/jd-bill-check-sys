import pandas as pd
from io import BytesIO
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.cost import Cost, CostCreate, CostUpdate
from app.services.cost_service import CostService
from app.utils.csv_parser import parse_generic_file, _normalize_string_value
from app.utils.exporter import export_to_excel

router = APIRouter(prefix="/api/costs", tags=["成本管理"])


@router.get("")
def get_costs(
    page: int = 1,
    page_size: int = 20,
    shop_name: Optional[str] = None,
    product_name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    service = CostService(db)
    skip = max(page - 1, 0) * page_size
    items = service.get_costs(skip=skip, limit=page_size, shop_name=shop_name, product_name=product_name)
    total = service.count_costs(shop_name=shop_name, product_name=product_name)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


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
            "shop_name": _normalize_string_value(item.get("店铺名称") or item.get("shop_name")),
            "sku": _normalize_string_value(item.get("sku") or item.get("SKU") or item.get("商品编号")),
            "product_name": _normalize_string_value(item.get("商品名称") or item.get("product_name")),
            "cost": pd.to_numeric(item.get("成本") or item.get("cost") or 0, errors="coerce"),
            "packaging_fee": pd.to_numeric(item.get("包材费用") or item.get("packaging_fee") or 0.5, errors="coerce"),
        }
        mapped["cost"] = float(mapped["cost"]) if not pd.isna(mapped["cost"]) else 0.0
        mapped["packaging_fee"] = float(mapped["packaging_fee"]) if not pd.isna(mapped["packaging_fee"]) else 0.5
        if mapped["shop_name"] and mapped["sku"]:
            costs.append(CostCreate(**mapped))
    
    created = service.import_costs_batch(costs)
    return {"count": len(created), "costs": created}


@router.post("/sync")
def sync_from_jd_bills(shop_name: Optional[str] = None, db: Session = Depends(get_db)):
    service = CostService(db)
    count = service.sync_from_jd_bills(shop_name=shop_name)
    return {"synced": count, "message": f"同步了 {count} 条成本数据"}


@router.get("/export")
def export_costs(
    shop_name: Optional[str] = None,
    product_name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    service = CostService(db)
    rows = service.list_costs(shop_name=shop_name, product_name=product_name)
    payload = [
        {
            "店铺名称": row.shop_name,
            "SKU": row.sku,
            "商品名称": row.product_name,
            "成本": row.cost,
            "包材费用": row.packaging_fee,
        }
        for row in rows
    ]
    excel_file = export_to_excel(payload, "成本数据.xlsx")
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=costs.xlsx"},
    )


@router.get("/template")
def download_cost_template():
    df = pd.DataFrame(columns=["店铺名称", "SKU", "商品名称", "成本", "包材费用"])
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="成本导入模板")
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=cost-template.xlsx"},
    )


@router.get("/{cost_id}", response_model=Cost)
def get_cost(cost_id: int, db: Session = Depends(get_db)):
    service = CostService(db)
    cost = service.get_cost(cost_id)
    if not cost:
        raise HTTPException(status_code=404, detail="成本不存在")
    return cost


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
