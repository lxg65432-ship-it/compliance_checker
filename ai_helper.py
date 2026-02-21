from __future__ import annotations

def ai_review_enabled() -> bool:
    return False

def ai_review(doc_type: str, text: str, report: dict) -> dict:
    return {"enabled": False, "notes": "AI review disabled in V1"}
