from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.models.jd_bill import JDBill, JDBillItem
from app.models.erp_order import ERPOrder
from app.models.express_bill import ExpressBill
from app.models.cost import Cost
import pandas as pd


def _to_native(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _to_native(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_native(item) for item in value]
    if isinstance(value, tuple):
        return [_to_native(item) for item in value]
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    if hasattr(value, "item"):
        try:
            return value.item()
        except (ValueError, TypeError):
            pass
    return value


class CalculationService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_profit(self, shop_name: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        jd_items_query = self.db.query(JDBillItem).join(JDBillItem.bill)
        if shop_name:
            jd_items_query = jd_items_query.filter(JDBill.shop_name == shop_name)
        
        jd_items = jd_items_query.all()
        erp_orders = self.db.query(ERPOrder).all()
        express_bills = self.db.query(ExpressBill).all()
        costs = self.db.query(Cost).all()

        df_jd = pd.DataFrame([{
            "order_no": item.order_no,
            "product_no": item.product_no,
            "settlement_amount": item.settlement_amount or 0,
            "fee_name": item.fee_name,
            "shop_name": item.bill.shop_name if item.bill else None
        } for item in jd_items if item.bill])

        df_erp = pd.DataFrame([{
            "jd_order_no": order.jd_order_no,
            "express_no": order.express_no
        } for order in erp_orders])

        df_express = pd.DataFrame([{
            "express_no": bill.express_no,
            "freight": bill.freight or 0,
            "weight": bill.weight
        } for bill in express_bills])

        df_costs = pd.DataFrame([{
            "sku": cost.sku,
            "cost": cost.cost or 0,
            "shop_name": cost.shop_name
        } for cost in costs])

        if len(df_jd) > 0 and len(df_erp) > 0:
            df_merged = pd.merge(df_jd, df_erp, left_on="order_no", right_on="jd_order_no", how="left")
        elif len(df_jd) > 0:
            df_merged = df_jd.copy()
            df_merged["express_no"] = None
        else:
            # 创建一个空的 dataframe，包含必要的列
            df_merged = pd.DataFrame(columns=["order_no", "product_no", "settlement_amount", "fee_name", "shop_name", "express_no"])

        if len(df_merged) > 0 and len(df_express) > 0:
            df_merged = pd.merge(df_merged, df_express, on="express_no", how="left")

        if len(df_merged) > 0 and len(df_costs) > 0:
            df_merged = pd.merge(df_merged, df_costs, left_on=["product_no", "shop_name"], right_on=["sku", "shop_name"], how="left")

        # 确保必要的列存在
        for col in ["freight", "cost", "settlement_amount"]:
            if col not in df_merged.columns:
                df_merged[col] = 0
            else:
                df_merged[col] = df_merged[col].fillna(0)

        total_income = df_merged[df_merged["settlement_amount"] > 0]["settlement_amount"].sum()
        total_expense = df_merged["freight"].sum() + df_merged["cost"].sum()
        profit = total_income - total_expense
        order_count = df_merged["order_no"].nunique() if "order_no" in df_merged.columns else 0

        income_list = []
        if "fee_name" in df_merged.columns and "settlement_amount" in df_merged.columns:
            income_by_category = df_merged[df_merged["settlement_amount"] > 0].groupby("fee_name")["settlement_amount"].sum().sort_values(ascending=False)
            income_list = [
                {
                    "name": _to_native(k),
                    "amount": float(v),
                    "percent": float(v / total_income * 100) if total_income > 0 else 0.0,
                }
                for k, v in income_by_category.items()
            ]
        
        expense_by_freight = pd.Series({"运费": df_merged["freight"].sum(), "商品成本": df_merged["cost"].sum()}).sort_values(ascending=False)
        expense_list = [
            {
                "name": _to_native(k),
                "amount": float(v),
                "percent": float(v / total_expense * 100) if total_expense > 0 else 0.0,
            }
            for k, v in expense_by_freight.items()
        ]

        # 重命名列并确保列存在
        rename_dict = {
            "order_no": "订单号",
            "express_no": "快递单号",
            "weight": "重量",
            "settlement_amount": "应结金额",
            "freight": "运费",
            "cost": "商品成本"
        }
        # 只重命名存在的列
        existing_rename = {k: v for k, v in rename_dict.items() if k in df_merged.columns}
        detail_list = [_to_native(record) for record in df_merged.rename(columns=existing_rename).to_dict("records")]

        return {
            "profit": float(profit),
            "total_income": float(total_income),
            "total_expense": float(total_expense),
            "order_count": int(order_count),
            "income_detail": income_list,
            "expense_detail": expense_list,
            "detail_list": detail_list
        }
