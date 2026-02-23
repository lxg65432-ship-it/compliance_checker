from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from checker import run_checks  # noqa: E402
from rules_loader import load_rules  # noqa: E402


EXPECTED_MARKERS = ("【预期问题】", "预期问题")

# 预期问题标签词典（按 001~010 的语义场景优先）
EXPECTED_TAG_RULES: dict[str, list[str]] = {
    "weather_risk": ["大雨", "暴雨", "雨天", "恶劣天气", "天气冲突"],
    "water_logging": ["积水", "渗水", "渗漏", "积水未处理到位", "积水未处理"],
    "height_protection": ["高空", "高处", "临边", "防护", "安全带", "防护棚", "警示标志"],
    "special_plan": ["专项方案", "审批", "方案文本", "未验收即使用", "特种设备", "安全技术交底缺失", "技术交底"],
    "tension_data": ["张拉", "伸长量", "回缩量", "张拉数据", "无复测记录", "无第三方检测"],
    "concrete_param": ["强度等级", "浇筑方量", "坍落度", "试块", "试件", "编号"],
    "closure_gap": ["闭环", "复查", "复检", "仅口头", "口头整改", "未形成闭环"],
    "supervision_subject": ["施工人员填写", "施工员填写", "职责界限", "监理职责"],
    "witness_supervision": ["旁站", "旁站情况"],
    "hidden_acceptance": ["隐蔽验收"],
    "measurement_recheck": ["测量复核", "复核记录"],
    "curing_plan": ["养护方案", "养护措施"],
    "stop_resume": ["停工", "复工", "审批记录", "巡查记录"],
    "template_text": ["模板化", "套话", "内容空泛", "无数据支撑", "无工序说明", "无具体部位", "无任何数据支撑"],
    "logic_conflict": ["结论与事实矛盾", "仍认定合格", "仍继续施工"],
    "detection_basis": ["检测依据", "检测数据", "抽检", "试验", "监测数据", "压实度", "厚度", "含水量", "测温", "压降"],
    "acceptance_procedure": ["验收程序", "验收记录", "验收表", "报验", "签字", "签认", "隐检", "隐蔽验收"],
    "stop_work_control": ["停工", "暂停", "未停工", "继续施工", "先整改后施工", "放行", "仍放行", "风险未升级处置"],
    "fire_work_safety": ["动火", "灭火器", "防火毯", "消防器材", "隔离措施"],
    "traffic_diversion": ["交通导改", "围挡", "警示灯", "反光标识", "通道占用", "临时通行", "验收与照片留证", "联合验收", "警戒", "指挥不规范"],
    "material_traceability": ["合格证", "复试报告", "台账", "批次", "进场时间", "标识不清", "追溯"],
    "measurement_recheck_ext": ["复测", "复核", "实测", "点位", "偏差", "标高", "沉降观测", "面积数据无依据", "数量异常"],
    "night_construction": ["夜间施工", "照明不足", "夜间浇筑", "旁站计划"],
    "finite_space": ["有限空间", "井内作业", "气体检测", "通风设备", "应急预案"],
    "equipment_calibration": ["校验", "压力表", "千斤顶", "量具", "有效期"],
    "process_quality_control": ["分层", "夯实", "碾压", "回填", "剪刀撑", "垫板", "离析", "返工", "复压", "施工工艺描述错误", "钢筋问题未整改"],
    "document_evidence": ["照片留证", "影像资料", "记录编号", "留痕"],
    "structure_stability": ["构造措施不符合", "失稳风险", "垫板", "剪刀撑", "连墙件", "支架构造"],
    "supporting_docs_missing": ["资料缺失", "计算书", "预压方案", "沉降观测", "布点", "核验结论"],
    "material_disposal_nonconform": ["不合格材料处置不当", "先用掉", "隔离标识", "退场", "跟踪处理"],
    "yard_protection_gap": ["堆场防护不足", "防雨棚", "防潮", "整改时限", "责任人"],
    "night_release_risk": ["夜间防护不足仍放行", "照明", "警示不足", "先整改后通行", "复查确认"],
    "acceptance_evidence_gap": ["缺少验收与照片留证", "联合验收", "交警", "业主确认", "影像资料编号"],
    "risk_escalation_gap": ["风险未升级处置", "组织排查", "加固", "停工措施", "不能仅", "注意排水", "未组织专项会商", "无加固方案"],
    "water_quality_test": ["缺水质检测", "水质检测", "投用前检测", "接通用户管网"],
    "resume_compliance": ["复工程序缺失", "整改未完成", "监理结论不合规", "擅自复工", "复工报审"],
    "special_equipment_acceptance": ["未验收即使用", "特种设备", "塔吊加节", "第三方检测", "无第三方检测"],
    "weld_inspection_gap": ["检验项目缺失", "探伤", "外观尺寸检查", "焊接质量"],
    "grouting_traceability": ["注浆质量不可追溯", "浆液配比", "回浆", "只写注满", "压浆关键数据缺失"],
    "construction_condition_gap": ["施工条件不满足", "潮湿基层", "空鼓", "烘干措施"],
    "supervision_guidance_gap": ["监理意见导向错误", "风险控制优先", "加快进度不当", "抓紧完成", "监理放行不当", "赶工风险未控制"],
    "strength_before_stripping": ["未达强度拆模", "同条件试块强度报告", "拆模依据"],
    "control_point_gap": ["工序控制点遗漏", "分级加载", "张拉顺序", "控制点", "过程控制缺失"],
    "elevation_adjustment_gap": ["标高偏差处理不当", "后期再抬", "复测确认"],
    "dispute_procedure": ["未按程序处理异议", "影响不大", "技术核定", "设计确认", "变更流程"],
    "equipment_risk": ["设备带病作业", "漏油", "故障继续", "停机检修"],
    "temporary_power_rain_risk": ["雨天电缆拖地积水", "电缆拖地", "积水触电", "临电防护"],
    "rectification_release_risk": ["整改未完成", "复工程序缺失", "擅自复工", "监理结论不合规"],
    "paving_quality_closure": ["质量缺陷未整改", "高低差", "后期再调", "返工调整"],
    "greening_process_control": ["工艺缺陷", "定根水", "排水层", "未滚压", "接缝较大", "养护计划缺失", "工序不到位", "数量无依据", "株号", "苗木规格"],
    "anchor_spray_control": ["施工条件不满足", "潮湿基层", "锚固质量未控制", "螺母未紧固", "锚杆长度"],
    "waterproof_base_record": ["基层条件记录缺失", "基层清理记录", "含水率未记录"],
}

# finding 标签词典（由 checker 输出语义到统一标签）
FINDING_TAG_RULES: dict[str, list[str]] = {
    "weather_risk": ["恶劣天气施工风险", "大雨", "暴雨", "雨天"],
    "water_logging": ["积水", "渗水", "渗漏"],
    "height_protection": ["高处作业", "高空", "临边", "防护", "安全带", "警戒"],
    "special_plan": ["专项方案", "审批"],
    "tension_data": ["张拉", "伸长量", "回缩量", "张拉力"],
    "concrete_param": ["强度等级", "方量", "坍落度", "试块", "试件", "编号"],
    "closure_gap": ["问题闭环不完整", "闭环", "复查", "整改", "口头整改未形成闭环"],
    "supervision_subject": ["监理记录主体疑似不规范", "记录主体", "施工员"],
    "witness_supervision": ["旁站", "全过程监督", "见证"],
    "hidden_acceptance": ["隐蔽", "签认", "验收"],
    "measurement_recheck": ["复测", "复核", "测量"],
    "curing_plan": ["养护"],
    "stop_resume": ["停工", "复工", "巡查"],
    "template_text": ["记录内容偏模板化", "模板化", "套话"],
    "logic_conflict": ["结论与问题描述可能不一致", "逻辑矛盾", "仍认定合格"],
    "detection_basis": ["检测", "抽检", "试验", "压实度", "厚度", "含水量", "温度", "监测", "数据"],
    "acceptance_procedure": ["验收", "报验", "签认", "签字", "隐蔽", "隐检", "复核"],
    "stop_work_control": ["停工", "暂停", "继续施工", "放行", "复工"],
    "fire_work_safety": ["动火", "灭火器", "防火", "消防器材", "隔离"],
    "traffic_diversion": ["导改", "围挡", "警示", "反光", "通道", "临时通行"],
    "material_traceability": ["合格证", "复试", "台账", "批次", "标识", "追溯"],
    "measurement_recheck_ext": ["实测", "复测", "复核", "偏差", "标高", "沉降"],
    "night_construction": ["夜间", "照明", "旁站"],
    "finite_space": ["井内", "气体检测", "通风", "应急预案", "有限空间"],
    "equipment_calibration": ["校验", "压力表", "千斤顶", "量具", "有效期"],
    "process_quality_control": ["分层", "夯实", "碾压", "回填", "剪刀撑", "垫板", "离析", "返工", "复压"],
    "document_evidence": ["影像资料", "留证", "留痕", "记录编号", "编号"],
    "closure_gap": ["缺陷处置闭环不足", "漏浆处置与复查不足", "缺陷处置记录不明确"],
    "curing_plan": ["养护措施记录不完整", "封闭养护", "覆盖洒水", "保湿养护"],
    "acceptance_procedure": ["支架资料核验缺失", "验收签认信息缺失", "验收表", "签认"],
    "measurement_recheck_ext": ["关键部位量化数据不足", "实测量化", "偏差范围", "点位"],
    "stop_work_control": ["高处隐患停工闭环不足", "风险处置升级不足", "停复工"],
    "material_traceability": ["不合格材料处置不当", "受潮结块", "隔离标识", "退场处理"],
    "traffic_diversion": ["导改通道占用放行不当", "通道占用", "绕行引导"],
    "process_quality_control": ["路基风险处置不充分", "弹簧土", "返工复压"],
    "equipment_calibration": ["试压量具校验依据缺失", "校验证明", "有效期"],
}


def _extend_keywords(rule_map: dict[str, list[str]], key: str, keywords: list[str]) -> None:
    current = list(rule_map.get(key, []))
    for kw in keywords:
        if kw and kw not in current:
            current.append(kw)
    rule_map[key] = current


# 统一融合关键词，避免维护时重复 key 覆盖导致标签丢失。
_extend_keywords(FINDING_TAG_RULES, "closure_gap", ["问题闭环不完整", "闭环", "复查", "整改", "缺陷处置闭环不足", "漏浆处置与复查不足", "缺陷处置记录不明确"])
_extend_keywords(FINDING_TAG_RULES, "curing_plan", ["养护", "养护措施记录不完整", "封闭养护", "覆盖洒水", "保湿养护"])
_extend_keywords(FINDING_TAG_RULES, "acceptance_procedure", ["验收", "报验", "签认", "签字", "隐蔽", "隐检", "复核", "支架资料核验缺失", "验收签认信息缺失"])
_extend_keywords(FINDING_TAG_RULES, "measurement_recheck_ext", ["实测", "复测", "复核", "偏差", "标高", "沉降", "关键部位量化数据不足", "点位"])
_extend_keywords(FINDING_TAG_RULES, "stop_work_control", ["停工", "暂停", "继续施工", "放行", "复工", "高处隐患停工闭环不足", "风险处置升级不足"])
_extend_keywords(FINDING_TAG_RULES, "material_traceability", ["合格证", "复试", "台账", "批次", "标识", "追溯", "不合格材料处置不当", "受潮结块", "隔离标识", "退场处理"])
_extend_keywords(FINDING_TAG_RULES, "traffic_diversion", ["导改", "围挡", "警示", "反光", "通道", "临时通行", "导改通道占用放行不当", "绕行引导"])
_extend_keywords(FINDING_TAG_RULES, "process_quality_control", ["分层", "夯实", "碾压", "回填", "剪刀撑", "垫板", "离析", "返工", "复压", "支架验收与构造控制不足", "路基风险处置不充分", "弹簧土"])
_extend_keywords(FINDING_TAG_RULES, "equipment_calibration", ["校验", "压力表", "千斤顶", "量具", "有效期", "试压量具校验依据缺失", "校验证明"])
_extend_keywords(FINDING_TAG_RULES, "tension_data", ["预应力张拉关键数据缺失", "张拉设备校验信息缺失", "张拉顺序", "分级加载"])
_extend_keywords(FINDING_TAG_RULES, "special_plan", ["特种设备未验收即使用", "第三方检测"])
_extend_keywords(FINDING_TAG_RULES, "night_construction", ["大风吊装管控不足", "吊装警戒指挥措施不足"])
_extend_keywords(FINDING_TAG_RULES, "yard_protection_gap", ["砌筑施工条件与质量控制不足"])
_extend_keywords(FINDING_TAG_RULES, "water_quality_test", ["给水投用前检测流程缺失", "水质检测"])
_extend_keywords(FINDING_TAG_RULES, "process_quality_control", ["注压浆关键参数记录不足", "设备异常处置不充分"])
_extend_keywords(FINDING_TAG_RULES, "stop_work_control", ["停复工程序执行不足"])
_extend_keywords(FINDING_TAG_RULES, "resume_compliance", ["停复工程序执行不足", "擅自复工", "复工报审", "复工批准", "监理结论不合规"])
_extend_keywords(FINDING_TAG_RULES, "fire_work_safety", ["临电安全隐患处置不足"])
_extend_keywords(FINDING_TAG_RULES, "supervision_guidance_gap", ["监理意见导向不当"])
_extend_keywords(FINDING_TAG_RULES, "acceptance_procedure", ["验收程序不完整", "特种设备未验收即使用"])
_extend_keywords(FINDING_TAG_RULES, "strength_before_stripping", ["未达强度拆模风险"])
_extend_keywords(FINDING_TAG_RULES, "material_traceability", ["特种设备资料追溯缺失", "给水消毒过程记录缺失", "注浆质量记录不可追溯"])
_extend_keywords(FINDING_TAG_RULES, "elevation_adjustment_gap", ["标高偏差处置不当"])
_extend_keywords(FINDING_TAG_RULES, "weld_inspection_gap", ["焊接检验项目缺失"])
_extend_keywords(FINDING_TAG_RULES, "grouting_traceability", ["注压浆关键参数记录不足", "注浆质量记录不可追溯"])
_extend_keywords(FINDING_TAG_RULES, "dispute_procedure", ["异议处理程序缺失", "影响不大/直接放行", "技术核定", "设计确认"])
_extend_keywords(FINDING_TAG_RULES, "equipment_risk", ["设备带病作业风险", "设备异常处置不充分", "漏油/故障/继续作业"])
_extend_keywords(FINDING_TAG_RULES, "temporary_power_rain_risk", ["雨天临电防护不足", "临电安全隐患处置不足", "电缆拖地/积水"])
_extend_keywords(FINDING_TAG_RULES, "rectification_release_risk", ["复工程序缺失", "整改未完成仍放行", "监理结论不合规", "停复工程序执行不足"])
_extend_keywords(FINDING_TAG_RULES, "paving_quality_closure", ["铺装质量缺陷未闭环", "高低差/后期再调"])
_extend_keywords(FINDING_TAG_RULES, "greening_process_control", ["绿化工序与养护控制不足", "定根水/滚压/排水层"])
_extend_keywords(FINDING_TAG_RULES, "anchor_spray_control", ["喷锚施工条件与锚固控制不足", "潮湿基层/锚固未紧"])
_extend_keywords(FINDING_TAG_RULES, "waterproof_base_record", ["防水基层条件记录缺失", "基层/含水率/清理记录"])
_extend_keywords(FINDING_TAG_RULES, "equipment_calibration", ["设备异常处置不充分"])
_extend_keywords(FINDING_TAG_RULES, "weather_risk", ["大风吊装管控不足"])
_extend_keywords(FINDING_TAG_RULES, "traffic_diversion", ["吊装警戒指挥措施不足"])
_extend_keywords(FINDING_TAG_RULES, "special_plan", ["特种设备未验收即使用"])
_extend_keywords(FINDING_TAG_RULES, "supervision_guidance_gap", ["给水投用放行不当"])
_extend_keywords(FINDING_TAG_RULES, "risk_escalation_gap", ["大风吊装管控不足"])
_extend_keywords(FINDING_TAG_RULES, "control_point_gap", ["未达强度拆模风险"])
_extend_keywords(FINDING_TAG_RULES, "greening_process_control", ["绿化工序与养护控制不足", "株号/规格/定根水"])
_extend_keywords(FINDING_TAG_RULES, "template_text", ["模板化记录缺少部位工序与数据", "全线/综合/整体正常"])
_extend_keywords(FINDING_TAG_RULES, "stop_resume", ["停工管理流程缺失", "停工/审批/巡查"])
_extend_keywords(FINDING_TAG_RULES, "stop_work_control", ["停工管理流程缺失"])
_extend_keywords(FINDING_TAG_RULES, "water_logging", ["积水处置不足", "积水/未处置记录"])
_extend_keywords(FINDING_TAG_RULES, "tension_data", ["张拉关键数据缺失", "张拉复测与第三方检测缺失"])
_extend_keywords(FINDING_TAG_RULES, "measurement_recheck_ext", ["量化数据依据不足", "约数值/缺复核"])
_extend_keywords(FINDING_TAG_RULES, "traffic_diversion", ["交通导改措施记录不完整", "导改/警示标志问题"])
_extend_keywords(FINDING_TAG_RULES, "process_quality_control", ["支座施工工艺描述异常", "钢筋问题未整改"])
_extend_keywords(FINDING_TAG_RULES, "curing_plan", ["养护方案缺失", "混凝土作业/无养护说明"])
_extend_keywords(FINDING_TAG_RULES, "risk_escalation_gap", ["风险处置升级不足"])
_extend_keywords(FINDING_TAG_RULES, "special_plan", ["安全技术交底缺失"])


def _norm(s: str) -> str:
    s = str(s or "").strip().lower()
    s = re.sub(r"\s+", "", s)
    return s


def _token_similarity(a: str, b: str) -> float:
    def _tokens(x: str) -> set[str]:
        t = _norm(x)
        return {w for w in re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]{2,}", t) if len(w) >= 2}

    ta, tb = _tokens(a), _tokens(b)
    if not ta and not tb:
        return 0.0
    return len(ta & tb) / max(1, len(ta | tb))


def _tags_for_text(text: str, rules: dict[str, list[str]]) -> set[str]:
    t = _norm(text)
    out: set[str] = set()
    for tag, kws in rules.items():
        if any(_norm(k) in t for k in kws if k):
            out.add(tag)
    return out


def _parse_cases_md(md_path: Path) -> dict[str, dict[str, Any]]:
    text = md_path.read_text(encoding="utf-8")
    parts = re.split(r"(?m)^#{2,3}\s*case_(\d{3})\s*$", text)
    parsed: dict[str, dict[str, Any]] = {}

    for i in range(1, len(parts), 2):
        case_code = f"case_{parts[i]}"
        block = parts[i + 1].strip()
        lines = [ln.rstrip() for ln in block.splitlines() if ln.strip()]
        marker_idx = next((j for j, ln in enumerate(lines) if any(m in ln for m in EXPECTED_MARKERS)), None)

        if marker_idx is None:
            content_lines = lines
            expected_items: list[str] = []
        else:
            content_lines = lines[:marker_idx]
            expected_items = []
            for ln in lines[marker_idx + 1 :]:
                m = re.match(r"^\s*\d+[^0-9A-Za-z\u4e00-\u9fff]\s*(.+)$", ln)
                if m:
                    expected_items.append(m.group(1).strip())

        parsed[case_code] = {
            "text": "\n".join(content_lines),
            "expected_issue_points": expected_items,
        }
    return parsed


def _build_expected_compare(expected_items: list[str], findings: list[dict[str, Any]]) -> dict[str, Any]:
    finding_profiles: list[dict[str, Any]] = []
    for f in findings:
        merged = " | ".join(
            [
                str(f.get("title", "")),
                str(f.get("reason", "")),
                str(f.get("suggestion", "")),
                str(f.get("quote", "")),
            ]
        )
        finding_profiles.append(
            {
                "title": str(f.get("title", "")),
                "category": str(f.get("category", "")),
                "text": merged,
                "tags": _tags_for_text(merged, FINDING_TAG_RULES),
            }
        )

    items: list[dict[str, Any]] = []
    matched_count = 0

    for exp in expected_items:
        exp_tags = _tags_for_text(exp, EXPECTED_TAG_RULES)
        best: dict[str, Any] | None = None
        best_score = 0.0
        best_tag_overlap = 0

        for fp in finding_profiles:
            overlap = len(exp_tags & fp["tags"]) if exp_tags else 0
            score = _token_similarity(exp, fp["text"])
            # 标签优先，词相似度次之
            rank = overlap * 10 + score
            if best is None or rank > (best_tag_overlap * 10 + best_score):
                best = fp
                best_score = score
                best_tag_overlap = overlap

        matched = False
        if best is not None:
            if exp_tags:
                matched = best_tag_overlap > 0
                # 标签未覆盖时，允许高相似度兜底，减少“有 finding 但标签词典漏写”的误判。
                if not matched and best_score >= 0.28:
                    matched = True
            else:
                matched = best_score >= 0.18

        if matched:
            matched_count += 1

        items.append(
            {
                "expected": exp,
                "expected_tags": sorted(list(exp_tags)),
                "matched": matched,
                "score": round(float(best_score), 4),
                "matched_tags_overlap": best_tag_overlap,
                "matched_finding": (
                    {"title": best["title"], "category": best["category"]} if best is not None else None
                ),
                "evidence": (best["text"][:240] if best is not None else ""),
                "gap_reason": "" if matched else "No aligned tag/finding for this expected issue.",
            }
        )

    return {
        "expected_total": len(expected_items),
        "matched_expected": matched_count,
        "unmatched_expected": len(expected_items) - matched_count,
        "actual_total": len(findings),
        "items": items,
    }


def _render_md(rows: list[dict[str, Any]]) -> str:
    lines = ["# case_001~case_010 Detailed Gap Report (tag-aligned)", ""]
    for r in rows:
        s = r["summary"]
        lines.append(f"## {r['case_code']} | {r['id']}")
        lines.append(
            f"- expected={s['expected_total']}, matched={s['matched_expected']}, "
            f"unmatched={s['unmatched_expected']}, actual={s['actual_total']}"
        )
        for it in r["items"]:
            flag = "MATCH" if it["matched"] else "MISS"
            title = it["matched_finding"]["title"] if it["matched_finding"] else "-"
            tags = ",".join(it.get("expected_tags", []))
            lines.append(
                f"- [{flag}] {it['expected']} | tags={tags or '-'} | "
                f"overlap={it.get('matched_tags_overlap', 0)} | finding={title}"
            )
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Rebuild expected compare by semantic tags.")
    parser.add_argument("--rules", default="rules_v1.xlsx")
    parser.add_argument("--md", default="batch_case_001_010.md")
    parser.add_argument("--pack", default="test_samples/cases.review_pack.json")
    parser.add_argument("--output-json", default="test_samples/batch_compare_001_010.retest.detailed.json")
    parser.add_argument("--output-md", default="test_samples/batch_compare_001_010.retest.detailed.md")
    parser.add_argument("--doc-type", default="日志")
    args = parser.parse_args()

    rules_path = (REPO_ROOT / args.rules).resolve() if not Path(args.rules).is_absolute() else Path(args.rules)
    md_path = (REPO_ROOT / args.md).resolve() if not Path(args.md).is_absolute() else Path(args.md)
    pack_path = (REPO_ROOT / args.pack).resolve() if not Path(args.pack).is_absolute() else Path(args.pack)
    out_json = (REPO_ROOT / args.output_json).resolve() if not Path(args.output_json).is_absolute() else Path(args.output_json)
    out_md = (REPO_ROOT / args.output_md).resolve() if not Path(args.output_md).is_absolute() else Path(args.output_md)

    rules = load_rules(rules_path)
    parsed = _parse_cases_md(md_path)

    payload = json.loads(pack_path.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    for case in payload.get("cases", []):
        code = str(case.get("case_code", ""))
        if code not in parsed:
            continue

        src = parsed[code]
        text_body = str(src["text"])
        expected_items = list(src["expected_issue_points"])

        report = run_checks(args.doc_type, text_body, rules)
        findings = report.get("findings", [])
        expected_compare = _build_expected_compare(expected_items, findings)

        case["doc_type"] = args.doc_type
        case["text"] = text_body
        case["text_excerpt"] = re.sub(r"\s+", " ", text_body)[:200]
        case["expected_issue_points"] = expected_items
        case["observed"] = {
            "summary": report.get("summary", {}),
            "categories": sorted(list({str(f.get("category", "")) for f in findings if f.get("category")})),
            "top_titles": [str(f.get("title", "")) for f in findings[:8]],
        }
        case["expected_compare"] = expected_compare
        case["decision"] = "pass" if expected_compare["unmatched_expected"] == 0 else "fail"
        case["review_notes"] = (
            f"Batch compare (tag-aligned): expected={expected_compare['expected_total']}, "
            f"matched={expected_compare['matched_expected']}, "
            f"unmatched={expected_compare['unmatched_expected']}."
        )

        rows.append(
            {
                "id": case.get("id", ""),
                "case_code": code,
                "summary": {
                    "expected_total": expected_compare["expected_total"],
                    "matched_expected": expected_compare["matched_expected"],
                    "unmatched_expected": expected_compare["unmatched_expected"],
                    "actual_total": expected_compare["actual_total"],
                },
                "items": expected_compare["items"],
                "actual_unmapped_titles": [str(f.get("title", "")) for f in findings],
                "decision": case["decision"],
            }
        )

    rows.sort(key=lambda x: x["case_code"])
    pack_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    out_json.write_text(json.dumps({"meta": {"count": len(rows)}, "results": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    out_md.write_text(_render_md(rows), encoding="utf-8")

    expected_total = sum(r["summary"]["expected_total"] for r in rows)
    matched_total = sum(r["summary"]["matched_expected"] for r in rows)
    unmatched_total = sum(r["summary"]["unmatched_expected"] for r in rows)
    actual_total = sum(r["summary"]["actual_total"] for r in rows)
    print(f"rows={len(rows)} expected_total={expected_total} matched={matched_total} unmatched={unmatched_total} actual={actual_total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
