from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent


def _read_text(path: Path) -> str:
    suffix = path.suffix.lower()
    data = path.read_bytes()

    if suffix in {".txt", ".md"}:
        try:
            return data.decode("utf-8").lstrip("\ufeff")
        except UnicodeDecodeError:
            return data.decode("gbk", errors="ignore").lstrip("\ufeff")

    if suffix == ".docx":
        from docx import Document
        import io

        doc = Document(io.BytesIO(data))
        return "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])

    if suffix == ".pdf":
        from pypdf import PdfReader
        import io

        reader = PdfReader(io.BytesIO(data))
        texts: list[str] = []
        for page in reader.pages:
            t = page.extract_text() or ""
            if t.strip():
                texts.append(t.strip())
        return "\n".join(texts)

    raise ValueError(f"Unsupported sample format: {path.name}")


def _infer_doc_type(name: str, default_doc_type: str) -> str:
    low = name.lower()
    if any(k in low for k in ("xunshi", "xun", "\u5de1", "\u5de1\u89c6")):
        return "\u5de1\u89c6"  # 巡视
    if any(k in low for k in ("rizhi", "log", "\u65e5\u5fd7")):
        return "\u65e5\u5fd7"  # 日志
    return default_doc_type


def build_cases(raw_dir: Path, output_path: Path, default_doc_type: str) -> dict[str, Any]:
    files = sorted([p for p in raw_dir.glob("*") if p.is_file() and not p.name.startswith(".")])
    cases: list[dict[str, Any]] = []

    for idx, path in enumerate(files, 1):
        try:
            text = _read_text(path).strip()
        except Exception as e:
            print(f"[skip] {path.name}: {e}")
            continue
        if not text:
            print(f"[skip] {path.name}: empty text")
            continue

        case_id = f"raw_{idx:03d}_{path.stem}"
        doc_type = _infer_doc_type(path.stem, default_doc_type)

        cases.append(
            {
                "id": case_id,
                "doc_type": doc_type,
                "text": text,
                "expected": {
                    "min_total": 0,
                    "max_total": 50,
                    "required_categories": [],
                    "forbidden_categories": [],
                    "required_titles_contains": [],
                    "forbidden_titles_contains": [],
                },
                "meta": {"source_file": path.name},
            }
        )

    payload = {"cases": cases}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Build evaluation cases from raw sample files.")
    parser.add_argument("--raw-dir", default="test_samples/raw", help="Raw sample file directory.")
    parser.add_argument("--output", default="test_samples/cases.generated.json", help="Generated cases json path.")
    parser.add_argument(
        "--default-doc-type",
        default="\u65e5\u5fd7",  # 日志
        choices=["\u65e5\u5fd7", "\u5de1\u89c6"],  # 日志/巡视
        help="Default doc type.",
    )
    args = parser.parse_args()

    raw_dir = (REPO_ROOT / args.raw_dir).resolve() if not Path(args.raw_dir).is_absolute() else Path(args.raw_dir)
    output = (REPO_ROOT / args.output).resolve() if not Path(args.output).is_absolute() else Path(args.output)
    if not raw_dir.exists():
        raise SystemExit(f"Raw sample directory not found: {raw_dir}")

    payload = build_cases(raw_dir, output, args.default_doc_type)
    print(f"Generated cases: {len(payload['cases'])}")
    print(f"Output: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
