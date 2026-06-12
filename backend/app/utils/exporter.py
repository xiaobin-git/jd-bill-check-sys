import pandas as pd
from io import BytesIO
from typing import List, Dict, Any


def export_to_excel(data: List[Dict[str, Any]], filename: str = "export.xlsx") -> BytesIO:
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    output.seek(0)
    return output
