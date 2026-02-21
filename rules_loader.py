from __future__ import annotations
import pandas as pd
from pathlib import Path

SHEETS = [
    "required_fields",
    "forbidden_phrases",
    "closure_rules",
    "logic_conflicts",
    "conditional_required",   # ✅ 新增
]


def load_rules(xlsx_path: str | Path) -> dict[str, pd.DataFrame]:
    path = Path(xlsx_path)
    if not path.exists():
        raise FileNotFoundError(f"Rules file not found: {path.resolve()}")

    rules: dict[str, pd.DataFrame] = {}
    xls = pd.ExcelFile(path)
    for sheet in SHEETS:
        if sheet not in xls.sheet_names:
            raise ValueError(f"Missing sheet '{sheet}' in {path.name}. Found: {xls.sheet_names}")
        df = pd.read_excel(xls, sheet_name=sheet).fillna("")
        rules[sheet] = df
    return rules
