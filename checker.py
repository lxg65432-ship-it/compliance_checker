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


def _is_negated_mention(text: str, phrase: str) -> bool:
    """
    判断某个词是否出现在“否定语境”中，避免误报：
    例如：未见安全隐患、未发现问题、无隐患、没有问题。
    """
    t = _norm_text(text)
    p = str(phrase or "").strip()
    if not p:
        return False

    escaped = re.escape(p)
    patterns = [
        rf"(未见|未发现|未查见|无|没有|未出现)[^。；;\n]{{0,8}}{escaped}",
        rf"{escaped}[^。；;\n]{{0,8}}(未见|未发现|无|没有)",
    ]
    return any(re.search(ptn, t) for ptn in patterns)


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
        suggestion_text = hint
        if suggestion_text.startswith("缺少"):
            suggestion_text = f"建议补充：{suggestion_text.replace('缺少', '', 1).strip()}"
        elif suggestion_text and not suggestion_text.startswith(("建议", "请")):
            suggestion_text = f"建议补充：{suggestion_text}"

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
                    suggestion=suggestion_text,
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
        rule_code = str(row.get("rule_code", "")).strip().lower()

        trig_hit = any(k in t for k in trigger_any)
        if not trig_hit:
            continue

        req_hit = any(k in t for k in required_any)

        # 特殊规则：正常施工作业应体现管理人员与工人数量。
        if rule_code == "personnel_count":
            mgmt_hit = bool(re.search(r"(现场管理人员|管理人员|管理岗|监理人员)", t))
            worker_hit = bool(re.search(r"(工人|作业人员|施工人员)", t))
            count_hit = bool(re.search(r"([0-9]+|[一二三四五六七八九十百]+)\s*(名|人)", t))
            req_hit = mgmt_hit and worker_hit and count_hit

        # 特殊规则：高风险作业应体现安全管理人员/安全员。
        if rule_code == "safety_personnel":
            req_hit = bool(re.search(r"(安全员|专职安全员|安全管理人员)", t))

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
            # “未见/无/未发现 + 词语”场景不按风险词处理，避免误报。
            if _is_negated_mention(t, phrase):
                continue
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

        issue_hit = any((w in t) and (not _is_negated_mention(t, w)) for w in issue_words)
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


def _normalize_conditional_rules(df_cond):
    """
    运行时修正规则，确保人员规则符合当前业务要求：
    1) 正常施工作业必须体现管理人员和工人数量；
    2) 高风险作业必须体现安全员/安全管理人员；
    3) 吊装触发词去除“安装”避免误报。
    """
    if df_cond is None:
        return None

    df = df_cond.copy()
    if "rule_code" not in df.columns:
        df["rule_code"] = ""

    trig = df["trigger_any"].astype(str)

    mask_hoist = trig.str.contains("吊装/起重/安装", regex=False)
    df.loc[mask_hoist, "trigger_any"] = "吊装/起重/吊车/起重机/吊运"
    df.loc[mask_hoist, "required_any"] = "吊车/起重机/吊装/指挥/警戒"
    df.loc[mask_hoist, "hint"] = "吊装作业建议体现起重设备、指挥警戒及安全管理人员"

    mask_person = trig.str.contains("施工/作业/浇筑/摊铺/开挖/吊装/张拉/压实/焊接/切割", regex=False)
    df.loc[mask_person, "required_any"] = "现场管理人员/工人/作业人员/施工人员/名/人"
    df.loc[mask_person, "hint"] = "建议补充现场人员数量：管理人员X名、工人X名"
    df.loc[mask_person, "rule_code"] = "personnel_count"

    mask_xs = trig.str.contains("巡视/检查/整改/隐患/问题", regex=False)
    df.loc[mask_xs, "required_any"] = "施工单位/责任人/管理人员/安全员"
    df.loc[mask_xs, "hint"] = "建议体现责任主体及现场管理/安全人员信息"

    has_safety_rule = (df["rule_code"].astype(str).str.lower() == "safety_personnel").any()
    if not has_safety_rule:
        row = {c: "" for c in df.columns}
        row["doc_type"] = "日志"
        row["trigger_any"] = "吊装/起重/高处/临边/深基坑/开挖/夜间施工/爆破/切割"
        row["required_any"] = "安全员/专职安全员/安全管理人员"
        row["severity"] = "高"
        row["hint"] = "高风险作业建议体现安全管理人员或安全员在场情况"
        row["tag"] = "人员配置"
        row["priority"] = "P0"
        row["rule_code"] = "safety_personnel"
        df.loc[len(df)] = row

    return df


def run_checks(doc_type: str, text: str, rules: dict[str, Any]) -> dict[str, Any]:
    df_required = rules["required_fields"]
    df_forbidden = rules["forbidden_phrases"]
    df_closure = rules["closure_rules"]
    df_logic = rules["logic_conflicts"]
    df_cond = _normalize_conditional_rules(rules.get("conditional_required"))

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
        "full_text_rewrite": _make_full_text_rewrite(doc_type, text, findings),
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


def _make_full_text_rewrite(doc_type: str, text: str, findings: list[Finding]) -> str:
    """
    生成可直接替换的日志草案：
    - 保留原文；
    - 追加针对命中问题的“完善段落”；
    - 避免只给碎片化建议句。
    """
    base = _norm_text(text)
    if not base:
        return ""

    enhanced_lines: list[str] = []
    seen = set()

    has_missing_site = False
    has_personnel_missing = False
    has_closure_issue = False

    for f in findings:
        title = str(f.title or "")
        quote = str(f.quote or "")

        if "缺少：施工部位" in title:
            has_missing_site = True

        if "条件必填缺失" in title and any(k in quote for k in ("施工", "作业", "浇筑")):
            has_personnel_missing = True

        if f.category == "closure_issues":
            has_closure_issue = True

    if has_missing_site:
        enhanced_lines.append("施工部位：请补充明确位置（如：X区X轴线/X楼层X作业面/桩号KX+XXX段）。")

    if has_personnel_missing:
        enhanced_lines.append("现场人员：管理人员X名（监理X名、施工管理X名），作业人员X名。")

    if has_closure_issue:
        enhanced_lines.append("整改闭环：已要求施工单位整改，并于X时复查，整改完成，满足要求。")

    # 兜底：若没有结构化增强项，仍提供一条可直接替换的收尾完善句。
    if not enhanced_lines:
        enhanced_lines.append("补充记录：现场检查总体受控，后续将持续跟踪并复查关键工序落实情况。")

    suffix = "\n".join(enhanced_lines)
    if base.endswith(("。", "！", "？")):
        return f"{base}\n{suffix}"
    return f"{base}。\n{suffix}"
