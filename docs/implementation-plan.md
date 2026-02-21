# 监理审查项目实施计划（Plan 文件化 + 默认自动上传 Git）

## 1. 目标
- 将实施计划固定为仓库文件，便于多电脑同步与追踪。
- 在本地启用“保存后自动提交并推送”机制，仅覆盖计划文档。

## 2. 范围
- 主计划文件：`docs/implementation-plan.md`
- 自动同步目标：`docs/*plan*.md`
- 自动化脚本：`scripts/auto_push_once.ps1`、`scripts/auto_push_plan.ps1`、`scripts/register_auto_push_task.ps1`

## 3. 里程碑
1. 建立计划文件与目录规范（docs/scripts）。
2. 完成单次推送执行器（检测变更、提交、推送、日志）。
3. 完成常驻监听器（防抖、互斥、事件监听）。
4. 完成 Windows 计划任务注册（登录自启）。
5. 完成 README 使用说明与回滚方案。

## 4. 待办清单
- [x] 新建主计划文件并固化方案。
- [x] 实现 `auto_push_once.ps1`。
- [x] 实现 `auto_push_plan.ps1`。
- [x] 实现 `register_auto_push_task.ps1`。
- [x] 完成文档说明（README）。
- [ ] 在目标机器验证 Git、远程仓库与认证配置。
- [ ] 实测 6 个场景并根据日志调参（防抖秒数/提交前缀）。

## 5. 验收标准
- 修改任意 `docs/*plan*.md` 后，30 秒内可见 commit 与 push（网络正常）。
- 无内容变化保存不产生空 commit。
- 非 plan 文件变化不会被自动提交。
- 网络异常时 push 失败有日志，恢复后再次保存可继续推送。
- 连续保存不会引发并发冲突或重复推送风暴。

## 6. 运行与维护约定
- 自动提交前缀：`docs(plan): auto sync`
- 建议每台开发机都执行一次 `scripts/register_auto_push_task.ps1`。
- 如需停用自动化，删除计划任务 `ComplianceChecker_AutoPushPlan`。

## 7. 风险与注意事项
- 自动推送依赖 Git 安装、仓库已初始化、已配置远程与认证。
- 请确保计划文档不包含敏感信息（自动提交会立刻推远端）。
- 若需要扩展范围到整个 docs，可将匹配改为 `docs/*.md`。
