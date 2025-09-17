from crisis_detector import check_crisis
def check_crisis(text: str, redact: bool = True) -> dict:
    """
    Simple and safe:
      - If any crisis keyword found -> immediate crisis (override)
      - Else use the model to decide (sadness/fear with high score)
    Returns simple dict with fields you can use.
    """
    original = text
    if redact:
        text = redact_pii(text)

    # 1) Keyword check (IMMEDIATE OVERRIDE)
    kw_flag = keyword_check(text)
    if kw_flag:
        # If keyword found, return immediately with crisis True
        return {
            "original_text": original,
            "redacted_text": text,
            "emotion": None,
            "score": None,
            "keyword_flag": True,
            "model_flag": False,
            "crisis": True,
            "note": "keyword_override"
        }

    # 2) No keyword found -> use model
    model_result = model_check(text)   # existing function that returns label and score
    model_flag = model_result["is_risky"]
    return {
        "original_text": original,
        "redacted_text": text,
        "emotion": model_result["label"],
        "score": model_result["score"],
        "keyword_flag": False,
        "model_flag": model_flag,
        "crisis": model_flag,
        "note": ""
    }

