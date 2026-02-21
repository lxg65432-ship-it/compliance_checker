# compliance_checker

## 快速开始
1. 创建并激活虚拟环境（Windows）：
   `python -m venv .venv`
   `.venv\Scripts\activate`
2. 安装依赖：
   `pip install -r requirements.txt`
3. 启动应用：
   `streamlit run app.py`

> 说明：如果要识别图片文字，需要额外安装 Tesseract OCR（Windows 默认路径通常为 `C:\Program Files\Tesseract-OCR\tesseract.exe`）。
> 报告导出：校验完成后可下载 `JSON` 与 `Word（DOCX）` 两种格式。

## 样例评估（误报/漏报）
1. 编辑样例文件：`test_samples/cases.json`
2. 运行评估：
   `python .\scripts\evaluate_samples.py --rules rules_v1.xlsx --cases test_samples/cases.json`
3. 查看评估报告：
   `test_samples/last_eval_report.json`

`expected` 字段支持的主要约束：
- `required_categories` / `forbidden_categories`
- `required_titles_contains` / `forbidden_titles_contains`
- `min_total` / `max_total`
- `min_high` / `max_high` / `min_medium` / `max_medium` / `min_low` / `max_low`

## Plan 自动同步
本项目支持将计划文档自动提交并推送到 Git 远端，默认仅处理 `docs/*plan*.md`。

### 文件说明
- `docs/implementation-plan.md`: 主计划文件。
- `scripts/auto_push_once.ps1`: 单次执行（检查变更、add/commit/push）。
- `scripts/auto_push_plan.ps1`: 常驻监听器（FileSystemWatcher + 防抖 + 互斥）。
- `scripts/register_auto_push_task.ps1`: 注册 Windows 登录自启任务。

### 使用步骤
1. 确保本机已安装 Git，且仓库已配置远程与认证。
2. 注册计划任务：
   `powershell -ExecutionPolicy Bypass -File .\scripts\register_auto_push_task.ps1`
3. 立即手动启动（可选）：
   `Start-ScheduledTask -TaskName 'ComplianceChecker_AutoPushPlan'`

### 日志与排障
- 日志目录：`.codex-auto-push/auto_push.log`
- 若自动推送失败，先检查：
  - `git --version` 是否可用
  - 当前分支是否存在远程 `origin`
  - 认证是否有效（SSH key / token）

### 停用与回滚
- 停用自动上传：
  `Unregister-ScheduledTask -TaskName 'ComplianceChecker_AutoPushPlan' -Confirm:$false`
- 手动单次执行：
  `powershell -ExecutionPolicy Bypass -File .\scripts\auto_push_once.ps1`
