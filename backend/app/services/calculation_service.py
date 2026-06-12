from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional, Tuple
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
    EXPORT_FEE_COLUMNS = [
        "商品保险服务费",
        "京豆",
        "货款",
        "代收配送费",
        "佣金",
        "交易服务费",
        "代收白条网络推广技术服务费",
    ]

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _normalize_direction(direction: Optional[str]) -> Optional[str]:
        text = (direction or "").strip()
        if not text:
            return None
        if text in {"收入", "收"} or "收入" in text:
            return "income"
        if text in {"支出", "支"} or "支出" in text:
            return "expense"
        return None

    @staticmethod
    def _parse_date(date_text: Optional[str]) -> Optional[datetime]:
        if not date_text:
            return None
        return datetime.strptime(date_text, "%Y-%m-%d")

    @staticmethod
    def _clean_text(value: Any, default: Optional[str] = None) -> Optional[str]:
        try:
            if pd.isna(value):
                return default
        except TypeError:
            pass
        text = str(value).strip()
        return text if text else default

    @classmethod
    def _first_non_empty(cls, series: pd.Series) -> Optional[str]:
        for value in series:
            text = cls._clean_text(value)
            if text is not None:
                return text
        return None

    @staticmethod
    def _first_not_null(series: pd.Series) -> Any:
        for value in series:
            try:
                if pd.isna(value):
                    continue
            except TypeError:
                pass
            return value
        return None

    def _load_dataframes(
        self,
        shop_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        jd_items_query = self.db.query(JDBillItem).join(JDBillItem.bill)
        if shop_name and shop_name != "全部":
            jd_items_query = jd_items_query.filter(JDBill.shop_name == shop_name)

        start_dt = self._parse_date(start_date)
        end_dt = self._parse_date(end_date)
        if start_dt:
            jd_items_query = jd_items_query.filter(JDBillItem.order_time >= start_dt)
        if end_dt:
            jd_items_query = jd_items_query.filter(JDBillItem.order_time < end_dt + timedelta(days=1))

        jd_items = jd_items_query.all()
        df_jd = pd.DataFrame(
            [
                {
                    "order_no": item.order_no,
                    "product_no": item.product_no,
                    "product_name": item.product_name,
                    "quantity": item.quantity or 0,
                    "settlement_amount": item.settlement_amount or 0,
                    "fee_name": item.fee_name,
                    "direction": item.direction,
                    "shop_name": item.bill.shop_name if item.bill else None,
                }
                for item in jd_items
                if item.bill
            ]
        )
        if df_jd.empty:
            df_jd = pd.DataFrame(
                columns=[
                    "order_no",
                    "product_no",
                    "product_name",
                    "quantity",
                    "settlement_amount",
                    "fee_name",
                    "direction",
                    "shop_name",
                ]
            )
            return (
                df_jd,
                pd.DataFrame(columns=["jd_order_no", "express_no"]),
                pd.DataFrame(columns=["express_no", "freight", "weight", "volume", "address"]),
                pd.DataFrame(columns=["sku", "cost"]),
            )

        order_nos = sorted(
            {
                self._clean_text(item.order_no, "")
                for item in jd_items
                if self._clean_text(item.order_no, "")
            }
        )
        product_nos = sorted(
            {
                self._clean_text(item.product_no, "")
                for item in jd_items
                if self._clean_text(item.product_no, "")
            }
        )

        erp_orders = []
        if order_nos:
            erp_orders = self.db.query(ERPOrder).filter(ERPOrder.jd_order_no.in_(order_nos)).all()
        df_erp = pd.DataFrame(
            [{"jd_order_no": order.jd_order_no, "express_no": order.express_no} for order in erp_orders]
        )
        if df_erp.empty:
            df_erp = pd.DataFrame(columns=["jd_order_no", "express_no"])

        express_nos = sorted(
            {self._clean_text(order.express_no, "") for order in erp_orders if self._clean_text(order.express_no, "")}
        )
        express_bills = []
        if express_nos:
            express_bills = self.db.query(ExpressBill).filter(ExpressBill.express_no.in_(express_nos)).all()
        df_express = pd.DataFrame(
            [
                {
                    "express_no": bill.express_no,
                    "freight": bill.freight or 0,
                    "weight": bill.weight,
                    "volume": bill.volume,
                    "address": bill.address,
                }
                for bill in express_bills
            ]
        )
        if df_express.empty:
            df_express = pd.DataFrame(columns=["express_no", "freight", "weight", "volume", "address"])

        costs = []
        if product_nos:
            costs = self.db.query(Cost).filter(Cost.sku.in_(product_nos)).all()
        df_costs = pd.DataFrame([{"sku": cost.sku, "cost": cost.cost or 0} for cost in costs])
        if df_costs.empty:
            df_costs = pd.DataFrame(columns=["sku", "cost"])

        return df_jd, df_erp, df_express, df_costs

    def _build_export_dataset(
        self,
        df_jd: pd.DataFrame,
        df_erp: pd.DataFrame,
        df_express: pd.DataFrame,
        df_costs: pd.DataFrame,
    ) -> Tuple[pd.DataFrame, List[str]]:
        if df_jd.empty:
            return (
                pd.DataFrame(
                    columns=[
                        "shop_name",
                        "order_no",
                        "product_no",
                        "product_name",
                        "quantity",
                        "express_no",
                        "freight",
                        "weight",
                        "volume",
                        "address",
                        "product_cost",
                    ]
                ),
                [],
            )

        df_jd = df_jd.copy()
        for col in ["order_no", "product_no", "product_name", "fee_name", "direction", "shop_name"]:
            df_jd[col] = df_jd[col].apply(lambda value: self._clean_text(value, ""))
        for col in ["quantity", "settlement_amount"]:
            df_jd[col] = pd.to_numeric(df_jd[col], errors="coerce").fillna(0)

        key_cols = ["order_no", "product_no"]
        base_df = (
            df_jd.groupby(key_cols, dropna=False)
            .agg(
                shop_name=("shop_name", self._first_non_empty),
                product_name=("product_name", self._first_non_empty),
            )
            .reset_index()
        )

        goods_qty_df = (
            df_jd[df_jd["fee_name"] == "货款"]
            .groupby(key_cols, dropna=False)["quantity"]
            .max()
            .reset_index(name="goods_quantity")
        )
        fallback_qty_df = (
            df_jd.groupby(key_cols, dropna=False)["quantity"].max().reset_index(name="fallback_quantity")
        )
        base_df = base_df.merge(goods_qty_df, on=key_cols, how="left").merge(fallback_qty_df, on=key_cols, how="left")
        base_df["quantity"] = base_df["goods_quantity"].fillna(base_df["fallback_quantity"]).fillna(0)
        base_df = base_df.drop(columns=["goods_quantity", "fallback_quantity"])

        fee_columns = [fee for fee in self.EXPORT_FEE_COLUMNS if fee in set(df_jd["fee_name"].tolist())]
        if fee_columns:
            fee_df = (
                df_jd[df_jd["fee_name"].isin(fee_columns)]
                .pivot_table(
                    index=key_cols,
                    columns="fee_name",
                    values="settlement_amount",
                    aggfunc="sum",
                    fill_value=0,
                )
                .reset_index()
            )
            fee_df.columns.name = None
            base_df = base_df.merge(fee_df, on=key_cols, how="left")
        for fee in fee_columns:
            if fee not in base_df.columns:
                base_df[fee] = 0.0
            else:
                base_df[fee] = pd.to_numeric(base_df[fee], errors="coerce").fillna(0.0)

        if not df_erp.empty:
            df_erp = df_erp.copy()
            for col in ["jd_order_no", "express_no"]:
                df_erp[col] = df_erp[col].apply(lambda value: self._clean_text(value, ""))
            erp_df = (
                df_erp.groupby("jd_order_no", dropna=False)
                .agg(express_no=("express_no", self._first_non_empty))
                .reset_index()
            )
            base_df = base_df.merge(erp_df, left_on="order_no", right_on="jd_order_no", how="left").drop(
                columns=["jd_order_no"], errors="ignore"
            )
        else:
            base_df["express_no"] = None

        if not df_express.empty:
            df_express = df_express.copy()
            df_express["express_no"] = df_express["express_no"].apply(lambda value: self._clean_text(value, ""))
            for col in ["freight", "weight", "volume"]:
                df_express[col] = pd.to_numeric(df_express[col], errors="coerce")
            df_express["address"] = df_express["address"].apply(lambda value: self._clean_text(value))
            express_df = (
                df_express.groupby("express_no", dropna=False)
                .agg(
                    freight=("freight", self._first_not_null),
                    weight=("weight", self._first_not_null),
                    volume=("volume", self._first_not_null),
                    address=("address", self._first_non_empty),
                )
                .reset_index()
            )
            base_df = base_df.merge(express_df, on="express_no", how="left")
        else:
            for col in ["freight", "weight", "volume", "address"]:
                base_df[col] = None

        if not df_costs.empty:
            df_costs = df_costs.copy()
            df_costs["sku"] = df_costs["sku"].apply(lambda value: self._clean_text(value, ""))
            df_costs["cost"] = pd.to_numeric(df_costs["cost"], errors="coerce")
            cost_df = (
                df_costs.groupby("sku", dropna=False)
                .agg(unit_cost=("cost", self._first_not_null))
                .reset_index()
            )
            base_df = base_df.merge(cost_df, left_on="product_no", right_on="sku", how="left").drop(
                columns=["sku"], errors="ignore"
            )
        else:
            base_df["unit_cost"] = None

        base_df["freight"] = pd.to_numeric(base_df.get("freight"), errors="coerce").fillna(0.0)
        base_df["quantity"] = pd.to_numeric(base_df["quantity"], errors="coerce").fillna(0)
        base_df["unit_cost"] = pd.to_numeric(base_df.get("unit_cost"), errors="coerce").fillna(0.0)
        base_df["product_cost"] = base_df["unit_cost"] * base_df["quantity"]

        for col in ["weight", "volume"]:
            base_df[col] = pd.to_numeric(base_df.get(col), errors="coerce")

        return base_df, fee_columns

    def _format_export_dataset(self, export_df: pd.DataFrame, fee_columns: List[str]) -> pd.DataFrame:
        if export_df.empty:
            columns = ["店铺名称", "订单号", "商品编号", "商品名称", "数量"] + fee_columns + [
                "快递单号",
                "快递费用",
                "重量",
                "体积",
                "收货地址",
                "商品成本",
            ]
            return pd.DataFrame(columns=columns)

        formatted_df = export_df.copy()
        rename_dict = {
            "shop_name": "店铺名称",
            "order_no": "订单号",
            "product_no": "商品编号",
            "product_name": "商品名称",
            "quantity": "数量",
            "express_no": "快递单号",
            "freight": "快递费用",
            "weight": "重量",
            "volume": "体积",
            "address": "收货地址",
            "product_cost": "商品成本",
        }
        formatted_df = formatted_df.rename(columns=rename_dict)

        selected_columns = ["店铺名称", "订单号", "商品编号", "商品名称", "数量"] + fee_columns + [
            "快递单号",
            "快递费用",
            "重量",
            "体积",
            "收货地址",
            "商品成本",
        ]
        for col in selected_columns:
            if col not in formatted_df.columns:
                formatted_df[col] = None

        numeric_columns = ["数量", "快递费用", "重量", "体积", "商品成本"] + fee_columns
        for col in numeric_columns:
            formatted_df[col] = pd.to_numeric(formatted_df[col], errors="coerce")

        formatted_df["数量"] = formatted_df["数量"].fillna(0).astype(int)
        for col in ["店铺名称", "订单号", "商品编号", "商品名称", "快递单号", "收货地址"]:
            formatted_df[col] = formatted_df[col].apply(lambda value: self._clean_text(value))

        return formatted_df[selected_columns]

    def calculate_profit(self, shop_name: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        df_jd, df_erp, df_express, df_costs = self._load_dataframes(
            shop_name=shop_name,
            start_date=start_date,
            end_date=end_date,
        )
        export_df, fee_columns = self._build_export_dataset(df_jd, df_erp, df_express, df_costs)

        if not df_jd.empty:
            df_jd = df_jd.copy()
            df_jd["fee_name"] = df_jd["fee_name"].apply(lambda value: self._clean_text(value, ""))
            df_jd["direction"] = df_jd["direction"].apply(lambda value: self._clean_text(value, ""))
            df_jd["settlement_amount"] = pd.to_numeric(df_jd["settlement_amount"], errors="coerce").fillna(0)
            df_jd["direction_type"] = df_jd["direction"].apply(self._normalize_direction)
            df_jd["settlement_amount_abs"] = df_jd["settlement_amount"].abs()
        else:
            df_jd = pd.DataFrame(columns=["order_no", "fee_name", "direction_type", "settlement_amount_abs"])

        jd_income_df = df_jd[df_jd["direction_type"] == "income"].copy()
        jd_expense_df = df_jd[df_jd["direction_type"] == "expense"].copy()

        total_income = float(jd_income_df["settlement_amount_abs"].sum())

        freight_total = 0.0
        if not export_df.empty:
            express_rows = export_df[export_df["express_no"].notna() & (export_df["express_no"] != "")]
            if len(express_rows) > 0:
                freight_total = float(express_rows.drop_duplicates(subset=["express_no"])["freight"].fillna(0).sum())

        cost_total = float(export_df["product_cost"].fillna(0).sum()) if "product_cost" in export_df.columns else 0.0
        jd_expense_total = float(jd_expense_df["settlement_amount_abs"].sum())
        total_expense = jd_expense_total + freight_total + cost_total
        profit = total_income - total_expense
        order_count = export_df["order_no"].nunique() if "order_no" in export_df.columns else 0

        income_list = []
        if len(jd_income_df) > 0:
            income_by_category = (
                jd_income_df.assign(fee_name=jd_income_df["fee_name"].fillna("未分类收入"))
                .groupby("fee_name")["settlement_amount_abs"]
                .sum()
                .sort_values(ascending=False)
            )
            income_list = [
                {
                    "name": _to_native(k),
                    "amount": float(v),
                    "percent": float(v / total_income * 100) if total_income > 0 else 0.0,
                }
                for k, v in income_by_category.items()
            ]

        expense_series_list = []
        if len(jd_expense_df) > 0:
            expense_series_list.append(
                jd_expense_df.assign(fee_name=jd_expense_df["fee_name"].fillna("未分类支出"))
                .groupby("fee_name")["settlement_amount_abs"]
                .sum()
            )
        expense_series_list.append(pd.Series({"运费": freight_total, "商品成本": cost_total}))
        expense_by_category = pd.concat(expense_series_list).groupby(level=0).sum().sort_values(ascending=False)
        expense_list = [
            {
                "name": _to_native(k),
                "amount": float(v),
                "percent": float(v / total_expense * 100) if total_expense > 0 else 0.0,
            }
            for k, v in expense_by_category.items()
        ]
        detail_df = self._format_export_dataset(export_df, fee_columns)
        detail_list = [_to_native(record) for record in detail_df.to_dict("records")]

        return {
            "profit": float(profit),
            "total_income": float(total_income),
            "total_expense": float(total_expense),
            "order_count": int(order_count),
            "income_detail": income_list,
            "expense_detail": expense_list,
            "detail_list": detail_list
        }
