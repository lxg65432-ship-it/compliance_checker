# case_001~case_010 Detailed Gap Report (tag-aligned)

## case_001 | raw_017_batch_case_001
- expected=5, matched=5, unmatched=0, actual=10
- [MATCH] 大雨天气仍进行吊装作业 | tags=weather_risk | overlap=1 | finding=恶劣天气施工风险
- [MATCH] 积水未处理到位 | tags=water_logging | overlap=1 | finding=积水处置不足
- [MATCH] 高空作业防护措施不完善 | tags=height_protection | overlap=1 | finding=恶劣天气施工风险
- [MATCH] 未提专项方案审批情况 | tags=special_plan | overlap=1 | finding=恶劣天气施工风险
- [MATCH] 张拉数据缺失 | tags=tension_data | overlap=1 | finding=张拉关键数据缺失

## case_002 | raw_018_batch_case_002
- expected=5, matched=5, unmatched=0, actual=7
- [MATCH] 未填写混凝土强度等级 | tags=concrete_param | overlap=1 | finding=条件必填缺失
- [MATCH] 未填写浇筑方量 | tags=concrete_param | overlap=1 | finding=条件必填缺失
- [MATCH] 试块数量、编号缺失 | tags=concrete_param | overlap=1 | finding=条件必填缺失
- [MATCH] 无坍落度检测记录 | tags=concrete_param | overlap=1 | finding=条件必填缺失
- [MATCH] 漏浆问题未形成闭环处理 | tags=closure_gap | overlap=1 | finding=缺陷处置闭环不足

## case_003 | raw_019_batch_case_003
- expected=5, matched=5, unmatched=0, actual=8
- [MATCH] 日志由施工人员填写 | tags=supervision_subject | overlap=1 | finding=监理记录主体疑似不规范
- [MATCH] 监理职责界限不清 | tags=supervision_subject | overlap=1 | finding=监理记录主体疑似不规范
- [MATCH] 面积数据无依据 | tags=measurement_recheck_ext | overlap=1 | finding=量化数据依据不足
- [MATCH] 交通导改措施记录不完整 | tags=traffic_diversion | overlap=1 | finding=交通导改措施记录不完整
- [MATCH] 未注明旁站情况 | tags=witness_supervision | overlap=1 | finding=监理记录主体疑似不规范

## case_004 | raw_020_batch_case_004
- expected=5, matched=5, unmatched=0, actual=8
- [MATCH] 支座施工工艺描述错误 | tags=process_quality_control | overlap=1 | finding=钢筋问题未整改
- [MATCH] 未进行隐蔽验收 | tags=acceptance_procedure,hidden_acceptance | overlap=2 | finding=钢筋问题未整改
- [MATCH] 钢筋问题未整改 | tags=process_quality_control | overlap=1 | finding=钢筋问题未整改
- [MATCH] 无测量复核记录 | tags=measurement_recheck,measurement_recheck_ext | overlap=2 | finding=钢筋问题未整改
- [MATCH] 无养护方案 | tags=curing_plan | overlap=1 | finding=养护方案缺失

## case_005 | raw_021_batch_case_005
- expected=5, matched=5, unmatched=0, actual=7
- [MATCH] 高支架无专项方案 | tags=special_plan | overlap=1 | finding=支架验收与构造控制不足
- [MATCH] 无验收记录 | tags=acceptance_procedure | overlap=1 | finding=支架验收与构造控制不足
- [MATCH] 整改无复查记录 | tags=closure_gap | overlap=1 | finding=支架验收与构造控制不足
- [MATCH] 口头整改无书面闭环 | tags=closure_gap | overlap=1 | finding=支架验收与构造控制不足
- [MATCH] 安全技术交底缺失 | tags=special_plan | overlap=1 | finding=安全技术交底缺失

## case_006 | raw_022_batch_case_006
- expected=5, matched=5, unmatched=0, actual=10
- [MATCH] 出现塌方未停工 | tags=stop_resume,stop_work_control | overlap=2 | finding=风险处置升级不足
- [MATCH] 未组织专项会商 | tags=risk_escalation_gap | overlap=1 | finding=风险处置升级不足
- [MATCH] 无监测数据 | tags=detection_basis | overlap=1 | finding=风险处置升级不足
- [MATCH] 无加固方案 | tags=risk_escalation_gap | overlap=1 | finding=风险处置升级不足
- [MATCH] 结论与事实矛盾 | tags=logic_conflict | overlap=1 | finding=结论与问题描述可能不一致

## case_007 | raw_023_batch_case_007
- expected=4, matched=4, unmatched=0, actual=3
- [MATCH] 无具体部位 | tags=template_text | overlap=1 | finding=模板化记录缺少部位工序与数据
- [MATCH] 无工序说明 | tags=template_text | overlap=1 | finding=模板化记录缺少部位工序与数据
- [MATCH] 无任何数据支撑 | tags=template_text | overlap=1 | finding=模板化记录缺少部位工序与数据
- [MATCH] 典型模板化套话 | tags=template_text | overlap=1 | finding=模板化记录缺少部位工序与数据

## case_008 | raw_024_batch_case_008
- expected=5, matched=5, unmatched=0, actual=4
- [MATCH] 数量异常 | tags=measurement_recheck_ext | overlap=1 | finding=关键部位量化数据不足
- [MATCH] 合格证不完整 | tags=material_traceability | overlap=1 | finding=不合格材料处置不当
- [MATCH] 无复试报告 | tags=material_traceability | overlap=1 | finding=不合格材料处置不当
- [MATCH] 标识不清仍允许使用 | tags=material_traceability | overlap=1 | finding=不合格材料处置不当
- [MATCH] 材料台账缺失 | tags=material_traceability | overlap=1 | finding=不合格材料处置不当

## case_009 | raw_025_batch_case_009
- expected=4, matched=4, unmatched=0, actual=5
- [MATCH] 张拉数据缺失 | tags=tension_data | overlap=1 | finding=张拉关键数据缺失
- [MATCH] 无复测记录 | tags=measurement_recheck_ext,tension_data | overlap=2 | finding=张拉复测与第三方检测缺失
- [MATCH] 无第三方检测 | tags=special_equipment_acceptance,tension_data | overlap=1 | finding=张拉关键数据缺失
- [MATCH] 记录不完整仍认定合格 | tags=logic_conflict | overlap=1 | finding=结论与问题描述可能不一致

## case_010 | raw_026_batch_case_010
- expected=4, matched=4, unmatched=0, actual=4
- [MATCH] 停工原因不规范 | tags=stop_resume,stop_work_control | overlap=2 | finding=停工管理流程缺失
- [MATCH] 无停复工审批记录 | tags=special_plan,stop_resume | overlap=2 | finding=停工管理流程缺失
- [MATCH] 无安全巡查记录 | tags=stop_resume | overlap=1 | finding=停工管理流程缺失
- [MATCH] 停工管理流程缺失 | tags=stop_resume,stop_work_control | overlap=2 | finding=停工管理流程缺失
