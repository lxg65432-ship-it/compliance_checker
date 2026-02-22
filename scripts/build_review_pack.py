from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
import sys


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from checker import run_checks  # noqa: E402
from rules_loader import load_rules  # noqa: E402


def _read_cases(path: Path) -> list[dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict) and isinstance(raw.get("cases"), list):
        return raw["cases"]
    raise ValueError("Cases file must be JSON array or object with key 'cases'.")


def _text_excerpt(text: str, max_len: int = 120) -> str:
    t = " ".join(str(text).split())
    if len(t) <= max_len:
        return t
    return t[:max_len] + "..."


def build_review_pack(cases: list[dict[str, Any]], rules: dict[str, Any]) -> dict[str, Any]:
    out_cases: list[dict[str, Any]] = []
    for c in cases:
        case_id = str(c.get("id", "")).strip() or "unknown_case"
        doc_type = str(c.get("doc_type", "")).strip()
        text = str(c.get("text", ""))
        expected = c.get("expected", {}) or {}

        report = run_checks(doc_type, text, rules)
        findings = report.get("findings", [])

        out_cases.append(
            {
                "id": case_id,
                "doc_type": doc_type,
                "text": text,
                "text_excerpt": _text_excerpt(text),
                "observed": {
                    "summary": report.get("summary", {}),
                    "categories": sorted(list({str(f.get("category", "")) for f in findings if f.get("category")})),
                    "top_titles": [str(f.get("title", "")) for f in findings[:5]],
                },
                "expected": expected,
                "review_notes": "",
                "decision": "",  # pass / fail / unsure
            }
        )

    return {"cases": out_cases}


def render_review_todo_md(pack: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# 样本标注待办")
    lines.append("")
    lines.append("说明：逐条补充 `expected` 和 `decision`，完成后可直接用于评估。")
    lines.append("")
    for i, c in enumerate(pack.get("cases", []), 1):
        sid = c.get("id", "unknown")
        dt = c.get("doc_type", "")
        ex = c.get("text_excerpt", "")
        summ = c.get("observed", {}).get("summary", {})
        lines.append(f"## {i}. {sid} ({dt})")
        lines.append(f"- 文本摘要: {ex}")
        lines.append(
            f"- 现状命中: total={summ.get('total', 0)}, high={summ.get('high', 0)}, "
            f"medium={summ.get('medium', 0)}, low={summ.get('low', 0)}"
        )
        cats = c.get("observed", {}).get("categories", [])
        if cats:
            lines.append(f"- 类别: {', '.join(cats)}")
        titles = c.get("observed", {}).get("top_titles", [])
        if titles:
            lines.append(f"- 代表标题: {' | '.join(titles)}")
        lines.append("- 待标注: expected + decision + review_notes")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build review pack from sample cases with observed checker outputs.")
    parser.add_argument("--rules", default="rules_v1.xlsx", help="Rules xlsx path.")
    parser.add_argument("--cases", default="test_samples/cases.generated.json", help="Input cases json path.")
    parser.add_argument("--output", default="test_samples/cases.review_pack.json", help="Output review pack json path.")
    parser.add_argument("--todo-md", default="test_samples/review_todo.md", help="Output markdown todo path.")
    args = parser.parse_args()

    rules_path = (REPO_ROOT / args.rules).resolve() if not Path(args.rules).is_absolute() else Path(args.rules)
    cases_path = (REPO_ROOT / args.cases).resolve() if not Path(args.cases).is_absolute() else Path(args.cases)
    out_path = (REPO_ROOT / args.output).resolve() if not Path(args.output).is_absolute() else Path(args.output)
    todo_path = (REPO_ROOT / args.todo_md).resolve() if not Path(args.todo_md).is_absolute() else Path(args.todo_md)

    rules = load_rules(rules_path)
    cases = _read_cases(cases_path)
    pack = build_review_pack(cases, rules)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")

    todo_md = render_review_todo_md(pack)
    todo_path.write_text(todo_md, encoding="utf-8")

    print(f"Review pack: {out_path}")
    print(f"Todo md: {todo_path}")
    print(f"Cases: {len(pack.get('cases', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

