# file_extractors.py
from __future__ import annotations

import io
from typing import Tuple


def extract_text_from_upload(uploaded_file) -> Tuple[str, str]:
    """
    返回: (text, source_label)
    source_label: txt / docx / pdf / image_ocr / image_no_ocr / unsupported
    """
    name = (uploaded_file.name or "").lower()

    # ---------- TXT ----------
    if name.endswith(".txt"):
        data = uploaded_file.getvalue()
        try:
            return data.decode("utf-8"), "txt"
        except UnicodeDecodeError:
            return data.decode("gbk", errors="ignore"), "txt"

    # ---------- DOCX ----------
    if name.endswith(".docx"):
        from docx import Document

        doc = Document(io.BytesIO(uploaded_file.getvalue()))
        paras = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paras), "docx"

    # ---------- PDF ----------
    if name.endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(uploaded_file.getvalue()))
        texts = []

        for page in reader.pages:
            t = page.extract_text() or ""
            if t.strip():
                texts.append(t)

        return "\n".join(texts).strip(), "pdf"

    # ---------- IMAGE (OCR) ----------
    if name.endswith((".png", ".jpg", ".jpeg", ".webp")):
        try:
            import pytesseract
            from PIL import Image

            # 指定 tesseract 路径（按需调整）
            pytesseract.pytesseract.tesseract_cmd = (
                r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            )

            img = Image.open(io.BytesIO(uploaded_file.getvalue()))
            text = pytesseract.image_to_string(img, lang="chi_sim+eng")
            return (text or "").strip(), "image_ocr"

        except Exception as e:
            print("OCR error:", e)
            return "", "image_no_ocr"

    return "", "unsupported"
