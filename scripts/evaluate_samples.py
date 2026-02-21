from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import sys


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from checker import run_checks  # noqa: E402
from rules_loader import load_rules  # noqa: E402


@dataclass
class EvalCaseResult:
    case_id: str
    passed: bool
    violations: list[str]
    summary: dict[str, Any]
    findings: list[dict[str, Any]]


def _read_cases(cases_path: Path) -> list[dict[str, Any]]:
    raw = json.loads(cases_path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict) and isinstance(raw.get("cases"), list):
        return raw["cases"]
    raise ValueError("Cases file must be a JSON array or an object with key 'cases'.")


def _count_findings_by_category(findings: list[dict[str, Any]]) -> dict[str, int]:
    out: dict[str, int] = {}
    for item in findings:
        key = str(item.get("category", "")).strip() or "unknown"
        out[key] = out.get(key, 0) + 1
    return out


def _contains_text(findings: list[dict[str, Any]], token: str) -> bool:
    t = token.strip()
    if not t:
        return False
    for f in findings:
        for field in ("title", "quote", "reason", "suggestion"):
            v = str(f.get(field, ""))
            if t in v:
                return True
    return False


def _get_int(v: Any) -> int | None:
    if v is None or v == "":
        return None
    return int(v)


def _check_bound(name: str, actual: int, min_value: int | None, max_value: int | None) -> list[str]:
    violations: list[str] = []
    if min_value is not None and actual < min_value:
        violations.append(f"{name}={actual} < min_{name}={min_value}")
    if max_value is not None and actual > max_value:
        violations.append(f"{name}={actual} > max_{name}={max_value}")
    return violations


def evaluate_case(case: dict[str, Any], rules: dict[str, Any]) -> EvalCaseResult:
    case_id = str(case.get("id") or "").strip() or "unknown_case"
    doc_type = str(case.get("doc_type") or "").strip()
    text = str(case.get("text") or "")
    expected = case.get("expected") or {}
    if not doc_type:
        raise ValueError(f"[{case_id}] missing required field: doc_type")

    report = run_checks(doc_type, text, rules)
    findings = report.get("findings", [])
    summary = report.get("summary", {})
    categories = {str(f.get("category", "")) for f in findings}

    violations: list[str] = []

    for c in expected.get("required_categories", []):
        if c not in categories:
            violations.append(f"missing required category: {c}")

    for c in expected.get("forbidden_categories", []):
        if c in categories:
            violations.append(f"unexpected category found: {c}")

    for token in expected.get("required_titles_contains", []):
        if not _contains_text(findings, str(token)):
            violations.append(f"required token not found in findings: {token}")

    for token in expected.get("forbidden_titles_contains", []):
        if _contains_text(findings, str(token)):
            violations.append(f"forbidden token found in findings: {token}")

    total = int(summary.get("total", 0))
    high = int(summary.get("high", 0))
    medium = int(summary.get("medium", 0))
    low = int(summary.get("low", 0))

    violations += _check_bound("total", total, _get_int(expected.get("min_total")), _get_int(expected.get("max_total")))
    violations += _check_bound("high", high, _get_int(expected.get("min_high")), _get_int(expected.get("max_high")))
    violations += _check_bound(
        "medium",
        medium,
        _get_int(expected.get("min_medium")),
        _get_int(expected.get("max_medium")),
    )
    violations += _check_bound("low", low, _get_int(expected.get("min_low")), _get_int(expected.get("max_low")))

    return EvalCaseResult(
        case_id=case_id,
        passed=len(violations) == 0,
        violations=violations,
        summary=summary,
        findings=findings,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run sample-based evaluation for compliance checker.")
    parser.add_argument("--rules", default="rules_v1.xlsx", help="Rules xlsx path.")
    parser.add_argument("--cases", default="test_samples/cases.json", help="Sample cases json path.")
    parser.add_argument(
        "--output",
        default="test_samples/last_eval_report.json",
        help="Output report json path.",
    )
    args = parser.parse_args()

    rules_path = (REPO_ROOT / args.rules).resolve() if not Path(args.rules).is_absolute() else Path(args.rules)
    cases_path = (REPO_ROOT / args.cases).resolve() if not Path(args.cases).is_absolute() else Path(args.cases)
    output_path = (REPO_ROOT / args.output).resolve() if not Path(args.output).is_absolute() else Path(args.output)

    rules = load_rules(rules_path)
    cases = _read_cases(cases_path)

    results: list[EvalCaseResult] = []
    for case in cases:
        results.append(evaluate_case(case, rules))

    pass_count = sum(1 for r in results if r.passed)
    fail_count = len(results) - pass_count

    failure_reasons: dict[str, int] = {}
    category_hits: dict[str, int] = {}
    for r in results:
        for v in r.violations:
            failure_reasons[v] = failure_reasons.get(v, 0) + 1
        hit = _count_findings_by_category(r.findings)
        for k, n in hit.items():
            category_hits[k] = category_hits.get(k, 0) + n

    output = {
        "meta": {
            "rules_path": str(rules_path),
            "cases_path": str(cases_path),
            "total_cases": len(results),
            "pass_cases": pass_count,
            "fail_cases": fail_count,
            "pass_rate": round((pass_count / len(results)) * 100, 2) if results else 0.0,
        },
        "aggregate": {
            "failure_reasons": failure_reasons,
            "category_hits": category_hits,
        },
        "results": [
            {
                "id": r.case_id,
                "passed": r.passed,
                "violations": r.violations,
                "summary": r.summary,
                "findings": r.findings,
            }
            for r in results
        ],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Cases: {len(results)} | Pass: {pass_count} | Fail: {fail_count}")
    print(f"Report: {output_path}")
    return 0 if fail_count == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
