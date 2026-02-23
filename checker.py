from __future__ import annotations

from dataclasses import dataclass
import os
import re
from typing import Any, Callable, Protocol

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

    def _is_construction_content_hit(raw_text: str, keys: list[str]) -> bool:
        """
        对“施工内容”采用宽松多信号判定，避免：
        1) 仅靠“施工/检查”等泛词误判为已填写；
        2) 规则过严导致正常工序描述被误报。
        """
        strong_words = [
            "浇筑",
            "绑扎",
            "焊接",
            "切割",
            "摊铺",
            "压实",
            "开挖",
            "回填",
            "吊装",
            "张拉",
            "压浆",
            "送检",
            "取样",
            "验槽",
            "成孔",
            "灌注",
            "安装",
            "铺设",
            "调试",
        ]
        object_words = [
            "钢筋",
            "混凝土",
            "模板",
            "沥青",
            "管道",
            "支座",
            "梁板",
            "路基",
            "路面",
            "桩",
            "沟槽",
            "试块",
            "试件",
        ]
        weak_words = [
            "施工",
            "作业",
            "检测",
            "检查",
            "维护",
            "整改",
        ]

        # 信号1：出现强工序词
        if any(w in raw_text for w in strong_words):
            return True

        # 信号2：出现“动作+对象”的自然工序表达（不要求死板固定搭配）
        action_pattern = (
            r"(进行|开展|实施|完成|组织|安排|采用|已)?"
            r"(浇筑|绑扎|焊接|切割|摊铺|压实|开挖|回填|吊装|张拉|压浆|安装|铺设|调试)"
            r".{0,8}"
            r"(钢筋|混凝土|模板|沥青|管道|支座|梁板|路基|路面|桩|沟槽|试块|试件)"
        )
        if re.search(action_pattern, raw_text):
            return True

        # 信号3：命中至少两个非泛词关键词，也可视为内容已写明
        key_hits = [k for k in keys if k and k in raw_text]
        non_weak_hits = [k for k in key_hits if k not in weak_words]
        if len(set(non_weak_hits)) >= 2:
            return True

        # 仅泛词（施工/作业/检测/检查）不判定为“施工内容完整”
        return False

    def _is_site_location_hit(raw_text: str, keys: list[str]) -> bool:
        """
        “施工部位”判定：
        - 支持常见位置表达（楼栋/楼层/轴线/桩号/区段等）；
        - 避免把孤立字符（如单个 K）误判为已填写部位。
        """
        patterns = [
            r"\d+#楼",
            r"[一二三四五六七八九十\d]+层",
            r"[A-Z]-?\d+轴",
            r"[A-Z]?\d+\+\d+",
            r"K\d+\+\d+",
            r"\d+\s*(号|#)\s*(墩|台|楼|孔|桩|井|段|塔|梁)",
            r"[A-Za-z]?\d+\s*(墩|台|楼|孔|桩|井|段|塔|梁)",
            r"(墩|台)\s*\d+",
            r"\d+\s*-\s*\d+\s*轴",
            r"(左|右|中)幅",
            r"(上游|下游|内侧|外侧)",
            r"[左右]幅",
            r"(东侧|西侧|南侧|北侧)",
            r"(标段|区段|工点|作业面|施工段|部位)",
            r"(桥台|桥墩|涵洞|隧道|基坑|沟槽|梁板|顶板|底板)",
        ]
        if any(re.search(p, raw_text) for p in patterns):
            return True

        for k in keys:
            if not k:
                continue
            # 单字符关键词仅在结构化桩号表达中视为有效（如 K0+800）
            if len(k) == 1:
                if k.upper() == "K" and re.search(r"K\d+\+\d+", raw_text):
                    return True
                continue
            if k in raw_text:
                return True
        return False

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
        if field == "施工内容":
            hit = _is_construction_content_hit(t, keys)
        elif field == "施工部位":
            hit = _is_site_location_hit(t, keys)
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
    pending: list[tuple[Finding, str, str, str]] = []
    t = _norm_text(text)

    def _is_equipment_required(required_keys: list[str]) -> bool:
        equipment_words = {
            "摊铺机",
            "运输车",
            "压路机",
            "振动压路机",
            "夯实机",
            "平板夯",
            "吊车",
            "起重机",
            "泵车",
            "罐车",
            "振捣器",
            "挖机",
            "装载机",
            "自卸车",
        }
        return any(k in equipment_words for k in required_keys)

    def _is_material_required(required_keys: list[str]) -> bool:
        material_words = {
            "混凝土",
            "坍落度",
            "试件",
            "配合比",
            "强度",
            "钢筋",
            "HRB",
            "直径",
            "接头",
            "焊条",
            "套筒",
            "沥青",
            "混合料",
            "油石比",
            "级配",
            "水泥",
            "含水量",
            "管材",
            "砂石",
            "垫层",
            "回填料",
            "卷材",
            "涂料",
            "厚度",
            "搭接",
            "合格证",
            "复试",
        }
        return any(k in material_words for k in required_keys)

    def _is_execution_context(raw_text: str) -> bool:
        # 明确施工进行语境
        exec_words = (
            "正在",
            "进行",
            "开展",
            "实施",
            "作业",
            "浇筑",
            "摊铺",
            "压实",
            "开挖",
            "吊装",
            "泵送",
            "回填",
            "碾压",
            "完成",
        )
        # 纯计划语境，不应强触发设备类缺项
        plan_words = ("计划", "拟", "将于", "明日", "明天", "后续")
        has_exec = any(w in raw_text for w in exec_words)
        has_generic_construction = "施工" in raw_text
        has_plan = any(w in raw_text for w in plan_words)
        if has_exec:
            return True
        if has_generic_construction and not has_plan:
            return True
        return False

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
        # personnel_count 使用更严格触发，避免“施工单位”等词造成误触发。
        if rule_code == "personnel_count":
            trig_hit = bool(
                re.search(
                    r"(作业|浇筑|摊铺|开挖|吊装|张拉|压实|焊接|切割|施工(?!单位))",
                    t,
                )
            )
        # 设备类要求只在“明确正在实施”的语境下触发，避免计划性文本误报。
        if _is_equipment_required(required_any) and not _is_execution_context(t):
            trig_hit = False
        # 材料类要求同样需要执行或质量语境，避免“计划/概述”文本触发噪声。
        if _is_material_required(required_any):
            quality_context_words = (
                "材料",
                "合格证",
                "复试",
                "试验",
                "检测",
                "取样",
                "送检",
                "配合比",
                "坍落度",
                "强度",
                "油石比",
                "级配",
                "含水量",
                "HRB",
                "直径",
                "套筒",
                "焊条",
                "卷材",
                "涂料",
                "厚度",
                "搭接",
            )
            has_quality_context = any(w in t for w in quality_context_words)
            if not (_is_execution_context(t) or has_quality_context):
                trig_hit = False
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
            f = Finding(
                category="missing_items",
                severity=severity,
                title="条件必填缺失",
                quote="触发：" + "/".join(trigger_any[:3]),
                reason=f"检测到触发关键词，但未检测到要求项：{'/'.join(required_any[:3])}",
                suggestion=hint or f"建议补充：{'/'.join(required_any)}",
            )
            pending.append((f, "/".join(trigger_any), "/".join(required_any), rule_code))

    if not pending:
        return findings

    def _is_concrete_related(trigger: str) -> bool:
        return any(k in trigger for k in ("混凝土", "浇筑", "砼", "泵送"))

    def _priority(required: str) -> int:
        # 优先保留质量闭环相关项，压低设备类提示，减少同类噪声。
        if any(k in required for k in ("试件", "取样", "送检")):
            return 0
        if any(k in required for k in ("旁站", "全过程监督", "见证")):
            return 1
        if any(k in required for k in ("管理人员", "工人", "作业人员")):
            return 2
        return 3

    concrete: list[tuple[Finding, str, str, str]] = []
    others: list[tuple[Finding, str, str, str]] = []
    for item in pending:
        if _is_concrete_related(item[1]):
            concrete.append(item)
        else:
            others.append(item)

    if concrete:
        concrete.sort(key=lambda x: (_priority(x[2]), x[0].quote))
        # 同一日志内混凝土类条件项最多保留两条，降低重复提示。
        concrete = concrete[:2]

    merged = others + concrete
    merged.sort(key=lambda x: (_priority(x[2]), x[0].quote))

    # 去重：同一 rule_code + 要求项组合只保留一条，避免同类提示刷屏。
    seen_conditional_signatures: set[tuple[str, str]] = set()
    for f, _trigger, required, rule_code in merged:
        sig = (rule_code or "", required)
        if sig in seen_conditional_signatures:
            continue
        seen_conditional_signatures.add(sig)
        findings.append(f)
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
    seen_missing_signatures: set[tuple[str, ...]] = set()

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
            missing_sig = tuple(missing)
            if missing_sig in seen_missing_signatures:
                continue
            seen_missing_signatures.add(missing_sig)

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


def check_semantic_negative_patterns(doc_type: str, text: str) -> list[Finding]:
    """
    轻量语义规则：覆盖“未见/无/口头整改/结论与事实冲突”等弱结构化问题。
    不依赖 AI，仅用可解释的模式匹配，避免当前纯关键词规则漏检。
    """
    findings: list[Finding] = []
    t = _norm_text(text)
    if not t:
        return findings

    seen_titles: set[str] = set()

    def _push(category: str, severity: str, title: str, quote: str, reason: str, suggestion: str) -> None:
        if title in seen_titles:
            return
        seen_titles.add(title)
        findings.append(
            Finding(
                category=category,
                severity=severity,
                title=title,
                quote=quote,
                reason=reason,
                suggestion=suggestion,
            )
        )

    # 1) 恶劣天气+高风险作业仍继续。
    bad_weather = re.search(r"(大雨|暴雨|雷雨|大风|强风|雨中)", t)
    risky_work = re.search(r"(吊装|起重|高空|高处|临边|张拉)", t)
    keep_working = re.search(r"(继续作业|继续施工|同意继续|正常施工)", t)
    if bad_weather and risky_work and keep_working:
        _push(
            category="logic_warnings",
            severity="high",
            title="恶劣天气施工风险",
            quote="恶劣天气/高风险作业/继续施工",
            reason="检测到恶劣天气下仍继续高风险作业，存在较大安全风险。",
            suggestion="建议补充：停工或风险评估结论、专项审批及现场防护措施。",
        )

    # 2) 口头整改但缺复查闭环。
    has_oral_fix = re.search(r"(口头要求整改|已口头要求整改|口头整改)", t)
    has_recheck = re.search(r"(复查|复检|整改完成|闭环)", t)
    if has_oral_fix and not has_recheck:
        _push(
            category="closure_issues",
            severity="medium",
            title="口头整改未形成闭环",
            quote="口头整改",
            reason="文本仅体现口头整改，未见复查结果或闭环证据。",
            suggestion="建议补充：整改责任人、整改时限、复查时间和复查结论。",
        )

    # 3) 施工员代写监理日志/监理履职边界不清。
    if re.search(r"记录人[:：].{0,12}施工员", t):
        _push(
            category="logic_warnings",
            severity="medium",
            title="监理记录主体疑似不规范",
            quote="记录人：施工员",
            reason="日志记录主体出现施工员，可能与监理日志责任边界不一致。",
            suggestion="建议补充：监理人员签名及旁站/巡视记录，明确责任主体。",
        )

    # 4) 发现问题但结论直接“合格/符合/同意继续”。
    has_problem = re.search(r"(发现|存在|偏大|缺失|不完整|隐患|漏浆|塌方|起泡|渗漏)", t)
    has_positive_conclusion = re.search(r"(质量合格|符合设计要求|基本受控|同意继续|可投入使用)", t)
    if has_problem and has_positive_conclusion:
        _push(
            category="logic_warnings",
            severity="medium",
            title="结论与问题描述可能不一致",
            quote="发现问题 + 合格/继续结论",
            reason="文本同时出现问题描述与直接放行结论，建议核对是否已完成整改与复查。",
            suggestion="建议补充：问题整改措施、复查记录及放行依据。",
        )

    # 5) 套话化表述：缺少部位/工序/数据支撑。
    cliche = re.search(r"(整体正常|质量良好|进度满足计划|安全生产形势稳定|继续施工)", t)
    has_number = re.search(r"[0-9一二三四五六七八九十]+", t)
    has_site_or_step = re.search(r"(施工部位|浇筑|摊铺|开挖|张拉|吊装|压实|安装|桩号|轴线|楼层|墩|台)", t)
    if cliche and (not has_number or not has_site_or_step):
        _push(
            category="missing_items",
            severity="low",
            title="记录内容偏模板化",
            quote="整体正常/继续施工",
            reason="描述偏概括，缺少可追溯的部位、工序或量化数据。",
            suggestion="建议补充：施工部位、具体工序、检测数据及处理结果。",
        )

    # 6) 验收/签认类记录缺失。
    if re.search(r"(未见|未记录|未体现|未说明|无).{0,10}(验收|签认|签字|报验|隐检|隐蔽验收)", t):
        _push(
            category="missing_items",
            severity="medium",
            title="验收签认信息缺失",
            quote="验收/签认/报验",
            reason="检测到验收签认相关信息缺失，无法形成放行依据。",
            suggestion="建议补充：验收程序、签认人员、报验记录及结论。",
        )

    # 7) 检测/监测类数据缺失。
    if re.search(r"(未见|未记录|未说明|无).{0,12}(检测|监测|试验|抽检|数据|压实度|坍落度|温度|压降|方量)", t):
        _push(
            category="missing_items",
            severity="medium",
            title="检测监测数据缺失",
            quote="检测/监测/试验数据",
            reason="检测到关键检测监测数据缺失，质量判断依据不足。",
            suggestion="建议补充：检测点位、实测数值、判定标准和结论。",
        )

    # 8) 隐患场景未停工或未升级处置。
    if re.search(
        r"(塌方|失稳|裂缝|开裂|隐患|大雨|大风|基坑|积水).{0,24}(继续施工|继续作业|同意继续|未停工|未暂停|仍继续)",
        t,
    ) or (
        re.search(r"(基坑|积水|开裂|支护)", t) and re.search(r"(注意排水|雨停后处理)", t)
    ):
        _push(
            category="logic_warnings",
            severity="high",
            title="风险处置升级不足",
            quote="隐患/继续施工",
            reason="检测到风险事件后仍继续施工，未体现停工或升级处置。",
            suggestion="建议补充：停工指令、会商结论、加固措施与复工条件。",
        )

    # 9) 动火安全管理缺失。
    if re.search(r"(焊接|切割|动火).{0,24}(未见|无|未记录|未提供).{0,10}(审批|灭火器|防火毯|隔离|监护|消防)", t):
        _push(
            category="missing_items",
            severity="high",
            title="动火安全措施缺失",
            quote="动火审批/消防隔离",
            reason="检测到动火作业，但未体现审批及消防隔离监护措施。",
            suggestion="建议补充：动火审批单、灭火器配置、隔离措施和现场监护记录。",
        )

    # 10) 材料追溯资料缺失。
    if re.search(r"(未见|未记录|未提供|无).{0,10}(批次|台账|编号|复试|合格证|追溯)", t):
        _push(
            category="missing_items",
            severity="medium",
            title="材料追溯资料缺失",
            quote="批次/台账/复试",
            reason="检测到材料追溯相关资料缺失，质量可追溯性不足。",
            suggestion="建议补充：批次编号、台账、复试报告及对应关系。",
        )

    # 11) 量具/设备校验有效期缺失。
    if re.search(r"(压力表|油表|千斤顶|量具|仪器).{0,16}(未校验|未核验|无.{0,6}(校验|证书|有效期))", t):
        _push(
            category="missing_items",
            severity="medium",
            title="设备量具校验信息缺失",
            quote="校验/有效期",
            reason="检测到关键设备或量具缺少校验有效期信息。",
            suggestion="建议补充：校验证书编号、有效期和使用确认记录。",
        )

    # 12) 有限空间作业控制缺失。
    if re.search(r"(井内|有限空间|接收井).{0,24}(未见|未记录|无).{0,10}(气体检测|通风|监护|应急)", t):
        _push(
            category="missing_items",
            severity="high",
            title="有限空间作业控制缺失",
            quote="气体检测/通风/监护",
            reason="检测到有限空间作业控制措施缺失，存在较高安全风险。",
            suggestion="建议补充：气体检测、通风、监护安排和应急预案执行记录。",
        )

    # 13) 交通导改与留证缺失。
    if re.search(r"(导改|围挡|临时通行|警示灯|反光).{0,24}(未见|未记录|无|缺失).{0,10}(验收|照片|留证|影像|引导)", t):
        _push(
            category="missing_items",
            severity="medium",
            title="导改验收留证缺失",
            quote="导改/留证",
            reason="检测到导改通行措施缺少验收留证信息。",
            suggestion="建议补充：导改验收记录、影像编号和现场引导措施。",
        )

    # 14) 漏浆/离析等缺陷仅简单处理，未形成复查闭环。
    if re.search(r"(漏浆|离析|起泡|翘边|蜂窝|麻面)", t) and re.search(r"(简单封堵|简单处理|回补找平|后期再调)", t):
        if not re.search(r"(复查|复检|返工|整改完成|闭环)", t):
            _push(
                category="closure_issues",
                severity="medium",
                title="缺陷处置闭环不足",
                quote="漏浆/离析/简单处理",
                reason="检测到质量缺陷仅简单处置，未体现复检复查闭环。",
                suggestion="建议补充：返工或修补措施、复检结果和闭环记录。",
            )

    # 15) 养护措施记录不足（时间/责任人/频次缺失）。
    if re.search(r"(养护|保湿|洒水|覆盖|自然养护)", t):
        lacks_core = not re.search(r"(开始时间|责任人|频次|每日|每班|巡查)", t)
        weak_mode = re.search(r"(自然养护|未覆盖|未.*洒水|未写措施)", t)
        if weak_mode or lacks_core:
            _push(
                category="missing_items",
                severity="medium",
                title="养护措施记录不完整",
                quote="养护/洒水/覆盖",
                reason="检测到养护描述缺少时间、责任人或巡查频次等关键信息。",
                suggestion="建议补充：养护开始时间、责任人、频次及巡查记录。",
            )

    # 16) 雨天沥青摊铺仍继续，停工/调整措施缺失。
    if re.search(r"(雨天|雨中|小雨|中雨|大雨)", t) and re.search(r"(沥青|摊铺|碾压)", t):
        if not re.search(r"(停工|暂停|改期|覆盖|排水|调整工序|监理通知)", t):
            _push(
                category="logic_warnings",
                severity="high",
                title="雨天摊铺管控不足",
                quote="雨天/沥青摊铺",
                reason="检测到雨天沥青施工但未体现停工或调整控制措施。",
                suggestion="建议补充：停工或调整工序依据、现场防雨排水和监理指令留痕。",
            )

    # 17) 支架/脚手架存在构造问题但缺验收放行依据。
    if re.search(r"(支架|脚手架)", t):
        has_struct_risk = re.search(r"(垫板|剪刀撑|连墙件).{0,8}(未|不连续|偏大|不足)", t)
        lacks_accept = re.search(r"(未见|无|未提供).{0,10}(验收|验收表|签字|签认|计算书|专项方案)", t)
        if has_struct_risk or lacks_accept:
            _push(
                category="missing_items",
                severity="high",
                title="支架验收与构造控制不足",
                quote="支架/验收/构造",
                reason="检测到支架构造风险或验收资料缺失，放行依据不足。",
                suggestion="建议补充：专项方案、计算书、验收签字及整改复查记录。",
            )

    # 18) 关键部位检查缺少量化实测。
    if re.search(r"(抽查|检查|间距|偏差|部位|关键部位)", t):
        if re.search(r"(未记录|未写|未体现|无).{0,12}(点位|实测|数值|偏差范围|结论)", t):
            _push(
                category="missing_items",
                severity="medium",
                title="关键部位实测量化不足",
                quote="点位/实测/偏差",
                reason="检测到关键部位检查描述，但缺少点位和实测量化数据。",
                suggestion="建议补充：抽查点位、实测数值、偏差判定和结论。",
            )

    # 19) 浇筑放行控制点不足（未整改不得浇筑）。
    if re.search(r"(浇筑前|准备浇筑|拟浇筑|浇筑)", t) and re.search(r"(承诺|后续补齐|整改)", t):
        if not re.search(r"(未整改不得浇筑|停工指令|复验签认|旁站要求)", t):
            _push(
                category="logic_warnings",
                severity="medium",
                title="浇筑前放行控制不足",
                quote="浇筑前/整改承诺",
                reason="检测到问题仅口头承诺整改，未体现浇筑前复验放行控制。",
                suggestion="建议补充：未整改不得浇筑、复验签认和旁站要求。",
            )

    # 20) 干缩/裂缝等缺陷处置记录不足。
    if re.search(r"(干缩|裂缝|掉角|起泡|翘边)", t):
        if not re.search(r"(封闭养护|修补方案|返工|复查结论|通知单)", t):
            _push(
                category="closure_issues",
                severity="medium",
                title="缺陷处置记录不明确",
                quote="干缩/裂缝/缺陷",
                reason="检测到缺陷迹象，但未体现处置方案与复查结论。",
                suggestion="建议补充：处置措施、复查结果及质量问题通知记录。",
            )

    # 21) 漏浆仅砂浆抹补，未体现拆检与复查。
    if re.search(r"(漏浆)", t) and re.search(r"(砂浆抹补|抹补)", t):
        if not re.search(r"(拆模后检查|凿除|复检|复查|闭环)", t):
            _push(
                category="closure_issues",
                severity="medium",
                title="漏浆处置与复查不足",
                quote="漏浆/砂浆抹补",
                reason="检测到漏浆仅抹补，未体现实体检查与复查闭环。",
                suggestion="建议补充：拆模后实体检查、必要凿除修补及复查结论。",
            )

    # 22) 支架资料核验缺失（计算书/预压方案/沉降布点）。
    if re.search(r"(支架|预压)", t):
        if re.search(r"(未提供|未见|无).{0,14}(计算书|预压方案|沉降观测|布点|验收表)", t):
            _push(
                category="missing_items",
                severity="high",
                title="支架资料核验缺失",
                quote="计算书/预压方案/沉降观测",
                reason="检测到支架关键核验资料缺失，无法支撑放行。",
                suggestion="建议补充：计算书、预压方案、沉降观测布点和验收签认记录。",
            )

    # 23) 关键部位检查未量化（抽查/间距/偏差仅定性）。
    if re.search(r"(抽查|间距|偏差|加密区)", t):
        if re.search(r"(未记录|未写|无).{0,12}(点位|实测|数值|偏差范围)", t) or not re.search(
            r"([0-9]+|一|二|三|四|五|六|七|八|九|十).{0,3}(mm|cm|m|处|点)",
            t,
        ):
            _push(
                category="missing_items",
                severity="medium",
                title="关键部位量化数据不足",
                quote="抽查/间距/偏差",
                reason="检测到关键部位检查缺少点位或实测量化数据。",
                suggestion="建议补充：抽查点位、实测数值、偏差范围与判定结论。",
            )

    # 24) 高处重大隐患仅口头提醒，未停工闭环。
    if re.search(r"(高处|临边|未系安全带|无防护网)", t):
        if re.search(r"(口头提醒|短暂停止|随后又继续|继续)", t) and not re.search(r"(停工|复工手续|整改完成)", t):
            _push(
                category="logic_warnings",
                severity="high",
                title="高处隐患停工闭环不足",
                quote="高处隐患/继续施工",
                reason="检测到高处隐患后仅口头处置且继续施工，未形成停复工闭环。",
                suggestion="建议补充：停工指令、整改验收、复工手续与复查结论。",
            )

    # 25) 材料受潮结块仍“先用掉”。
    if re.search(r"(受潮|结块|破损|标识不清)", t) and re.search(r"(先用掉|继续使用|允许使用)", t):
        _push(
            category="logic_warnings",
            severity="high",
            title="不合格材料处置不当",
            quote="受潮结块/继续使用",
            reason="检测到疑似不合格材料仍计划继续使用，存在质量风险。",
            suggestion="建议补充：隔离标识、复检或退场处理及复查记录。",
        )

    # 26) 导改通道占用与通行放行冲突。
    if re.search(r"(导改|围挡|通道)", t) and re.search(r"(占用|被占)", t):
        if re.search(r"(同意临时通行|继续通行|允许通行)", t) and not re.search(r"(清理|绕行|整改完成|复查)", t):
            _push(
                category="logic_warnings",
                severity="medium",
                title="导改通道占用放行不当",
                quote="通道占用/同意通行",
                reason="检测到通道占用情况下仍放行，未体现先整改后通行控制。",
                suggestion="建议补充：立即清理、绕行引导、复查确认后通行。",
            )

    # 27) 路基弹簧土风险未体现返工复压。
    if re.search(r"(弹簧土|边坡)", t) and re.search(r"(继续填筑|继续施工)", t):
        if not re.search(r"(返工|复压|停工|复查)", t):
            _push(
                category="logic_warnings",
                severity="medium",
                title="路基风险处置不充分",
                quote="弹簧土/继续填筑",
                reason="检测到路基异常后继续施工，未体现返工复压或复查控制。",
                suggestion="建议补充：返工处理、复压与复查记录后再放行。",
            )

    # 28) 试压量具校验缺失且直接判定通过。
    if re.search(r"(试压|压力表|油表)", t):
        if re.search(r"(未见|未提供|无).{0,8}(校验|校验证明|有效期)", t):
            _push(
                category="missing_items",
                severity="medium",
                title="试压量具校验依据缺失",
                quote="试压表/校验",
                reason="检测到试压量具未见校验有效期证明，结论依据不足。",
                suggestion="建议补充：校验证书、有效期和更换复测记录。",
            )

    # 29) 预应力张拉记录关键参数缺失。
    if re.search(r"(预应力|张拉)", t):
        lacks_data = re.search(r"(未记录|未填写|仅填写|未写|不完整|缺失).{0,12}(伸长量|回缩量|持荷|顺序|分级|张拉力)", t)
        lacks_cal = re.search(r"(千斤顶|油表).{0,16}(未校验|未核验|无.{0,6}校验|校验.{0,6}未提供)", t)
        if lacks_data:
            _push(
                category="missing_items",
                severity="medium",
                title="预应力张拉关键数据缺失",
                quote="张拉/伸长量/持荷",
                reason="检测到预应力张拉记录缺少关键参数，无法完整判定质量。",
                suggestion="建议补充：张拉力、伸长量、回缩量、持荷时间及顺序记录。",
            )
        if lacks_cal:
            _push(
                category="missing_items",
                severity="medium",
                title="张拉设备校验信息缺失",
                quote="千斤顶/油表校验",
                reason="检测到张拉设备或量具校验依据缺失。",
                suggestion="建议补充：千斤顶/油表校验证书及有效期。",
            )

    # 30) 大风吊装未体现测风与停吊控制。
    if re.search(r"(吊装|起重)", t) and re.search(r"(大风|阵风)", t):
        if not re.search(r"(风速|测风|停吊|暂停|限制作业)", t):
            _push(
                category="logic_warnings",
                severity="high",
                title="大风吊装管控不足",
                quote="大风/吊装",
                reason="检测到大风条件吊装，未体现测风与停吊控制。",
                suggestion="建议补充：风速记录、停吊阈值及现场执行措施。",
            )

    # 31) 吊装警戒和指挥不规范。
    if re.search(r"(吊装|起重|警戒线|指挥)", t) and re.search(r"(未封闭|混乱|不到位|不规范)", t):
        _push(
            category="missing_items",
            severity="high",
            title="吊装警戒指挥措施不足",
            quote="警戒/指挥",
            reason="检测到吊装警戒或指挥措施不规范，存在安全风险。",
            suggestion="建议补充：封控范围、统一指挥和现场安全指令记录。",
        )

    # 32) 特种设备加节后未验收即使用。
    if re.search(r"(塔吊|加节|特种设备)", t) and re.search(r"(即投入|直接投入|未验收即使用|未提供第三方检测)", t):
        _push(
            category="logic_warnings",
            severity="high",
            title="特种设备未验收即使用",
            quote="加节/验收/检测",
            reason="检测到特种设备加节后未完成验收检测即投入使用。",
            suggestion="建议补充：验收记录、第三方检测报告和使用批准手续。",
        )

    # 33) 雨天砌筑或砂浆质量控制不足。
    if re.search(r"(砌筑|砂浆)", t) and re.search(r"(小雨|雨天|未搭棚|较稀|不饱满)", t):
        _push(
            category="missing_items",
            severity="medium",
            title="砌筑施工条件与质量控制不足",
            quote="雨天砌筑/砂浆质量",
            reason="检测到雨天砌筑或砂浆质量异常，未体现有效防护与处置。",
            suggestion="建议补充：防雨措施、砂浆质量控制、返工复查与强度验证。",
        )

    # 34) 水质检测与投用流程缺失。
    if re.search(r"(给水|消毒|冲洗|接通用户管网|投入使用)", t):
        if re.search(r"(未提供|未见|无).{0,10}(水质检测|检测报告)", t):
            _push(
                category="missing_items",
                severity="high",
                title="给水投用前检测流程缺失",
                quote="水质检测/投用",
                reason="检测到给水投用前缺少水质检测报告，存在公共安全风险。",
                suggestion="建议补充：检测报告、复验结论及投用审批记录。",
            )
        if re.search(r"(投加量|接触时间|排放去向)", t) and re.search(r"(未记录|缺失|未写|无)", t):
            _push(
                category="missing_items",
                severity="medium",
                title="给水消毒过程记录缺失",
                quote="投加量/接触时间",
                reason="检测到给水消毒关键过程记录缺失，过程不可追溯。",
                suggestion="建议补充：投加量、接触时间、排放去向及复核记录。",
            )

    # 35) 注浆/压浆关键参数缺失。
    if re.search(r"(注浆|压浆)", t) and re.search(r"(仅写|未记录|未填写|缺失).{0,12}(配比|压力|用量|流动度|保压|回浆)", t):
        _push(
            category="missing_items",
            severity="medium",
            title="注压浆关键参数记录不足",
            quote="注浆/压浆参数",
            reason="检测到注压浆关键工艺参数缺失，质量可追溯性不足。",
            suggestion="建议补充：配比、压力、用量、流动度、保压与回浆记录。",
        )

    # 36) 设备带病作业（漏油等）未处置。
    if re.search(r"(漏油|设备异常|指针回零不灵|带病作业)", t) and re.search(r"(继续|完成|抓紧)", t):
        _push(
            category="logic_warnings",
            severity="medium",
            title="设备异常处置不充分",
            quote="漏油/异常/继续作业",
            reason="检测到设备异常后仍继续作业，未体现停机处置与复检。",
            suggestion="建议补充：停机检修、污染处置、复检和恢复条件。",
        )

    # 37) 临电高风险隐患未闭环。
    if re.search(r"(配电箱|漏保|电缆|积水|临电)", t) and re.search(r"(未上锁|未试跳|拖地|积水)", t):
        _push(
            category="missing_items",
            severity="high",
            title="临电安全隐患处置不足",
            quote="配电箱/漏保/电缆",
            reason="检测到临电高风险隐患，未体现停用整改与复查闭环。",
            suggestion="建议补充：停用措施、整改时限、复查结论和影像留证。",
        )

    # 38) 停工后复工程序缺失。
    if re.search(r"(停工|整改停工)", t) and re.search(r"(自行恢复|擅自复工|正常施工)", t):
        if not re.search(r"(复工报审|复查记录|复工批准|复工条件)", t):
            _push(
                category="logic_warnings",
                severity="high",
                title="停复工程序执行不足",
                quote="停工/擅自复工",
                reason="检测到停工后复工程序缺失，流程合规风险较高。",
                suggestion="建议补充：复工报审、复查记录和批准手续。",
            )

    # 39) 监理意见导向不当（风险未控却强调抢进度）。
    if re.search(r"(加快进度|抓紧完成|尽快浇筑|继续施工)", t) and re.search(r"(隐患|风险|缺失|未|异常|不足)", t):
        _push(
            category="logic_warnings",
            severity="medium",
            title="监理意见导向不当",
            quote="风险未控/加快进度",
            reason="检测到风险未闭环情况下仍强调抢进度，导向存在偏差。",
            suggestion="建议补充：风险控制优先、整改闭环后放行。",
        )

    # 40) 验收程序不完整：监理未签且已投入使用。
    if re.search(r"(验收表|验收).{0,14}(监理未签|未签)", t) and re.search(r"(已开始|已投入|已开展)", t):
        _push(
            category="logic_warnings",
            severity="high",
            title="验收程序不完整",
            quote="监理未签/已投入使用",
            reason="检测到验收程序未闭合即投入使用，存在流程风险。",
            suggestion="建议补充：联合验收签字、整改复查和复工条件。",
        )

    # 41) 未达强度即拆模。
    if re.search(r"(拆模|模板拆除)", t) and re.search(r"(未提供|无|缺).{0,10}(强度报告|同条件试块|试块强度)", t):
        _push(
            category="logic_warnings",
            severity="high",
            title="未达强度拆模风险",
            quote="拆模/强度报告缺失",
            reason="检测到拆模缺少强度依据，存在结构质量风险。",
            suggestion="建议补充：同条件强度报告，未达条件不得拆模。",
        )

    # 42) 特种设备资料追溯缺失（资质/证书/检测编号）。
    if re.search(r"(塔吊|加节|安装单位)", t) and re.search(r"(缺|未提供|无).{0,14}(资质|证书|检测报告|编号)", t):
        _push(
            category="missing_items",
            severity="medium",
            title="特种设备资料追溯缺失",
            quote="资质/证书/检测编号",
            reason="检测到特种设备关键资料缺失，追溯性不足。",
            suggestion="建议补充：安装单位资质、人员证书、检测报告编号。",
        )

    # 43) 标高偏差“后续再调”处理不当。
    if re.search(r"(标高).{0,8}(偏低|偏高|偏差)", t) and re.search(r"(后期|铺面时).{0,6}(再抬|再调)", t):
        _push(
            category="logic_warnings",
            severity="medium",
            title="标高偏差处置不当",
            quote="标高偏差/后续再调",
            reason="检测到标高偏差未即时整改，拟以后续工序替代处理。",
            suggestion="建议补充：立即调整并复测确认后进入下一工序。",
        )

    # 44) 焊接检验项目缺失（探伤/外观尺寸复测）。
    if re.search(r"(焊接|焊缝)", t) and re.search(r"(未做|未见|未记录|无).{0,12}(探伤|外观尺寸|复测|检验)", t):
        _push(
            category="missing_items",
            severity="medium",
            title="焊接检验项目缺失",
            quote="探伤/外观尺寸复测",
            reason="检测到焊接质量检验项目缺失，验收依据不足。",
            suggestion="建议补充：外观尺寸检查、必要探伤及检验报告。",
        )

    # 45) 注浆记录仅“已注满”不可追溯。
    if re.search(r"(注浆|压浆)", t) and re.search(r"(仅写|仅记|只写).{0,8}(注满|完成)", t):
        _push(
            category="missing_items",
            severity="medium",
            title="注浆质量记录不可追溯",
            quote="仅写注满",
            reason="检测到注浆记录过于笼统，缺少可追溯工艺参数。",
            suggestion="建议补充：配比、压力、用量、回浆与旁站记录。",
        )

    # 46) 异议处理程序缺失：仅“影响不大”直接放行。
    if re.search(r"(影响不大|按经验做|不影响使用)", t) and re.search(r"(监理意见|合格|满足使用要求|基本合格)", t):
        if not re.search(r"(技术核定|设计确认|变更|会商|复核结论)", t):
            _push(
                category="logic_warnings",
                severity="medium",
                title="异议处理程序缺失",
                quote="影响不大/直接放行",
                reason="检测到施工异议仅口头说明即放行，未体现技术核定或设计确认流程。",
                suggestion="建议补充：技术核定、设计确认、会商纪要和复核结论。",
            )

    # 47) 设备带病作业：漏油/故障后继续施工。
    if re.search(r"(漏油|带病作业|压力表.*不灵|故障)", t) and re.search(r"(继续碾压|继续施工|继续作业|抓紧完成)", t):
        _push(
            category="logic_warnings",
            severity="high",
            title="设备带病作业风险",
            quote="漏油/故障/继续作业",
            reason="检测到设备异常后未停机处置，持续施工存在质量与安全风险。",
            suggestion="建议补充：停机检修、污染清理、复检合格与恢复条件。",
        )

    # 48) 雨天临电积水风险未闭环。
    if re.search(r"(雨天|小雨|降雨)", t) and re.search(r"(电缆|配电箱|漏保)", t) and re.search(r"(拖地|积水|未上锁|未试跳)", t):
        _push(
            category="missing_items",
            severity="high",
            title="雨天临电防护不足",
            quote="雨天/电缆拖地/积水",
            reason="检测到雨天临电设施存在拖地积水等高风险隐患，未体现架空或防水处置。",
            suggestion="建议补充：电缆架空或穿管、防水隔离、停用整改与复查记录。",
        )

    # 49) 复工程序缺失：停工后擅自恢复施工。
    if re.search(r"(停工|整改停工)", t) and re.search(r"(擅自复工|自行恢复|恢复开挖|正常施工)", t):
        if not re.search(r"(复工报审|复工批准|复工签认|复查合格|书面批准)", t):
            _push(
                category="logic_warnings",
                severity="high",
                title="复工程序缺失",
                quote="停工/擅自复工",
                reason="检测到停工后未履行复工报审与批准流程即恢复施工。",
                suggestion="建议补充：复工报审、复查签认、书面批准及抄送记录。",
            )

    # 50) 整改未完成仍放行。
    if re.search(r"(围挡缺口|整改未完成|条件未满足|仍存在)", t) and re.search(r"(正常施工|同意|继续施工|放行)", t):
        _push(
            category="logic_warnings",
            severity="high",
            title="整改未完成仍放行",
            quote="整改未完成/继续施工",
            reason="检测到整改条件未满足即放行，存在程序与安全风险。",
            suggestion="建议补充：继续停工整改、复查结论和复工条件。",
        )

    # 51) 监理结论不合规：应停工却给出正常施工结论。
    if re.search(r"(监理意见|结论)", t) and re.search(r"(正常施工|同意继续|可以投入使用|满足使用要求)", t):
        if re.search(r"(擅自复工|未验收|隐患|缺口|未整改|高风险)", t):
            _push(
                category="logic_warnings",
                severity="high",
                title="监理结论不合规",
                quote="风险未控/同意继续",
                reason="检测到关键风险未消除情况下仍给出放行结论，监理意见与控制要求不一致。",
                suggestion="建议补充：停工整改指令、复查签认与书面放行依据。",
            )

    # 52) 模板化泛化记录：部位/工序过泛且无量化数据。
    if re.search(r"(全线施工段|综合施工|整体正常|继续施工)", t):
        lacks_specific_step = not re.search(r"(浇筑|摊铺|开挖|张拉|吊装|压实|安装|绑扎|试压|验收|检测)", t)
        lacks_numeric_data = not re.search(r"([0-9]+(\.[0-9]+)?\s*(m³|m2|m|mm|cm|℃|吨|MPa|%|组|根|台|遍))", t, re.IGNORECASE)
        if lacks_specific_step or lacks_numeric_data:
            _push(
                category="missing_items",
                severity="low",
                title="模板化记录缺少部位工序与数据",
                quote="全线/综合/整体正常",
                reason="检测到记录使用泛化表述，缺少具体施工工序与量化数据支撑。",
                suggestion="建议补充：具体施工部位、工序动作、实测数据与处理结果。",
            )

    # 53) 停工管理流程缺失：停工原因/审批/巡查/复工条件缺项。
    if re.search(r"(停工|未组织施工|正常停工)", t):
        lacks_flow = not re.search(r"(停复工审批|复工报审|巡查记录|安全巡查|复工条件|书面批准)", t)
        if lacks_flow:
            _push(
                category="logic_warnings",
                severity="medium",
                title="停工管理流程缺失",
                quote="停工/审批/巡查",
                reason="检测到停工场景但未体现停复工审批、巡查记录或复工条件。",
                suggestion="建议补充：停工原因依据、审批记录、安全巡查与复工条件。",
            )

    # 52) 铺装质量缺陷未闭环（高低差/边缘不顺直后续再调）。
    if re.search(r"(铺设|铺装|人行道|透水砖)", t) and re.search(r"(高低差|不顺直|后期再调|后续再调)", t):
        _push(
            category="closure_issues",
            severity="medium",
            title="铺装质量缺陷未闭环",
            quote="高低差/后期再调",
            reason="检测到铺装质量缺陷未当场整改，拟后续处理，闭环不足。",
            suggestion="建议补充：当场返工调整、复测数据和复查结论。",
        )

    # 53) 绿化工序与养护控制不足。
    if re.search(r"(乔木|草皮|绿化)", t) and re.search(r"(未浇透|定根水|未滚压|接缝较大|未见排水层|后续统一养护)", t):
        _push(
            category="missing_items",
            severity="medium",
            title="绿化工序与养护控制不足",
            quote="定根水/滚压/排水层",
            reason="检测到绿化关键工序或养护措施缺失，成活质量风险较高。",
            suggestion="建议补充：定根水、滚压补缝、排水层和养护计划执行记录。",
        )

    # 54) 喷锚施工条件与锚固控制不足。
    if re.search(r"(喷锚|锚杆|喷浆)", t) and re.search(r"(潮湿|未拧紧|外露长度不一致|未记录长度|未记录间距)", t):
        _push(
            category="missing_items",
            severity="high",
            title="喷锚施工条件与锚固控制不足",
            quote="潮湿基层/锚固未紧",
            reason="检测到喷锚作业条件或锚固质量控制不足，存在结构风险。",
            suggestion="建议补充：施工条件确认、扭矩复查、实测参数与试验记录。",
        )

    # 55) 防水基层条件记录缺失。
    if re.search(r"(防水|涂膜|喷涂)", t) and re.search(r"(基层|含水率|清理记录)", t):
        if re.search(r"(未记录|缺失|未见|未写)", t):
            _push(
                category="missing_items",
                severity="medium",
                title="防水基层条件记录缺失",
                quote="基层/含水率/清理记录",
                reason="检测到防水施工前基层条件记录缺失，质量可追溯性不足。",
                suggestion="建议补充：基层清理、含水率、温度与复核记录。",
            )

    # 56) 给水投用放行不当（未检先用）。
    if re.search(r"(给水|水质检测)", t) and re.search(r"(未提供|无|未见).{0,10}(水质检测|检测报告)", t):
        if re.search(r"(可以投入使用|接通用户管网|允许投入使用)", t):
            _push(
                category="logic_warnings",
                severity="high",
                title="给水投用放行不当",
                quote="未检先用/投入使用",
                reason="检测到水质检测缺失情况下仍放行投用，公共安全风险较高。",
                suggestion="建议补充：暂停投用、补齐检测报告并复验合格后放行。",
            )

    # 57) 积水处置记录不足（恶劣天气下）。
    if re.search(r"(积水|局部积水|明显积水)", t):
        if not re.search(r"(排水|抽排|清理|处置完成|复查)", t):
            _push(
                category="logic_warnings",
                severity="medium",
                title="积水处置不足",
                quote="积水/未处置记录",
                reason="检测到现场存在积水，但未体现有效处置或复查结论。",
                suggestion="建议补充：排水措施、完成时点和复查结果。",
            )

    # 58) 张拉关键数据缺失。
    if re.search(r"(张拉|初张拉|预应力)", t):
        if not re.search(r"(张拉力|伸长量|回缩量|持荷|记录表|实测)", t):
            _push(
                category="missing_items",
                severity="medium",
                title="张拉关键数据缺失",
                quote="张拉/数据缺失",
                reason="检测到张拉作业但缺少关键过程数据，质量判定依据不足。",
                suggestion="建议补充：张拉力、伸长量、回缩量、持荷及记录表。",
            )
        if re.search(r"(记录不完整|数据缺失|仅填写)", t) and not re.search(r"(第三方检测|复测|复核)", t):
            _push(
                category="missing_items",
                severity="medium",
                title="张拉复测与第三方检测缺失",
                quote="张拉记录不完整",
                reason="检测到张拉记录不完整，未体现复测或第三方检测。",
                suggestion="建议补充：复测记录、第三方检测或见证资料。",
            )

    # 59) 量化数据依据不足（如面积约、深度约但无复核）。
    if re.search(r"(面积约|深度约|方量约|约[0-9]+)", t) and not re.search(r"(复核|复测|测量依据|检测数据|点位)", t):
        _push(
            category="missing_items",
            severity="low",
            title="量化数据依据不足",
            quote="约数值/缺复核",
            reason="检测到量化数据仅为约值，未体现测量复核或检测依据。",
            suggestion="建议补充：测量方法、复核点位、实测数据与判定标准。",
        )

    # 60) 交通导改措施记录不足（存在标志问题但缺整改闭环）。
    if re.search(r"(交通疏导|导改|警示标志)", t) and re.search(r"(不合理|不到位|缺失)", t):
        if not re.search(r"(整改完成|复查|调整后|闭环)", t):
            _push(
                category="closure_issues",
                severity="medium",
                title="交通导改措施记录不完整",
                quote="导改/警示标志问题",
                reason="检测到导改或警示标志问题，但未体现整改复查闭环。",
                suggestion="建议补充：整改措施、复查结论与留证信息。",
            )

    # 61) 支座施工工艺描述异常。
    if re.search(r"(支座更换|支座施工)", t) and re.search(r"(重新浇筑.*支座|混凝土支座)", t):
        _push(
            category="logic_warnings",
            severity="medium",
            title="支座施工工艺描述异常",
            quote="支座/浇筑描述",
            reason="检测到支座施工描述与常规工艺表达存在偏差，需进一步核验。",
            suggestion="建议补充：工艺步骤、设计依据与关键质量控制记录。",
        )

    # 62) 钢筋问题未整改仍放行。
    if re.search(r"(钢筋).{0,14}(偏大|偏差|问题)", t) and re.search(r"(未再调整|不影响使用)", t):
        _push(
            category="logic_warnings",
            severity="high",
            title="钢筋问题未整改",
            quote="钢筋偏差/未调整",
            reason="检测到钢筋偏差后未整改即放行，存在质量风险。",
            suggestion="建议补充：整改措施、复测结果和放行签认依据。",
        )

    # 63) 混凝土作业缺少养护方案说明。
    if re.search(r"(混凝土|浇筑|初凝)", t) and not re.search(r"(养护|洒水|覆盖|保湿|封闭养护)", t):
        _push(
            category="missing_items",
            severity="medium",
            title="养护方案缺失",
            quote="混凝土作业/无养护说明",
            reason="检测到混凝土施工记录未体现养护方式和计划。",
            suggestion="建议补充：养护措施、起止时间、责任人和巡查频次。",
        )

    # 64) 安全技术交底缺失（脚手架/高处等场景）。
    if re.search(r"(脚手架|高处作业|搭设)", t) and not re.search(r"(安全技术交底|交底记录|交底签字)", t):
        _push(
            category="missing_items",
            severity="medium",
            title="安全技术交底缺失",
            quote="脚手架/高处/交底",
            reason="检测到高风险作业场景，未体现安全技术交底记录。",
            suggestion="建议补充：交底内容、交底对象、签字和时间记录。",
        )

    return findings


def _normalize_conditional_rules(df_cond):
    """
    仅做轻量清洗，不在运行时改写业务规则内容。
    规则语义以 Excel(conditional_required) 为准。
    """
    if df_cond is None:
        return None

    df = df_cond.copy()
    for col in ("doc_type", "trigger_any", "required_any", "severity", "hint", "rule_code"):
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    if "rule_code" in df.columns:
        df["rule_code"] = df["rule_code"].str.lower()

    return df




class SemanticReviewProvider(Protocol):
    def review(self, doc_type: str, text: str, rule_report: dict[str, Any]) -> dict[str, Any]:
        ...


def _env_flag(name: str, default: bool = False) -> bool:
    raw = str(os.getenv(name, "")).strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


def _sanitize_ai_findings(raw_findings: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_findings, list):
        return []
    out: list[dict[str, Any]] = []
    for item in raw_findings:
        if not isinstance(item, dict):
            continue
        out.append(
            {
                "category": str(item.get("category", "semantic_ai")).strip() or "semantic_ai",
                "severity": _normalize_severity(str(item.get("severity", "medium")), default="medium"),
                "title": str(item.get("title", "AI????")).strip() or "AI????",
                "quote": str(item.get("quote", "")).strip(),
                "reason": str(item.get("reason", "")).strip(),
                "suggestion": str(item.get("suggestion", "")).strip(),
            }
        )
    return out


def _invoke_semantic_review(
    doc_type: str,
    text: str,
    rule_report: dict[str, Any],
    semantic_review_provider: SemanticReviewProvider | Callable[[str, str, dict[str, Any]], Any] | None,
    ai_enabled: bool | None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    enabled = _env_flag("AI_REVIEW_ENABLED", False) if ai_enabled is None else bool(ai_enabled)
    timeout_ms_raw = str(os.getenv("AI_REVIEW_TIMEOUT_MS", "6000")).strip()
    try:
        timeout_ms = int(timeout_ms_raw)
    except ValueError:
        timeout_ms = 6000

    base_meta = {
        "enabled": enabled,
        "source": "none",
        "status": "disabled",
        "timeout_ms": timeout_ms,
        "error": "",
    }
    if not enabled:
        return [], base_meta

    if semantic_review_provider is None:
        base_meta.update({"status": "skipped", "error": "provider_missing"})
        return [], base_meta

    try:
        if callable(semantic_review_provider):
            raw = semantic_review_provider(doc_type, text, rule_report)
            source = getattr(semantic_review_provider, "__name__", "callable_provider")
        else:
            raw = semantic_review_provider.review(doc_type, text, rule_report)
            source = semantic_review_provider.__class__.__name__

        ai_findings: list[dict[str, Any]]
        meta_extra: dict[str, Any] = {}
        if isinstance(raw, dict):
            ai_findings = _sanitize_ai_findings(raw.get("findings", []))
            raw_meta = raw.get("meta", {})
            if isinstance(raw_meta, dict):
                meta_extra = raw_meta
        else:
            ai_findings = _sanitize_ai_findings(raw)

        base_meta.update({"source": source, "status": "ok"})
        base_meta.update({k: v for k, v in meta_extra.items() if k != "enabled"})
        return ai_findings, base_meta
    except Exception as e:
        base_meta.update(
            {
                "status": "fallback",
                "error": f"{type(e).__name__}: {e}",
            }
        )
        return [], base_meta


def run_checks(
    doc_type: str,
    text: str,
    rules: dict[str, Any],
    semantic_review_provider: SemanticReviewProvider | Callable[[str, str, dict[str, Any]], Any] | None = None,
    ai_enabled: bool | None = None,
) -> dict[str, Any]:
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
    findings += check_semantic_negative_patterns(doc_type, text)

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

    ai_findings, ai_meta = _invoke_semantic_review(
        doc_type=doc_type,
        text=text,
        rule_report=out,
        semantic_review_provider=semantic_review_provider,
        ai_enabled=ai_enabled,
    )
    # AI??????????????? summary/findings ???
    out["ai_findings"] = ai_findings
    out["ai_meta"] = ai_meta
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
