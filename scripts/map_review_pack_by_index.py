from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


RE_HEADING = re.compile(r"^##\s+(\d+)\.\s+([A-Za-z0-9_\-]+)\s+\(")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_todo_index(todo_path: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for line in todo_path.read_text(encoding="utf-8").splitlines():
        m = RE_HEADING.match(line.strip())
        if not m:
            continue
        seq = int(m.group(1))
        raw_id = m.group(2)
        entries.append({"seq": seq, "raw_id": raw_id})
    entries.sort(key=lambda x: int(x["seq"]))
    return entries


def _suggest_reg_id(seq: int) -> str:
    return f"reg_{seq:03d}"


def init_id_map(todo_path: Path, out_path: Path) -> int:
    todo_entries = _parse_todo_index(todo_path)
    mapping: list[dict[str, Any]] = []
    for item in todo_entries:
        seq = int(item["seq"])
        mapping.append(
            {
                "seq": seq,
                "raw_id": item["raw_id"],
                "reg_id": "",
                "suggest_reg_id": _suggest_reg_id(seq),
                "note": "",
            }
        )

    payload = {
        "meta": {
            "source_todo": str(todo_path),
            "description": "Map review_todo sequence(raw_id) to regression reg_id. Fill reg_id manually.",
            "count": len(mapping),
        },
        "mapping": mapping,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Map template written: {out_path}")
    print(f"Rows: {len(mapping)}")
    return 0


def build_mapped_pack(
    raw_review_pack_path: Path,
    regression_cases_path: Path,
    id_map_path: Path,
    output_path: Path,
) -> int:
    raw_pack = _load_json(raw_review_pack_path)
    reg_cases_raw = _load_json(regression_cases_path)
    id_map = _load_json(id_map_path)

    raw_cases = raw_pack.get("cases", [])
    reg_cases = reg_cases_raw.get("cases", []) if isinstance(reg_cases_raw, dict) else reg_cases_raw
    if not isinstance(raw_cases, list) or not isinstance(reg_cases, list):
        raise SystemExit("Invalid input json format.")

    raw_by_id = {str(c.get("id", "")).strip(): c for c in raw_cases}
    reg_by_id = {str(c.get("id", "")).strip(): c for c in reg_cases}

    map_rows = id_map.get("mapping", [])
    if not isinstance(map_rows, list):
        raise SystemExit("id map must include list field 'mapping'.")

    reg_to_row: dict[str, dict[str, Any]] = {}
    unresolved: list[dict[str, Any]] = []
    duplicate_reg_ids: set[str] = set()

    ordered_rows: list[dict[str, Any]] = []
    for row in map_rows:
        seq = int(row.get("seq", 0))
        raw_id = str(row.get("raw_id", "")).strip()
        reg_id = str(row.get("reg_id", "")).strip()
        if not reg_id:
            unresolved.append({"seq": seq, "raw_id": raw_id, "reason": "reg_id empty"})
            continue
        if reg_id in reg_to_row:
            duplicate_reg_ids.add(reg_id)
            continue
        row_obj = {"seq": seq, "raw_id": raw_id, "reg_id": reg_id}
        reg_to_row[reg_id] = row_obj
        ordered_rows.append(row_obj)

    if duplicate_reg_ids:
        raise SystemExit(f"Duplicate reg_id in id map: {sorted(list(duplicate_reg_ids))}")

    out_cases: list[dict[str, Any]] = []
    mapped_count = 0
    seen_reg_ids: set[str] = set()

    # 1) 主输出严格按 seq 顺序，保证 raw_* 与 reg_* 前后一致。
    for row in sorted(ordered_rows, key=lambda x: int(x["seq"])):
        reg_id = row["reg_id"]
        raw_id = row["raw_id"]
        reg_case = reg_by_id.get(reg_id)
        if not reg_case:
            unresolved.append(
                {
                    "seq": row["seq"],
                    "raw_id": raw_id,
                    "reg_id": reg_id,
                    "reason": "reg_id not found in regression cases",
                }
            )
            continue

        raw_case = raw_by_id.get(raw_id)
        if not raw_case:
            unresolved.append(
                {
                    "seq": row["seq"],
                    "raw_id": raw_id,
                    "reg_id": reg_id,
                    "reason": "raw_id not found in raw review pack",
                }
            )
            out_cases.append(
                {
                    "id": reg_id,
                    "doc_type": reg_case.get("doc_type", ""),
                    "text": reg_case.get("text", ""),
                    "expected": reg_case.get("expected", {}),
                    "decision": "",
                    "review_notes": "",
                    "map_meta": {"seq": row["seq"], "raw_id": raw_id, "reg_id": reg_id},
                }
            )
            continue

        mapped_count += 1
        seen_reg_ids.add(reg_id)
        out_cases.append(
            {
                "id": reg_id,
                "doc_type": reg_case.get("doc_type", ""),
                "text": reg_case.get("text", ""),
                "expected": reg_case.get("expected", {}),
                "decision": raw_case.get("decision", ""),
                "review_notes": raw_case.get("review_notes", ""),
                "map_meta": {"seq": row["seq"], "raw_id": row["raw_id"], "reg_id": reg_id},
            }
        )

    # 2) 将未在 mapping 中出现的 regression 用例追加到末尾，避免静默丢失。
    for reg_case in reg_cases:
        reg_id = str(reg_case.get("id", "")).strip()
        if not reg_id or reg_id in seen_reg_ids:
            continue
        unresolved.append(
            {
                "seq": None,
                "raw_id": None,
                "reg_id": reg_id,
                "reason": "reg_id not mapped in id_map",
            }
        )
        out_cases.append(
            {
                "id": reg_id,
                "doc_type": reg_case.get("doc_type", ""),
                "text": reg_case.get("text", ""),
                "expected": reg_case.get("expected", {}),
                "decision": "",
                "review_notes": "",
                "map_meta": {"seq": None, "raw_id": None, "reg_id": reg_id},
            }
        )

    out = {
        "meta": {
            "source_raw_review_pack": str(raw_review_pack_path),
            "source_regression_cases": str(regression_cases_path),
            "source_id_map": str(id_map_path),
            "order_policy": "seq_from_review_id_map",
            "mapped_cases": mapped_count,
            "total_reg_cases": len(reg_cases),
            "unresolved_count": len(unresolved),
        },
        "unresolved": unresolved,
        "cases": out_cases,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Mapped review pack written: {output_path}")
    print(f"Mapped: {mapped_count}/{len(reg_cases)}")
    print(f"Unresolved: {len(unresolved)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Map raw review pack to regression ids by review_todo sequence mapping.")
    parser.add_argument("--todo", default="test_samples/review_todo.md", help="Review todo markdown path.")
    parser.add_argument("--id-map", default="test_samples/review_id_map.json", help="Sequence mapping json path.")
    parser.add_argument("--init-id-map", action="store_true", help="Generate id map template from review_todo headings.")
    parser.add_argument("--raw-review-pack", default="test_samples/cases.review_pack.json", help="Raw review pack json path.")
    parser.add_argument("--regression-cases", default="test_samples/cases.regression.json", help="Regression cases json path.")
    parser.add_argument(
        "--output",
        default="test_samples/cases.review_pack.regression.mapped.by_index.json",
        help="Output mapped review pack path.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    todo_path = (repo_root / args.todo).resolve() if not Path(args.todo).is_absolute() else Path(args.todo)
    id_map_path = (repo_root / args.id_map).resolve() if not Path(args.id_map).is_absolute() else Path(args.id_map)

    if args.init_id_map:
        if not todo_path.exists():
            raise SystemExit(f"todo not found: {todo_path}")
        return init_id_map(todo_path, id_map_path)

    raw_review_pack_path = (
        (repo_root / args.raw_review_pack).resolve()
        if not Path(args.raw_review_pack).is_absolute()
        else Path(args.raw_review_pack)
    )
    regression_cases_path = (
        (repo_root / args.regression_cases).resolve()
        if not Path(args.regression_cases).is_absolute()
        else Path(args.regression_cases)
    )
    output_path = (repo_root / args.output).resolve() if not Path(args.output).is_absolute() else Path(args.output)

    for p in (raw_review_pack_path, regression_cases_path, id_map_path):
        if not p.exists():
            raise SystemExit(f"file not found: {p}")

    return build_mapped_pack(
        raw_review_pack_path=raw_review_pack_path,
        regression_cases_path=regression_cases_path,
        id_map_path=id_map_path,
        output_path=output_path,
    )


if __name__ == "__main__":
    raise SystemExit(main())
