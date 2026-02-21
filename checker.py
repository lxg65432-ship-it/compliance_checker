from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

SEV_ORDER = {
    "high": 3,
    "medium": 2,
    "low": 1,
    "高": 3,
    "中": 2,
    "低": 1,
}

SEV_ALIASES = {
    "high": "high",
    "medium": "medium",
    "low": "low",
    "高": "high",
    "中": "medium",
    "低": "low",
}


def _norm_text(text: str) -> str:
    text = text.strip()
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    return text


def _split_keywords(cell: str) -> list[str]:
    s = str(cell).strip()
    if not s:
        return []
    parts = re.split(r"[\/,，、\s]+", s)
    return [p.strip() for p in parts if p.strip()]


def _normalize_severity(sev: str, default: str = "medium") -> str:
    raw = str(sev or "").strip().lower()
    if not raw:
        return default
    return SEV_ALIASES.get(raw, SEV_ALIASES.get(str(sev).strip(), default))


def _is_same_doc_type(rule_doc_type: str, current_doc_type: str) -> bool:
    v = str(rule_doc_type or "").strip()
    if not v:
        return True
    if v.lower() in {"all", "全部"}:
        return True
    return v == str(current_doc_type).strip()


@dataclass
class Finding:
    category: str
    severity: str
    title: str
    quote: str = ""
    reason: str = ""
    suggestion: str = ""


def _sev_sort_key(sev: str) -> int:
    return -SEV_ORDER.get(_normalize_severity(sev), 0)


def check_required_fields(doc_type: str, text: str, df_required) -> list[Finding]:
    findings: list[Finding] = []
    t = _norm_text(text)

    for _, row in df_required.iterrows():
        if not _is_same_doc_type(row.get("doc_type", ""), doc_type):
            continue

        field = str(row.get("field", "")).strip()
        severity = _normalize_severity(row.get("severity", "中"), default="medium")
        hint = str(row.get("hint", "")).strip()

        keys = _split_keywords(row.get("keywords_any", ""))
        if not keys:
            continue

        hit = any(k in t for k in keys)
        if not hit:
            findings.append(
                Finding(
                    category="missing_items",
                    severity=severity,
                    title=f"缺少：{field}",
                    reason=hint or f"未检测到与“{field}”相关的关键词。",
                    suggestion=hint,
                )
            )
    return findings


def check_conditional_required(doc_type: str, text: str, df_cond) -> list[Finding]:
    """
    条件必填：命中 trigger_any 但未命中 required_any 时提示。
    依赖 Excel sheet: conditional_required
    列名：doc_type, trigger_any, required_any, severity, hint
    """
    findings: list[Finding] = []
    t = _norm_text(text)

    for _, row in df_cond.iterrows():
        if not _is_same_doc_type(row.get("doc_type", ""), doc_type):
            continue

        trigger_any = _split_keywords(row.get("trigger_any", ""))
        required_any = _split_keywords(row.get("required_any", ""))
        if not trigger_any or not required_any:
            continue

        severity = _normalize_severity(row.get("severity", "中"), default="medium")
        hint = str(row.get("hint", "")).strip()

        trig_hit = any(k in t for k in trigger_any)
        if not trig_hit:
            continue

        req_hit = any(k in t for k in required_any)
        if not req_hit:
            findings.append(
                Finding(
                    category="missing_items",
                    severity=severity,
                    title="条件必填缺失",
                    quote="触发：" + "/".join(trigger_any[:3]),
                    reason=f"检测到触发关键词，但未检测到要求项：{'/'.join(required_any[:3])}",
                    suggestion=hint or f"建议补充：{'/'.join(required_any)}",
                )
            )

    return findings


def check_forbidden_phrases(doc_type: str, text: str, df_forbidden) -> list[Finding]:
    findings: list[Finding] = []
    t = _norm_text(text)

    for _, row in df_forbidden.iterrows():
        phrase = str(row.get("phrase", "")).strip()
        if not phrase:
            continue

        if not _is_same_doc_type(row.get("doc_type", ""), doc_type):
            continue

        if phrase in t:
            severity = _normalize_severity(row.get("severity", "中"), default="medium")
            risk_reason = str(row.get("risk_reason", "")).strip()
            safe_replace = str(row.get("safe_replace", "")).strip()

            findings.append(
                Finding(
                    category="risky_phrases",
                    severity=severity,
                    title=f"风险用词：{phrase}",
                    quote=phrase,
                    reason=risk_reason or "该表述可能过于绝对或指责性较强，存在合规风险。",
                    suggestion=safe_replace,
                )
            )
    return findings


def check_closure(doc_type: str, text: str, df_closure) -> list[Finding]:
    findings: list[Finding] = []
    t = _norm_text(text)

    for _, row in df_closure.iterrows():
        issue_words = _split_keywords(row.get("issue_words", ""))
        action_words = _split_keywords(row.get("action_words", ""))
        verify_words = _split_keywords(row.get("verify_words", ""))

        severity = _normalize_severity(row.get("severity", "高"), default="high")
        hint = str(row.get("hint", "")).strip()

        if not issue_words:
            continue

        issue_hit = any(w in t for w in issue_words)
        if not issue_hit:
            continue

        action_hit = any(w in t for w in action_words) if action_words else False
        verify_hit = any(w in t for w in verify_words) if verify_words else False

        if not action_hit or not verify_hit:
            missing = []
            if not action_hit:
                missing.append("处理措施")
            if not verify_hit:
                missing.append("复查/结果")

            findings.append(
                Finding(
                    category="closure_issues",
                    severity=severity,
                    title="问题闭环不完整",
                    quote=" / ".join(issue_words[:3]),
                    reason=f"检测到问题描述，但未完整体现：{'+'.join(missing)}",
                    suggestion=hint or "建议补充：已要求/已督促...；已复查，整改完成...（形成闭环）",
                )
            )

    return findings


def check_logic_conflicts(doc_type: str, text: str, df_logic) -> list[Finding]:
    findings: list[Finding] = []
    t = _norm_text(text)

    for _, row in df_logic.iterrows():
        a = _split_keywords(row.get("trigger_a", ""))
        b = _split_keywords(row.get("trigger_b", ""))
        severity = _normalize_severity(row.get("severity", "低"), default="low")
        hint = str(row.get("hint", "")).strip()

        if not a or not b:
            continue

        a_hit = any(x in t for x in a)
        b_hit = any(x in t for x in b)

        if a_hit and b_hit:
            findings.append(
                Finding(
                    category="logic_warnings",
                    severity=severity,
                    title="可能存在逻辑矛盾/缺项",
                    quote=f"{a[0]} & {b[0]}",
                    reason="文本同时命中两个触发条件，建议核对是否需补充说明。",
                    suggestion=hint or "请核对描述是否一致，必要时补充措施或原因说明。",
                )
            )

    return findings


def run_checks(doc_type: str, text: str, rules: dict[str, Any]) -> dict[str, Any]:
    df_required = rules["required_fields"]
    df_forbidden = rules["forbidden_phrases"]
    df_closure = rules["closure_rules"]
    df_logic = rules["logic_conflicts"]
    df_cond = rules.get("conditional_required")

    findings: list[Finding] = []
    findings += check_required_fields(doc_type, text, df_required)

    if df_cond is not None:
        findings += check_conditional_required(doc_type, text, df_cond)

    findings += check_forbidden_phrases(doc_type, text, df_forbidden)
    findings += check_closure(doc_type, text, df_closure)
    findings += check_logic_conflicts(doc_type, text, df_logic)

    findings.sort(key=lambda f: (_sev_sort_key(f.severity), f.category))

    out = {
        "doc_type": doc_type,
        "summary": {
            "high": sum(1 for f in findings if _normalize_severity(f.severity) == "high"),
            "medium": sum(1 for f in findings if _normalize_severity(f.severity) == "medium"),
            "low": sum(1 for f in findings if _normalize_severity(f.severity) == "low"),
            "total": len(findings),
        },
        "findings": [
            {
                "category": f.category,
                "severity": _normalize_severity(f.severity),
                "title": f.title,
                "quote": f.quote,
                "reason": f.reason,
                "suggestion": f.suggestion,
            }
            for f in findings
        ],
        "copy_ready_suggestions": _make_copy_ready_suggestions(findings),
    }
    return out


def _make_copy_ready_suggestions(findings: list[Finding]) -> list[str]:
    s: list[str] = []
    seen = set()
    for f in findings:
        sug = (f.suggestion or "").strip()
        if not sug or len(sug) < 6 or sug in seen:
            continue
        seen.add(sug)
        s.append(sug)

    defaults = [
        "已提示施工单位加强现场管理，并要求按规范落实整改。",
        "已对整改情况进行复查，整改措施落实到位。",
        "关键工序已实施旁站监理，过程受控。",
        "已督促完善安全防护及警示标志，确保施工安全。",
    ]
    for d in defaults:
        if d not in seen:
            s.append(d)
            seen.add(d)
    return s[:12]
