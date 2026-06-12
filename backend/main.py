from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.core.config import settings
from app.core.database import engine, Base
from app.api import jd_bill, erp_order, express_bill, cost, dashboard
from app.utils.express_field_mapping import ensure_mapping_file

Base.metadata.create_all(bind=engine)


def ensure_erp_order_columns():
    expected_columns = {
        "platform_type": "VARCHAR",
        "system_order_no": "VARCHAR",
        "order_status": "VARCHAR",
        "refund_status": "VARCHAR",
        "customer_note": "VARCHAR",
        "payment_time": "DATETIME",
        "shipping_time": "DATETIME",
        "estimated_weight": "FLOAT",
        "actual_receipt": "FLOAT",
        "express_company": "VARCHAR",
        "package_count": "INTEGER",
    }
    with engine.begin() as conn:
        existing = {row[1] for row in conn.execute(text("PRAGMA table_info(erp_orders)")).fetchall()}
        for column_name, column_type in expected_columns.items():
            if column_name not in existing:
                conn.execute(text(f"ALTER TABLE erp_orders ADD COLUMN {column_name} {column_type}"))


def ensure_express_bill_columns():
    expected_columns = {
        "created_time": "DATETIME",
        "volume": "FLOAT",
    }
    with engine.begin() as conn:
        existing = {row[1] for row in conn.execute(text("PRAGMA table_info(express_bills)")).fetchall()}
        for column_name, column_type in expected_columns.items():
            if column_name not in existing:
                conn.execute(text(f"ALTER TABLE express_bills ADD COLUMN {column_name} {column_type}"))


ensure_erp_order_columns()
ensure_express_bill_columns()
ensure_mapping_file()

app = FastAPI(title="京东账单核对系统")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jd_bill.router)
app.include_router(erp_order.router)
app.include_router(express_bill.router)
app.include_router(cost.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {"message": "京东账单核对系统 API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
