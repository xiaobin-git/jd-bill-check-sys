from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from app.core.database import get_db
from app.schemas.erp_order import ERPOrder, ERPOrderCreate, ERPOrderUpdate
from app.services.erp_order_service import ERPOrderService
from app.utils.csv_parser import parse_generic_file

router = APIRouter(prefix="/api/erp-orders", tags=["ERP订单"])


def _clean_text(value):
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return None
    if text.startswith("'"):
        text = text[1:].strip()
    return text or None


def _parse_datetime(value):
    text = _clean_text(value)
    if not text:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _parse_float(value):
    text = _clean_text(value)
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _parse_int(value):
    text = _clean_text(value)
    if not text:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


@router.get("")
def get_orders(page: int = 1, page_size: int = 20, shop_name: Optional[str] = None, db: Session = Depends(get_db)):
    service = ERPOrderService(db)
    skip = max(page - 1, 0) * page_size
    items = service.get_orders(skip=skip, limit=page_size, shop_name=shop_name)
    total = service.count_orders(shop_name=shop_name)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{order_id}", response_model=ERPOrder)
def get_order(order_id: int, db: Session = Depends(get_db)):
    service = ERPOrderService(db)
    order = service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


@router.post("", response_model=ERPOrder)
def create_order(order: ERPOrderCreate, db: Session = Depends(get_db)):
    service = ERPOrderService(db)
    return service.create_order(order)


@router.post("/upload")
async def upload_orders(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    try:
        data = parse_generic_file(content, file.filename or "")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    
    service = ERPOrderService(db)
    orders = []
    for item in data:
        mapped = {
            "shop_name": _clean_text(item.get("店铺") or item.get("店铺名称") or item.get("shop_name")),
            "platform_type": _clean_text(item.get("平台类型") or item.get("platform_type")),
            "jd_order_no": _clean_text(item.get("平台订单号") or item.get("京东系统订单号") or item.get("jd_order_no") or item.get("order_no")),
            "express_no": _clean_text(item.get("快递单号") or item.get("express_no")),
            "system_order_no": _clean_text(item.get("系统单号") or item.get("system_order_no")),
            "order_status": _clean_text(item.get("订单状态") or item.get("order_status")),
            "refund_status": _clean_text(item.get("退款状态") or item.get("refund_status")),
            "customer_note": _clean_text(item.get("客服备注") or item.get("customer_note")),
            "payment_time": _parse_datetime(item.get("付款时间") or item.get("payment_time")),
            "shipping_time": _parse_datetime(item.get("发货时间") or item.get("shipping_time")),
            "estimated_weight": _parse_float(item.get("预估总重量") or item.get("estimated_weight")),
            "actual_receipt": _parse_float(item.get("商家实收") or item.get("actual_receipt")),
            "express_company": _clean_text(item.get("快递公司") or item.get("express_company")),
            "package_count": _parse_int(item.get("包裹个数") or item.get("package_count")),
        }
        if mapped["jd_order_no"] and mapped["shop_name"]:
            orders.append(ERPOrderCreate(**mapped))

    if not orders:
        raise HTTPException(status_code=400, detail="未识别到可导入的 ERP 数据，请检查表头是否包含：店铺、平台订单号、快递单号等字段")
    
    created = service.create_orders_batch(orders)
    return {"count": len(created), "orders": created}


@router.put("/{order_id}", response_model=ERPOrder)
def update_order(order_id: int, order: ERPOrderUpdate, db: Session = Depends(get_db)):
    service = ERPOrderService(db)
    updated = service.update_order(order_id, order)
    if not updated:
        raise HTTPException(status_code=404, detail="订单不存在")
    return updated


@router.delete("/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    service = ERPOrderService(db)
    success = service.delete_order(order_id)
    if not success:
        raise HTTPException(status_code=404, detail="订单不存在")
    return {"message": "删除成功"}
