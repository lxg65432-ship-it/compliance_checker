from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def load_report(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_triage(report: dict[str, Any]) -> dict[str, Any]:
    results = report.get("results", [])
    failed = [r for r in results if not bool(r.get("passed"))]

    failure_reason_counts: Counter[str] = Counter()
    category_counts_failed: Counter[str] = Counter()
    keyword_counts_failed: Counter[str] = Counter()
    cases_by_reason: dict[str, list[str]] = defaultdict(list)

    for r in failed:
        case_id = str(r.get("id", "unknown"))
        for v in r.get("violations", []):
            reason = str(v)
            failure_reason_counts[reason] += 1
            cases_by_reason[reason].append(case_id)

        for f in r.get("findings", []):
            cat = str(f.get("category", "unknown"))
            category_counts_failed[cat] += 1
            title = str(f.get("title", ""))
            if title:
                keyword_counts_failed[title] += 1

    return {
        "meta": report.get("meta", {}),
        "failed_cases": len(failed),
        "failure_reasons": failure_reason_counts,
        "failed_category_hits": category_counts_failed,
        "failed_titles": keyword_counts_failed,
        "cases_by_reason": cases_by_reason,
    }


def render_markdown(triage: dict[str, Any]) -> str:
    meta = triage.get("meta", {})
    total = meta.get("total_cases", 0)
    passed = meta.get("pass_cases", 0)
    failed = meta.get("fail_cases", 0)
    pass_rate = meta.get("pass_rate", 0)

    lines: list[str] = []
    lines.append("# 回归评估分流清单")
    lines.append("")
    lines.append("## 汇总")
    lines.append(f"- 总用例: {total}")
    lines.append(f"- 通过: {passed}")
    lines.append(f"- 失败: {failed}")
    lines.append(f"- 通过率: {pass_rate}%")
    lines.append("")

    reason_counts: Counter[str] = triage["failure_reasons"]
    if not reason_counts:
        lines.append("## 失败原因排序")
        lines.append("- 当前无失败用例。")
        lines.append("")
        lines.append("## 下一步建议")
        lines.append("- 继续扩充真实样本并补充 expected 断言。")
        lines.append("- 每次改规则后运行回归，保持门禁稳定通过。")
        return "\n".join(lines)

    lines.append("## 失败原因排序")
    for reason, cnt in reason_counts.most_common():
        lines.append(f"- {reason}: {cnt}")
    lines.append("")

    lines.append("## 失败类别热度")
    cat_counts: Counter[str] = triage["failed_category_hits"]
    for cat, cnt in cat_counts.most_common():
        lines.append(f"- {cat}: {cnt}")
    lines.append("")

    lines.append("## 高优先级修复建议")
    top_reasons = [r for r, _ in reason_counts.most_common(3)]
    for reason in top_reasons:
        lines.append(f"- `{reason}`")
        lines.append("  - 建议动作: 在 rules_v1.xlsx 对应 sheet 缩小触发词范围或增加排除条件。")
        example_cases = triage["cases_by_reason"].get(reason, [])[:5]
        if example_cases:
            lines.append(f"  - 关联用例: {', '.join(example_cases)}")
    lines.append("")

    lines.append("## 操作建议")
    lines.append("- 先修复排序第 1 的失败原因，再跑全量回归。")
    lines.append("- 每次只改一个规则簇，便于定位效果。")
    lines.append("- 修复后更新 cases.regression.json，固化新断言。")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build triage checklist from evaluation report.")
    parser.add_argument(
        "--report",
        default="test_samples/last_eval_report.regression.json",
        help="Input evaluation report json.",
    )
    parser.add_argument(
        "--output",
        default="test_samples/regression_triage.md",
        help="Output markdown path.",
    )
    args = parser.parse_args()

    report_path = Path(args.report)
    if not report_path.is_absolute():
        report_path = (Path(__file__).resolve().parent.parent / report_path).resolve()

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = (Path(__file__).resolve().parent.parent / output_path).resolve()

    if not report_path.exists():
        raise SystemExit(f"Report not found: {report_path}")

    report = load_report(report_path)
    triage = build_triage(report)
    md = render_markdown(triage)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md, encoding="utf-8")
    print(f"Triage file: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

