import pandas as pd
from io import BytesIO, StringIO
from pathlib import Path
from typing import List, Dict, Any


def _normalize_string_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    text = str(value).strip()
    if text.startswith("'"):
        text = text[1:].strip()
    return text or None


def _is_non_settlement_status(value: Any) -> bool:
    text = _normalize_string_value(value)
    if not text:
        return False
    normalized = text.replace(" ", "")
    return normalized == "不结算" or "不结算" in normalized


def _decode_text_content(content: bytes) -> str:
    encodings = ["utf-8", "utf-8-sig", "gb18030", "gbk"]
    for encoding in encodings:
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("无法识别文件编码，请保存为 UTF-8、GBK 或 Excel 格式后再导入")


def _read_tabular_file(content: bytes, filename: str) -> pd.DataFrame:
    suffix = Path(filename or "").suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(StringIO(_decode_text_content(content)))
    if suffix == ".xlsx":
        return pd.read_excel(BytesIO(content), engine="openpyxl")
    if suffix == ".xls":
        return pd.read_excel(BytesIO(content), engine="xlrd")
    raise ValueError("仅支持 csv、xls、xlsx 文件")


def read_tabular_dataframe(content: bytes, filename: str) -> pd.DataFrame:
    df = _read_tabular_file(content, filename)
    df.columns = [str(column).strip() for column in df.columns]
    return df


def parse_jd_bill_file(content: bytes, filename: str) -> List[Dict[str, Any]]:
    df = read_tabular_dataframe(content, filename)
    
    column_mapping = {
        "订单编号": "order_no",
        "订单状态": "order_status",
        "订单下单时间": "order_time",
        "商品编号": "product_no",
        "商品名称": "product_name",
        "商品数量": "quantity",
        "扣点类型": "commission_type",
        "佣金比例": "commission_rate",
        "费用名称": "fee_name",
        "应结金额": "settlement_amount",
        "币种": "currency",
        "收支方向": "direction",
        "结算状态": "settlement_status",
        "费用项含义": "fee_meaning",
        "费用说明": "fee_description"
    }
    
    df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})

    string_cols = [
        "order_no",
        "order_status",
        "product_no",
        "product_name",
        "commission_type",
        "fee_name",
        "currency",
        "direction",
        "settlement_status",
        "fee_meaning",
        "fee_description",
    ]
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].apply(_normalize_string_value)
    
    if "order_time" in df.columns:
        df["order_time"] = pd.to_datetime(df["order_time"], errors="coerce").apply(
            lambda value: value.to_pydatetime() if not pd.isna(value) else None
        )
    
    if "quantity" in df.columns:
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
    
    numeric_cols = ["commission_rate", "settlement_amount"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    if "settlement_status" in df.columns and "settlement_amount" in df.columns:
        non_settlement_mask = df["settlement_status"].apply(_is_non_settlement_status)
        df.loc[non_settlement_mask, "settlement_amount"] = 0
    
    result = [record for record in df.to_dict("records") if record.get("order_no")]
    return result


def parse_generic_file(content: bytes, filename: str) -> List[Dict[str, Any]]:
    df = read_tabular_dataframe(content, filename)
    return df.to_dict("records")
