# case_001~case_010 Detailed Gap Report (tag-aligned)

## case_011 | raw_027_batch_case_011
- expected=3, matched=3, unmatched=0, actual=7
- [MATCH] 压实度/厚度无检测依据：仅“约18cm、碾压3遍”不能证明合格，应要求现场抽检压实度、厚度（或芯样/尺量）并记录数据，必要时签发监理通知。 | tags=detection_basis,process_quality_control | overlap=2 | finding=条件必填缺失
- [MATCH] 离析处理无闭环：仅“回补找平”缺复压与复检，应要求铲除离析料、复拌/补料、复压并复检合格后放行。 | tags=closure_gap,process_quality_control,stop_work_control | overlap=2 | finding=缺陷处置闭环不足
- [MATCH] 缺少取样/配合比信息：水稳应记录配合比、取样频次与试验委托编号，监理应补充旁站要点并核验试验资料。 | tags=concrete_param,detection_basis,witness_supervision | overlap=1 | finding=缺陷处置闭环不足

## case_012 | raw_028_batch_case_012
- expected=3, matched=3, unmatched=0, actual=9
- [MATCH] 关键参数缺失：无强度等级/方量/坍落度/试块编号，无法追溯质量，应补录并核验试验委托单，必要时出具旁站记录。 | tags=concrete_param,detection_basis,material_traceability,witness_supervision | overlap=3 | finding=材料追溯资料缺失
- [MATCH] 漏浆处理不规范：砂浆抹补可能掩盖蜂窝麻面风险，应要求拆模后检查实体质量，必要时凿除修补并形成整改复查闭环。 | tags=closure_gap | overlap=1 | finding=漏浆处置与复查不足
- [MATCH] 养护措施不明确：垫层也需覆盖洒水/保湿，日志未写措施与责任人，应补充养护方式和巡查记录。 | tags=curing_plan,stop_resume,yard_protection_gap | overlap=2 | finding=养护措施记录不完整

## case_013 | raw_029_batch_case_013
- expected=3, matched=3, unmatched=0, actual=5
- [MATCH] 雨天摊铺：规范通常要求雨天不宜进行沥青摊铺，日志未说明监理采取停工/暂停/调整工序等措施，应下发监理通知或口头指令书面化并留痕。 | tags=document_evidence,stop_resume,stop_work_control,weather_risk | overlap=1 | finding=养护措施记录不完整
- [MATCH] 温度偏低风险：到场/摊铺温度135℃可能低于工艺控制要求，日志未指出并未要求复测温度或调整运输/拌和，应要求测温记录、必要时退料。 | tags=detection_basis,measurement_recheck_ext | overlap=1 | finding=条件必填缺失
- [MATCH] 无防雨措施记录：既然在雨天施工，应记录施工单位是否采取覆盖、排水、缩短摊铺长度等措施；若无，应责令停铺、返工或铣刨处理并形成闭环。 | tags=closure_gap,process_quality_control,weather_risk | overlap=1 | finding=条件必填缺失

## case_014 | raw_030_batch_case_014
- expected=3, matched=3, unmatched=0, actual=4
- [MATCH] 未验收即放行：支架属危大工程，需专项方案、验收程序与签字，日志仅“整改后可进入”但无停工/验收要求，应签发通知并组织验收。 | tags=acceptance_procedure,special_plan,stop_resume,stop_work_control | overlap=3 | finding=支架验收与构造控制不足
- [MATCH] 构造措施不符合：无垫板/剪刀撑不连续存在失稳风险，应要求按方案补齐并复查记录，必要时第三方复核。 | tags=closure_gap,measurement_recheck_ext,process_quality_control,structure_stability | overlap=2 | finding=支架验收与构造控制不足
- [MATCH] 资料缺失：无计算书、预压方案、沉降观测布点等信息，监理应要求补齐并在日志注明资料核验结论。 | tags=measurement_recheck_ext,supporting_docs_missing | overlap=1 | finding=支架资料核验缺失

## case_015 | raw_031_batch_case_015
- expected=3, matched=3, unmatched=0, actual=5
- [MATCH] 隐蔽验收缺失：管道接口、坡度、基础等应隐蔽验收后回填，日志未体现验收程序，应补办隐检并对已回填段开挖抽查。 | tags=acceptance_procedure,hidden_acceptance,process_quality_control | overlap=2 | finding=验收签认信息缺失
- [MATCH] 回填工艺不合规：含块石/机械直接碾压易损管，应要求筛土分层夯实、井周人工夯实并形成整改复查。 | tags=closure_gap,process_quality_control | overlap=1 | finding=条件必填缺失
- [MATCH] 缺检测数据：应记录压实度检测点位与结果，监理应督促见证取样/检测并在日志留存编号。 | tags=concrete_param,detection_basis,measurement_recheck_ext | overlap=1 | finding=条件必填缺失

## case_016 | raw_032_batch_case_016
- expected=3, matched=3, unmatched=0, actual=5
- [MATCH] 质量问题未闭环：发现垫块缺失/间距偏差但未要求整改完成复查，应下发监理通知并在浇筑前复验签认。 | tags=acceptance_procedure,closure_gap,measurement_recheck_ext | overlap=2 | finding=浇筑前放行控制不足
- [MATCH] 关键部位未量化：未记录抽查位置、实测间距数据与偏差范围，系统应提示补充“点位+数值+结论”。 | tags=measurement_recheck_ext | overlap=1 | finding=关键部位量化数据不足
- [MATCH] 浇筑前控制缺失：应明确“未整改不得浇筑”的控制点，必要时签发停工指令或旁站要求。 | tags=control_point_gap,stop_resume,stop_work_control,witness_supervision | overlap=2 | finding=浇筑前放行控制不足

## case_017 | raw_033_batch_case_017
- expected=3, matched=3, unmatched=0, actual=4
- [MATCH] 养护措施不足：未覆盖洒水易裂缝，应立即要求覆盖保湿、养护不少于规定天数，并记录开始时间与责任人。 | tags=curing_plan,yard_protection_gap | overlap=1 | finding=养护措施记录不完整
- [MATCH] 缺少温控记录：大体积/梁体应有温度监测或至少养护巡查记录，日志未写，监理应补充旁站/巡查数据。 | tags=stop_resume,witness_supervision | overlap=1 | finding=条件必填缺失
- [MATCH] 缺陷处置不明确：已出现干缩迹象应记录处置（封闭养护、修补方案、复查结论），必要时出具质量问题通知单。 | tags=closure_gap | overlap=1 | finding=缺陷处置记录不明确

## case_018 | raw_034_batch_case_018
- expected=3, matched=3, unmatched=0, actual=5
- [MATCH] 重大安全隐患未停工闭环：高处无防护、未系安全带应立即停工整改并形成书面记录（停工/复工手续）。 | tags=closure_gap,height_protection,stop_resume,stop_work_control | overlap=3 | finding=高处隐患停工闭环不足
- [MATCH] 动火管理缺失：焊接应有动火审批、消防器材与隔离措施，日志未体现，应要求补办手续并旁站。 | tags=fire_work_safety,special_plan,witness_supervision | overlap=2 | finding=动火安全措施缺失
- [MATCH] 危险品管理问题：油漆桶靠近动火点风险高，应责令清理、设专人监护并记录整改复查。 | tags=closure_gap,fire_work_safety | overlap=1 | finding=高处隐患停工闭环不足

## case_019 | raw_035_batch_case_019
- expected=3, matched=3, unmatched=0, actual=5
- [MATCH] 不合格材料处置不当：受潮结块材料不应“先用掉”，应隔离标识、复检或退场，监理应签发通知并跟踪处理结果。 | tags=closure_gap,material_disposal_nonconform | overlap=1 | finding=不合格材料处置不当
- [MATCH] 堆场防护不足：应有防雨棚、垫板、防潮措施，日志未记录整改时限与责任人，应补齐闭环。 | tags=closure_gap,height_protection,process_quality_control,structure_stability,yard_protection_gap | overlap=1 | finding=不合格材料处置不当
- [MATCH] 材料追溯缺失：未记录批次、进场时间、台账编号，监理应要求完善材料台账与复试报告关联。 | tags=concrete_param,material_traceability | overlap=1 | finding=不合格材料处置不当

## case_020 | raw_036_batch_case_020
- expected=3, matched=3, unmatched=0, actual=5
- [MATCH] 夜间防护不足仍放行：照明/警示不足属于安全风险，应先整改后通行，监理应下发整改通知并复查确认。 | tags=closure_gap,height_protection,night_release_risk,stop_work_control | overlap=2 | finding=导改通道占用放行不当
- [MATCH] 通道占用未整改：行人通道被占应立即清理，必要时暂停通行并设置临时绕行引导。 | tags=stop_work_control,traffic_diversion | overlap=2 | finding=导改通道占用放行不当
- [MATCH] 缺少验收与照片留证：导改通常需联合验收/交警或业主确认，日志未体现，建议补充验收记录与影像资料编号。 | tags=acceptance_evidence_gap,acceptance_procedure,concrete_param,document_evidence,traffic_diversion | overlap=1 | finding=导改通道占用放行不当

## case_021 | raw_037_batch_case_021
- expected=3, matched=3, unmatched=0, actual=5
- [MATCH] 分层厚度偏大：45cm可能超出规范/试验段控制值，应要求按试验段参数分层并复核松铺系数。 | tags=detection_basis,measurement_recheck_ext,process_quality_control | overlap=2 | finding=路基风险处置不充分
- [MATCH] 含水量未控：无含水量检测易造成弹簧土，应见证取样测含水量并调整洒水/晾晒措施。 | tags=detection_basis | overlap=1 | finding=路基风险处置不充分
- [MATCH] 边坡质量风险：弹簧土应返工处理并复压，日志未形成指令与复查，建议发监理通知单闭环。 | tags=closure_gap,process_quality_control | overlap=2 | finding=路基风险处置不充分

## case_022 | raw_038_batch_case_022
- expected=3, matched=3, unmatched=0, actual=6
- [MATCH] 基坑风险未升级处置：积水+支护裂缝应立即组织排查并采取加固/停工措施，不能仅“注意排水”。 | tags=risk_escalation_gap,stop_resume,stop_work_control,water_logging | overlap=2 | finding=风险处置升级不足
- [MATCH] 缺监测数据：深基坑应记录位移/沉降/水位监测结果，日志未写，应督促监测并纳入日报。 | tags=detection_basis | overlap=1 | finding=风险处置升级不足
- [MATCH] 整改无时限无闭环：应明确整改措施、责任人、完成时限并复查签认，必要时签发停工令。 | tags=acceptance_procedure,closure_gap,stop_resume,stop_work_control,yard_protection_gap | overlap=2 | finding=风险处置升级不足

## case_023 | raw_039_batch_case_023
- expected=3, matched=3, unmatched=0, actual=7
- [MATCH] 缺少基层条件控制：防水施工应控制含水率/温度，日志未记录检测数据，监理应要求测定并留存记录。 | tags=detection_basis | overlap=1 | finding=缺陷处置记录不明确
- [MATCH] 缺陷处置不规范：起泡翘边不应简单压平，应割除修补并复检粘结，必要时返工。 | tags=closure_gap,process_quality_control | overlap=1 | finding=缺陷处置记录不明确
- [MATCH] 验收程序缺失：未提闭水/淋水检验或抽检厚度，应补充验收记录与试验编号。 | tags=acceptance_procedure,concrete_param,detection_basis | overlap=2 | finding=防水基层条件记录缺失

## case_024 | raw_040_batch_case_024
- expected=3, matched=3, unmatched=0, actual=6
- [MATCH] 试验记录不完整：试压应记录稳压时间、允许压降、读数曲线等，日志缺关键数据，监理应要求补做/补录并签字盖章。 | tags=acceptance_procedure,detection_basis | overlap=1 | finding=条件必填缺失
- [MATCH] 量具不合规风险：压力表需校验有效期，未核验就试压不可靠，应要求更换合格表并留存证书。 | tags=equipment_calibration | overlap=1 | finding=试压量具校验依据缺失
- [MATCH] 程序错误：试压未确认合格就回填，存在返工困难，应要求试验报告出具后方可回填。 | tags=detection_basis,process_quality_control | overlap=2 | finding=条件必填缺失

## case_025 | raw_041_batch_case_025
- expected=3, matched=3, unmatched=0, actual=5
- [MATCH] 模板验收缺失：浇筑前应模板/钢筋/预埋验收，日志未体现验收程序，应要求组织验收并签认后浇筑。 | tags=acceptance_procedure | overlap=1 | finding=验收签认信息缺失
- [MATCH] 加固不足风险：螺栓间距偏大可能胀模，应要求整改并复查，必要时暂停夜间浇筑。 | tags=closure_gap,night_construction,risk_escalation_gap,stop_work_control | overlap=1 | finding=条件必填缺失
- [MATCH] 夜间施工控制不足：夜间浇筑需照明、旁站安排与应急预案，日志未说明监理措施，应补充旁站计划与安全要求。 | tags=finite_space,night_construction,night_release_risk,witness_supervision | overlap=1 | finding=条件必填缺失

## case_026 | raw_042_batch_case_026
- expected=3, matched=3, unmatched=0, actual=3
- [MATCH] 张拉数据缺失：应记录张拉力、伸长量、偏差、持荷时间等，否则无法判断是否合格，应要求补测/补录并签认。 | tags=acceptance_procedure,measurement_recheck_ext,tension_data | overlap=1 | finding=预应力张拉关键数据缺失
- [MATCH] 设备校验缺失：千斤顶、油表需在有效期内校验，未核验即施工应暂停并补齐资料。 | tags=equipment_calibration,stop_work_control | overlap=1 | finding=张拉设备校验信息缺失
- [MATCH] 工序控制点遗漏：未记录张拉顺序/分级加载，监理应要求按方案执行并旁站见证。 | tags=control_point_gap,tension_data,witness_supervision | overlap=1 | finding=预应力张拉关键数据缺失

## case_027 | raw_043_batch_case_027
- expected=3, matched=3, unmatched=0, actual=5
- [MATCH] 质量缺陷未整改：高低差、边缘不顺直应当场返工调整，不能“后期再调”，监理应下发整改并复查。 | tags=closure_gap,paving_quality_closure,process_quality_control | overlap=3 | finding=铺装质量缺陷未闭环
- [MATCH] 实测实量缺失：应记录平整度、坡度、缝宽等抽检数据，日志缺失应提示补录。 | tags=detection_basis,measurement_recheck_ext | overlap=2 | finding=铺装质量缺陷未闭环
- [MATCH] 工序衔接风险：基层压实与砂浆/砂层厚度未记录，后期沉陷风险高，应要求补充工序检查记录。 | tags=detection_basis | overlap=1 | finding=条件必填缺失

## case_028 | raw_044_batch_case_028
- expected=3, matched=3, unmatched=0, actual=9
- [MATCH] 大风条件未评估：大风通常需停吊或限制作业，日志未记录风速与停工措施，监理应要求测风并按方案执行。 | tags=risk_escalation_gap,stop_resume,stop_work_control | overlap=1 | finding=大风吊装管控不足
- [MATCH] 警戒/指挥不规范：封控不到位、指挥混乱属重大风险，应立即停工整改并记录安全指令。 | tags=stop_resume,stop_work_control,traffic_diversion | overlap=1 | finding=吊装警戒指挥措施不足
- [MATCH] 质量复核缺失：吊装后应复紧/复测标高轴线，日志未记录抽查数据，应补充测量与紧固记录。 | tags=measurement_recheck_ext | overlap=1 | finding=关键部位量化数据不足

## case_029 | raw_045_batch_case_029
- expected=3, matched=3, unmatched=0, actual=4
- [MATCH] 工艺缺陷：排水层/定根水是成活关键，日志未指出并未要求立即整改，应督促当日完成并复查。 | tags=closure_gap,greening_process_control | overlap=1 | finding=绿化工序与养护控制不足
- [MATCH] 数量无依据：仅“约60株”缺株号、规格、验收记录，监理应核对苗木检疫/规格清单。 | tags=acceptance_procedure,greening_process_control | overlap=1 | finding=绿化工序与养护控制不足
- [MATCH] 养护计划缺失：未记录支撑、包扎、养护周期与责任人，监理应要求提交养护方案并留痕。 | tags=curing_plan,document_evidence,greening_process_control,yard_protection_gap | overlap=2 | finding=绿化工序与养护控制不足

## case_030 | raw_046_batch_case_030
- expected=3, matched=3, unmatched=0, actual=6
- [MATCH] 未验收即使用：特种设备加节后需验收/检测合格方可使用，应立即停止使用并补齐验收与检测资料。 | tags=special_equipment_acceptance,special_plan | overlap=1 | finding=特种设备未验收即使用
- [MATCH] 安全防护不足：围挡不完整存在人员误入风险，应完善警戒并设置专人监护。 | tags=height_protection,traffic_diversion | overlap=1 | finding=条件必填缺失
- [MATCH] 资料追溯缺失：缺安装单位资质、人员证书、检测报告编号，监理应要求资料齐套并归档。 | tags=concrete_param,material_traceability | overlap=2 | finding=特种设备资料追溯缺失

## case_031 | raw_047_batch_case_031
- expected=3, matched=3, unmatched=0, actual=6
- [MATCH] 钢筋不符合未明确结论：应记录实测值与偏差，并明确“未整改不得浇筑”，必要时停工。 | tags=measurement_recheck_ext,stop_resume,stop_work_control | overlap=2 | finding=异议处理程序缺失
- [MATCH] 隐蔽程序缺失：应提交报验并组织隐蔽验收，日志未体现，应补办并留存验收编号。 | tags=acceptance_procedure,concrete_param,hidden_acceptance | overlap=2 | finding=验收签认信息缺失
- [MATCH] 整改无复查：仅“尽快整改”缺时限与复查记录，应形成闭环（通知单+复查合格）。 | tags=closure_gap | overlap=1 | finding=问题闭环不完整

## case_032 | raw_048_batch_case_032
- expected=3, matched=3, unmatched=0, actual=3
- [MATCH] 雨天砌筑防护缺失：砂浆受雨影响强度，需防雨措施或暂停施工，监理应要求停工/搭棚并记录措施。 | tags=height_protection,stop_resume,stop_work_control,weather_risk | overlap=2 | finding=砌筑施工条件与质量控制不足
- [MATCH] 砂浆质量问题未处理：砖缝不饱满应返工或补缝并复查，必要时抽检砂浆强度。 | tags=closure_gap,detection_basis,process_quality_control | overlap=3 | finding=砌筑施工条件与质量控制不足
- [MATCH] 标高偏差处理不当：井座标高应及时调整，不能依赖后期摊铺“抬起”，应责令整改并复测确认。 | tags=elevation_adjustment_gap,measurement_recheck_ext | overlap=2 | finding=标高偏差处置不当

## case_033 | raw_049_batch_case_033
- expected=3, matched=3, unmatched=0, actual=6
- [MATCH] 检验项目缺失：焊接质量至少需外观尺寸检查，必要时探伤，日志未记录检验数据与结论，应补检并出报告。 | tags=weld_inspection_gap | overlap=1 | finding=焊接检验项目缺失
- [MATCH] 动火安全缺失：未配灭火器/防火毯，监理应要求动火审批与现场防火措施，必要时暂停作业。 | tags=fire_work_safety,special_plan,stop_work_control | overlap=2 | finding=动火安全措施缺失
- [MATCH] 资料缺编号：缺安装报验、材料合格证/出厂检验、焊材批号等，监理应补齐可追溯资料。 | tags=acceptance_procedure,concrete_param,material_traceability | overlap=1 | finding=焊接检验项目缺失

## case_034 | raw_050_batch_case_034
- expected=3, matched=3, unmatched=0, actual=4
- [MATCH] 台背工艺风险：台背应分层薄填、靠近结构宜小型机具夯实，压路机靠近存在结构受力风险，应调整工艺并记录。 | tags=process_quality_control | overlap=1 | finding=条件必填缺失
- [MATCH] 检测缺失：台背压实度是关键控制项，日志未写检测数据与点位，应见证检测并补录。 | tags=detection_basis,measurement_recheck_ext | overlap=2 | finding=检测监测数据缺失
- [MATCH] 沉陷未处置：已出现沉陷迹象应停工排查、返工处理并复测沉降，不能继续回填放行。 | tags=measurement_recheck_ext,process_quality_control,stop_resume,stop_work_control | overlap=1 | finding=条件必填缺失

## case_035 | raw_051_batch_case_035
- expected=3, matched=3, unmatched=0, actual=3
- [MATCH] 夜间质量控制不足：照明不足影响振捣与找平，应要求完善照明并安排旁站，否则应暂停。 | tags=night_construction,night_release_risk,stop_work_control,witness_supervision | overlap=2 | finding=条件必填缺失
- [MATCH] 冷缝风险未闭环：冷缝应按处理方案凿毛、清理、界面剂处理并记录复查，不能仅“加振捣”。 | tags=closure_gap,risk_escalation_gap | overlap=1 | finding=问题闭环不完整
- [MATCH] 见证取样缺失：试块应监理见证取样并编号留存，施工员自带走不合规，应立即纠正并补做见证手续。 | tags=concrete_param | overlap=1 | finding=条件必填缺失

## case_036 | raw_052_batch_case_036
- expected=3, matched=3, unmatched=0, actual=10
- [MATCH] 临边孔洞防护缺失：存在坠落风险，应立即设置围挡、警示标识并记录整改。 | tags=height_protection,traffic_diversion | overlap=1 | finding=条件必填缺失
- [MATCH] 预埋偏差未复测：螺栓定位应测量复核，偏差超限需调整，监理应要求复测数据与整改后复核。 | tags=measurement_recheck,measurement_recheck_ext | overlap=2 | finding=关键部位量化数据不足
- [MATCH] 工序放行不当：存在明显质量风险仍催促浇筑，应明确“复测合格后方可浇筑”，必要时下发通知单。 | tags=measurement_recheck_ext,stop_work_control | overlap=2 | finding=监理意见导向不当

## case_037 | raw_053_batch_case_037
- expected=3, matched=3, unmatched=0, actual=6
- [MATCH] 施工条件不满足：潮湿基层喷浆易空鼓，应要求干燥后施工或采取烘干措施并记录。 | tags=anchor_spray_control,construction_condition_gap | overlap=1 | finding=喷锚施工条件与锚固控制不足
- [MATCH] 锚固质量未控制：螺母未紧固应立即整改并复查扭矩，不能拖延。 | tags=anchor_spray_control,closure_gap | overlap=2 | finding=喷锚施工条件与锚固控制不足
- [MATCH] 关键参数缺失：锚杆长度/间距/拉拔试验等未记录，监理应要求实测实量与试验报告编号。 | tags=anchor_spray_control,concrete_param,detection_basis,measurement_recheck_ext | overlap=3 | finding=喷锚施工条件与锚固控制不足

## case_038 | raw_054_batch_case_038
- expected=3, matched=3, unmatched=0, actual=8
- [MATCH] 有限空间管理缺失：井内作业需气体检测、通风、监护与应急预案，日志未体现，属重大安全隐患，应立即停工整改。 | tags=finite_space,stop_resume,stop_work_control | overlap=1 | finding=有限空间作业控制缺失
- [MATCH] 渗水处置不足：井壁渗水应采取堵漏/降水措施并评估稳定性，不能仅抽水，应形成技术措施与复查。 | tags=closure_gap,risk_escalation_gap,water_logging | overlap=2 | finding=问题闭环不完整
- [MATCH] 监理意见导向错误：在风险未控制时“加快进度”不当，应改为“风险控制优先”，并出具书面指令。 | tags=supervision_guidance_gap | overlap=1 | finding=监理意见导向不当

## case_039 | raw_055_batch_case_039
- expected=3, matched=3, unmatched=0, actual=5
- [MATCH] 验收程序不完整：应由施工/监理等共同验收签字，监理未签却投入使用不合规，应停止使用补验收。 | tags=acceptance_procedure | overlap=1 | finding=验收程序不完整
- [MATCH] 实体缺陷未整改：连墙件缺失、网破损应先整改并复查合格后放行。 | tags=closure_gap,stop_work_control,structure_stability | overlap=2 | finding=验收程序不完整
- [MATCH] 过程控制缺失：已开展抹灰属于违规抢工，应下发停工/整改通知并形成复工条件。 | tags=control_point_gap,stop_resume,stop_work_control | overlap=2 | finding=验收程序不完整

## case_040 | raw_056_batch_case_040
- expected=3, matched=3, unmatched=0, actual=2
- [MATCH] 分层厚度与工艺风险：40cm可能超出控制值，应按试验段参数分层并记录松铺厚度与遍数。 | tags=detection_basis,process_quality_control | overlap=1 | finding=条件必填缺失
- [MATCH] 含水量控制不足：起皮说明含水不适宜，应检测含水量并采取洒水/晾晒、拌和均匀后再压实。 | tags=detection_basis | overlap=1 | finding=条件必填缺失
- [MATCH] 无压实度数据仍判合格：属于结论依据不足，应要求检测并以数据判定，必要时返工重压。 | tags=detection_basis,process_quality_control | overlap=1 | finding=条件必填缺失

## case_041 | raw_057_batch_case_041
- expected=3, matched=3, unmatched=0, actual=8
- [MATCH] 缺陷修补无标准：起泡应按工艺切除、打磨、补涂并做搭接处理，日志未描述流程与复检结论，应补充并复查。 | tags=closure_gap | overlap=1 | finding=问题闭环不完整
- [MATCH] 厚度与粘结未验证：防水层应抽检厚度/粘结，未复测即放行不严谨，应安排检测并留存编号。 | tags=concrete_param,detection_basis,measurement_recheck_ext,stop_work_control | overlap=2 | finding=关键部位量化数据不足
- [MATCH] 基层条件记录缺失：清理、含水率等未记录，影响可追溯性，监理应完善施工前检查记录。 | tags=material_traceability,waterproof_base_record | overlap=2 | finding=防水基层条件记录缺失

## case_042 | raw_058_batch_case_042
- expected=3, matched=3, unmatched=0, actual=6
- [MATCH] 未达强度拆模：拆模应以强度报告为依据，缺报告属于程序与质量风险，应责令停止拆模并补检/补报告。 | tags=strength_before_stripping | overlap=1 | finding=未达强度拆模风险
- [MATCH] 掉角处置不规范：应评估缺陷程度，必要时按修补方案处理并复查，不应随意抹补。 | tags=closure_gap | overlap=1 | finding=缺陷处置记录不明确
- [MATCH] 赶工风险未控制：监理应明确工序控制点与停工条件，必要时签发停工/整改通知并记录复工要求。 | tags=control_point_gap,stop_resume,stop_work_control,supervision_guidance_gap | overlap=1 | finding=未达强度拆模风险

## case_043 | raw_059_batch_case_043
- expected=3, matched=3, unmatched=0, actual=5
- [MATCH] 缺水质检测：给水管投用前需水质检测合格，未检即投用不合规，应要求检测并暂停接通。 | tags=stop_work_control,water_quality_test | overlap=2 | finding=给水投用放行不当
- [MATCH] 过程记录缺失：投加量、接触时间、排放去向等缺失，无法追溯，应补录并按规范重新执行。 | tags=material_traceability | overlap=1 | finding=给水消毒过程记录缺失
- [MATCH] 监理放行不当：对公共卫生风险控制不足，应签发整改通知并明确复验合格后方可投用。 | tags=stop_work_control,supervision_guidance_gap | overlap=2 | finding=给水投用放行不当

## case_044 | raw_060_batch_case_044
- expected=3, matched=3, unmatched=0, actual=5
- [MATCH] 关键参数不合格：外露长度/孔位偏移可能影响锚固效果，应按设计复测并整改，必要时补打锚杆。 | tags=measurement_recheck_ext | overlap=1 | finding=异议处理程序缺失
- [MATCH] 注浆质量不可追溯：应记录浆液配比、压力、用量、回浆情况，不能只写“注满”，监理应要求补齐注浆记录与旁站。 | tags=grouting_traceability,material_traceability,witness_supervision | overlap=3 | finding=注浆质量记录不可追溯
- [MATCH] 未按程序处理异议：施工单位称“影响不大”需技术核定/设计确认，监理应启动变更/核定流程而非直接认定合格。 | tags=dispute_procedure | overlap=1 | finding=异议处理程序缺失

## case_045 | raw_061_batch_case_045
- expected=3, matched=3, unmatched=0, actual=9
- [MATCH] 质量控制条件不足：无测温设备无法控制摊铺/碾压温度，应暂停并补齐设备与记录。 | tags=detection_basis,process_quality_control,stop_work_control | overlap=2 | finding=设备异常处置不充分
- [MATCH] 设备带病作业：漏油污染影响粘结与外观，应停止设备、清理污染并对污染段采取铣刨/修复措施。 | tags=equipment_risk | overlap=1 | finding=设备带病作业风险
- [MATCH] 监理意见不当：风险未控时不应“抓紧完成”，应改为“停工整改+复查放行”，并形成书面指令。 | tags=closure_gap,stop_resume,stop_work_control,supervision_guidance_gap | overlap=3 | finding=监理意见导向不当

## case_046 | raw_062_batch_case_046
- expected=3, matched=3, unmatched=0, actual=3
- [MATCH] 压浆关键数据缺失：水胶比、流动度、保压时间决定饱满度，缺数据无法判定，应要求补测并完善记录。 | tags=grouting_traceability | overlap=1 | finding=注压浆关键参数记录不足
- [MATCH] 设备异常未处置：压力表不灵影响控制，应停用检修或更换并补校验。 | tags=equipment_calibration | overlap=1 | finding=设备异常处置不充分
- [MATCH] 缺抽检验证：压浆应有回浆观察、饱满度抽检或超声/钻孔验证计划，日志未体现，监理应提出抽检要求并留痕。 | tags=detection_basis,document_evidence,grouting_traceability | overlap=2 | finding=注压浆关键参数记录不足

## case_047 | raw_063_batch_case_047
- expected=3, matched=3, unmatched=0, actual=3
- [MATCH] 工序不到位：铺设后应滚压、补缝并浇透水，缺失易空鼓枯黄，应要求立即整改并复查。 | tags=closure_gap,construction_condition_gap,greening_process_control | overlap=1 | finding=绿化工序与养护控制不足
- [MATCH] 养护计划缺失：应明确浇水频次、成活率目标与责任人，监理应要求提交养护方案并检查执行。 | tags=curing_plan,greening_process_control,yard_protection_gap | overlap=2 | finding=绿化工序与养护控制不足
- [MATCH] 质量验收依据不足：未记录面积、品种、验收标准与抽检方法，应补录并关联材料清单。 | tags=detection_basis | overlap=1 | finding=条件必填缺失

## case_048 | raw_064_batch_case_048
- expected=3, matched=3, unmatched=0, actual=4
- [MATCH] 临电重大隐患未处置：配电箱不上锁、漏保未试跳属高风险，应立即停用整改并复查合格后恢复。 | tags=closure_gap | overlap=1 | finding=临电安全隐患处置不足
- [MATCH] 雨天电缆拖地积水：存在触电风险，应架空/穿管并做好防水，监理应签发安全整改通知单。 | tags=temporary_power_rain_risk,water_logging,weather_risk | overlap=3 | finding=雨天临电防护不足
- [MATCH] 缺检查记录闭环：应记录检查点位、整改时限、复查结论与照片编号，避免仅口头提醒。 | tags=closure_gap,concrete_param,measurement_recheck_ext,yard_protection_gap | overlap=1 | finding=临电安全隐患处置不足

## case_049 | raw_065_batch_case_049
- expected=3, matched=3, unmatched=0, actual=6
- [MATCH] 复工程序缺失：停工整改后复工需报审、复查合格并签认，擅自复工应立即制止并补办手续。 | tags=acceptance_procedure,closure_gap,rectification_release_risk,resume_compliance,stop_resume,stop_work_control | overlap=6 | finding=监理结论不合规
- [MATCH] 整改未完成：围挡缺口说明安全条件未满足，应继续停工整改并复查。 | tags=closure_gap,rectification_release_risk,resume_compliance,stop_resume,stop_work_control,traffic_diversion | overlap=5 | finding=监理结论不合规
- [MATCH] 监理结论不合规：监理应明确复工条件与书面批准，必要时签发停工令并抄送业主。 | tags=rectification_release_risk,resume_compliance,stop_resume,stop_work_control | overlap=4 | finding=监理结论不合规

## case_050 | raw_066_batch_case_050
- expected=3, matched=3, unmatched=0, actual=5
- [MATCH] 多项隐患未闭环：应分别提出整改措施、责任人、期限并复查签认，不能只记“口头承诺”。 | tags=acceptance_procedure,closure_gap,yard_protection_gap | overlap=1 | finding=结论与问题描述可能不一致
- [MATCH] 消防通道占用高风险：应立即清理恢复通道并留存影像，必要时下发停工/安全整改通知。 | tags=stop_resume,stop_work_control,traffic_diversion | overlap=1 | finding=结论与问题描述可能不一致
- [MATCH] 试验资料缺失：台账不完整影响质量追溯，监理应要求补齐试验委托/报告编号并建立材料—工序—检验关联。 | tags=concrete_param,detection_basis,material_traceability,supporting_docs_missing | overlap=1 | finding=监理意见导向不当
