from file_extractors import extract_text_from_upload
import json
import streamlit as st

from rules_loader import load_rules
from checker import run_checks
from ai_helper import ai_review_enabled, ai_review
from report_exporter import build_docx_report

st.set_page_config(page_title="监理文书合规校验 V1", layout="wide")

st.title("监理文书合规校验系统 V1（市政/公路）")
st.caption("不改模板，只核查内容：缺失项 / 风险用词 / 闭环问题 / 逻辑冲突")

with st.sidebar:
    st.header("设置")
    rules_path = st.text_input("规则库文件", value="rules_v1.xlsx")
    doc_type = st.selectbox("文书类型", ["日志", "巡视"])
    st.divider()
    st.markdown("把 `rules_v1.xlsx` 放在同一文件夹，最省事。")

col1, col2 = st.columns([1.2, 1])
source_label = "manual"

with col1:
    st.subheader("上传日志/巡视文件（可选）")
    uploaded = st.file_uploader(
        "支持：PDF / DOCX / TXT / 图片（PNG/JPG）",
        type=["pdf", "docx", "txt", "png", "jpg", "jpeg", "webp"],
    )

    if uploaded is not None:
        extracted_text, source = extract_text_from_upload(uploaded)
        source_label = source

        if extracted_text.strip():
            st.success(f"已从文件提取文本（来源：{source}），并自动填入下方文本框。")
            st.session_state["input_text"] = extracted_text
        else:
            if source == "image_no_ocr":
                st.warning(
                    "检测到图片，但当前环境未启用 OCR（pytesseract/Tesseract）。"
                    "请先安装 OCR，或手动复制图片文字到下方文本框。"
                )
            elif source == "pdf":
                st.warning(
                    "PDF 可能是扫描版图片，未能直接提取文本。"
                    "建议启用 OCR 或将内容复制到下方文本框。"
                )
            elif source == "unsupported":
                st.warning("暂不支持该文件类型，请转换为 PDF/DOCX/TXT/图片。")
            else:
                st.warning("未能从文件提取文本，请手动粘贴到下方文本框。")

    st.subheader("粘贴文书内容")
    text = st.text_area(
        "粘贴文书内容",
        key="input_text",
        height=260,
        placeholder="也可以先上传文件自动识别，再在这里补充/修改。",
    )

    run_btn = st.button("开始校验", type="primary", use_container_width=True)

with col2:
    st.subheader("输出报告")
    st.write("等待校验...")

    if run_btn:
        if not str(text).strip():
            st.error("请先粘贴文书内容再校验。")
            st.stop()

        try:
            rules = load_rules(rules_path)
        except Exception as e:
            st.error(f"规则库加载失败：{e}")
            st.stop()

        report = run_checks(doc_type, text, rules)

        if ai_review_enabled():
            report["ai_review"] = ai_review(doc_type, text, report)

        s = report["summary"]
        st.success(
            f"校验完成：共 {s['total']} 条提示（高 {s['high']} / 中 {s['medium']} / 低 {s['low']}）"
        )

        findings = report["findings"]
        if not findings:
            st.info("未发现明显问题（仍建议人工复核）。")
        else:
            groups = {}
            for f in findings:
                groups.setdefault(f["category"], []).append(f)

            def render_group(title: str, key: str):
                items = groups.get(key, [])
                if not items:
                    return
                st.markdown(f"### {title}（{len(items)}）")
                for i, f in enumerate(items, 1):
                    sev = f["severity"]
                    badge = "🔴" if sev == "high" else ("🟠" if sev == "medium" else "🟢")
                    st.markdown(f"**{badge} {i}. {f['title']}**")
                    if f.get("quote"):
                        st.write(f"触发：{f['quote']}")
                    if f.get("reason"):
                        st.write(f"原因：{f['reason']}")
                    if f.get("suggestion"):
                        st.write(f"建议：{f['suggestion']}")
                    st.divider()

            render_group("必填项缺失", "missing_items")
            render_group("风险用词", "risky_phrases")
            render_group("闭环问题", "closure_issues")
            render_group("逻辑/一致性提醒", "logic_warnings")

        st.markdown("### 可复制建议句")
        st.code("\n".join(report.get("copy_ready_suggestions", [])), language="text")

        st.markdown("### 导出报告")
        json_str = json.dumps(report, ensure_ascii=False, indent=2)
        docx_data = build_docx_report(report, doc_type=doc_type, source=source_label)
        st.download_button(
            label="下载 JSON 报告",
            data=json_str.encode("utf-8"),
            file_name="compliance_report.json",
            mime="application/json",
            use_container_width=True,
        )
        st.download_button(
            label="下载 Word 报告（DOCX）",
            data=docx_data,
            file_name="compliance_report.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
        st.code(json_str, language="json")
