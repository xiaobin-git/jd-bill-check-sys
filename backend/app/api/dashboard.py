from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.services.calculation_service import CalculationService
from app.utils.exporter import export_to_excel

router = APIRouter(prefix="/api/dashboard", tags=["仪表盘"])


@router.get("/profit")
def get_profit(shop_name: Optional[str] = None, db: Session = Depends(get_db)):
    service = CalculationService(db)
    return service.calculate_profit(shop_name=shop_name)


@router.get("/export")
def export_detail(shop_name: Optional[str] = None, db: Session = Depends(get_db)):
    service = CalculationService(db)
    result = service.calculate_profit(shop_name=shop_name)
    excel_file = export_to_excel(result["detail_list"], "利润明细.xlsx")
    
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=利润明细.xlsx"}
    )
