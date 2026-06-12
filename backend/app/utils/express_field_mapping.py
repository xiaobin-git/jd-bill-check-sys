import json
from pathlib import Path
from typing import Any, Dict, List

from app.core.config import settings


SYSTEM_FIELDS = [
    {"key": "express_no", "label": "快递单号"},
    {"key": "address", "label": "收货地址"},
    {"key": "created_time", "label": "创建时间"},
    {"key": "weight", "label": "重量"},
    {"key": "volume", "label": "体积"},
    {"key": "freight", "label": "运费"},
]

DEFAULT_MAPPINGS = {
    "express_no": ["快递单号", "运单号", "运单编号", "物流单号", "物流单号/运单号"],
    "address": ["收货地址", "地址", "详细地址", "收件地址", "目的地"],
    "created_time": ["创建时间", "下单时间", "寄件时间", "发货时间", "出库时间"],
    "weight": ["重量", "预估重量", "结算重量", "实际重量"],
    "volume": ["体积", "包裹体积", "计费体积", "长宽高体积"],
    "freight": ["运费", "总运费", "合计", "费用合计", "结算运费", "快递费"],
}

MAPPING_FILE = Path(settings.BASE_DIR) / "data" / "express_field_mappings.json"


def _normalize_text(value: str) -> str:
    return str(value).strip().lower().replace(" ", "")


def ensure_mapping_file() -> None:
    if not MAPPING_FILE.exists():
        MAPPING_FILE.parent.mkdir(parents=True, exist_ok=True)
        MAPPING_FILE.write_text(
            json.dumps({"mappings": DEFAULT_MAPPINGS}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def load_field_mappings() -> Dict[str, List[str]]:
    ensure_mapping_file()
    data = json.loads(MAPPING_FILE.read_text(encoding="utf-8"))
    mappings = data.get("mappings", {})
    result: Dict[str, List[str]] = {}
    for field in SYSTEM_FIELDS:
        result[field["key"]] = list(dict.fromkeys(mappings.get(field["key"], DEFAULT_MAPPINGS.get(field["key"], []))))
    return result


def save_field_mappings(mappings: Dict[str, List[str]]) -> Dict[str, List[str]]:
    cleaned: Dict[str, List[str]] = {}
    for field in SYSTEM_FIELDS:
        key = field["key"]
        values = mappings.get(key, [])
        cleaned[key] = [str(item).strip() for item in values if str(item).strip()]
    MAPPING_FILE.parent.mkdir(parents=True, exist_ok=True)
    MAPPING_FILE.write_text(json.dumps({"mappings": cleaned}, ensure_ascii=False, indent=2), encoding="utf-8")
    return cleaned


def append_field_aliases(field_mapping: Dict[str, str]) -> Dict[str, List[str]]:
    mappings = load_field_mappings()
    for system_field, source_field in field_mapping.items():
        if source_field and source_field not in mappings.get(system_field, []):
            mappings.setdefault(system_field, []).append(source_field)
    return save_field_mappings(mappings)


def get_mapping_payload() -> Dict[str, Any]:
    mappings = load_field_mappings()
    return {
        "system_fields": [
            {
                "key": field["key"],
                "label": field["label"],
                "aliases": mappings.get(field["key"], []),
            }
            for field in SYSTEM_FIELDS
        ]
    }


def auto_match_fields(source_columns: List[str]) -> Dict[str, str]:
    mappings = load_field_mappings()
    normalized_columns = {_normalize_text(column): column for column in source_columns}
    resolved: Dict[str, str] = {}
    for field in SYSTEM_FIELDS:
        key = field["key"]
        for alias in mappings.get(key, []):
            matched = normalized_columns.get(_normalize_text(alias))
            if matched:
                resolved[key] = matched
                break
    return resolved
