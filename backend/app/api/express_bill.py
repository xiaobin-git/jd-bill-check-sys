import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.express_bill import ExpressBill, ExpressBillCreate, ExpressBillUpdate
from app.services.express_bill_service import ExpressBillService
from app.utils.csv_parser import read_tabular_dataframe
from app.utils.express_field_mapping import (
    SYSTEM_FIELDS,
    append_field_aliases,
    auto_match_fields,
    get_mapping_payload,
    load_field_mappings,
    save_field_mappings,
)

router = APIRouter(prefix="/api/express-bills", tags=["快递账单"])


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


def _parse_freight(value):
    freight = _parse_float(value)
    if freight is None:
        return None
    return abs(freight)


def _required_field_keys():
    return [field["key"] for field in SYSTEM_FIELDS]


def _system_field_payload():
    return [{"key": field["key"], "label": field["label"]} for field in SYSTEM_FIELDS]


def _build_express_bills(df, carrier: str, field_mapping: dict[str, str]) -> list[ExpressBillCreate]:
    records = df.to_dict("records")
    bills: list[ExpressBillCreate] = []
    for item in records:
        mapped = {
            "express_no": _clean_text(item.get(field_mapping["express_no"])),
            "address": _clean_text(item.get(field_mapping["address"])),
            "created_time": _parse_datetime(item.get(field_mapping["created_time"])),
            "weight": _parse_float(item.get(field_mapping["weight"])),
            "volume": _parse_float(item.get(field_mapping["volume"])),
            "freight": _parse_freight(item.get(field_mapping["freight"])),
            "carrier": carrier,
        }
        if mapped["express_no"]:
            bills.append(ExpressBillCreate(**mapped))
    return bills


@router.get("")
def get_bills(page: int = 1, page_size: int = 20, carrier: Optional[str] = None, db: Session = Depends(get_db)):
    service = ExpressBillService(db)
    skip = max(page - 1, 0) * page_size
    items = service.get_bills(skip=skip, limit=page_size, carrier=carrier)
    total = service.count_bills(carrier=carrier)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/carriers", response_model=List[str])
def get_carriers(db: Session = Depends(get_db)):
    service = ExpressBillService(db)
    return service.get_distinct_carriers()


@router.get("/field-mappings")
def get_field_mappings():
    return get_mapping_payload()


@router.put("/field-mappings")
def update_field_mappings(payload: dict = Body(...)):
    mappings = payload.get("mappings", {})
    save_field_mappings(mappings)
    return get_mapping_payload()


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


@router.post("/import")
async def import_bills(
    carrier: str = Form(...),
    file: UploadFile = File(...),
    field_mapping: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    content = await file.read()
    try:
        df = read_tabular_dataframe(content, file.filename or "")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    carrier_name = _clean_text(carrier)
    if not carrier_name:
        raise HTTPException(status_code=400, detail="承运商名称不能为空")

    source_columns = [column for column in df.columns if column]
    if not source_columns:
        raise HTTPException(status_code=400, detail="导入文件缺少表头，无法识别字段")

    resolved_mapping = auto_match_fields(source_columns)
    if field_mapping:
        try:
            manual_mapping = json.loads(field_mapping)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail="字段映射格式不正确") from exc
        resolved_mapping.update({key: value for key, value in manual_mapping.items() if value})

    missing_fields = [key for key in _required_field_keys() if not resolved_mapping.get(key)]
    invalid_fields = [key for key, value in resolved_mapping.items() if value not in source_columns]
    if invalid_fields:
        raise HTTPException(status_code=400, detail=f"字段映射无效：{', '.join(invalid_fields)}")

    if missing_fields:
        return {
            "status": "need_mapping",
            "carrier": carrier_name,
            "source_columns": source_columns,
            "system_fields": _system_field_payload(),
            "resolved_mapping": resolved_mapping,
            "missing_fields": missing_fields,
        }

    service = ExpressBillService(db)
    bills = _build_express_bills(df, carrier_name, resolved_mapping)
    if not bills:
        raise HTTPException(status_code=400, detail="未识别到可导入的快递账单数据，请检查字段映射或文件内容")

    append_field_aliases(resolved_mapping)
    created = service.create_bills_batch(bills)
    return {
        "status": "imported",
        "count": len(created),
        "bills": created,
        "carrier": carrier_name,
        "field_mapping": resolved_mapping,
    }


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
