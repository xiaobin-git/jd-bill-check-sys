from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from urllib.parse import quote
from app.core.database import get_db
from app.services.calculation_service import CalculationService
from app.utils.exporter import export_to_excel

router = APIRouter(prefix="/api/dashboard", tags=["仪表盘"])


@router.get("/profit")
def get_profit(
    shop_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
):
    service = CalculationService(db)
    return service.calculate_profit(shop_name=shop_name, start_date=start_date, end_date=end_date)


@router.get("/export")
def export_detail(
    shop_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
):
    service = CalculationService(db)
    result = service.calculate_profit(shop_name=shop_name, start_date=start_date, end_date=end_date)
    filename = "profit-detail.xlsx"
    download_name = quote("利润明细.xlsx")
    excel_file = export_to_excel(result["detail_list"], filename)

    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}; filename*=UTF-8''{download_name}"
        }
    )
