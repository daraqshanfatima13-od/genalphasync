# crisis_detector.py
import re
import json
import os
import requests
from difflib import SequenceMatcher

# ---------------- Load keywords ----------------
def load_keywords(path="keywords.txt"):
    try:
        with open(path, encoding="utf-8") as f:
            kws = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        kws = []
    patterns = [re.compile(r"\b" + re.escape(k) + r"\b", flags=re.I) for k in kws]
    return kws, patterns

KEYWORDS_LIST, KEYWORD_PATTERNS = load_keywords()
print(f"DEBUG: Loaded {len(KEYWORDS_LIST)} keywords")

# ---------------- Model config ----------------
HF_API_KEY = os.environ.get("HF_API_KEY")
API_URL = "https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base"
headers = {"Authorization": f"Bearer {HF_API_KEY}"} if HF_API_KEY else {}

def query_hf_model(text: str):
    response = requests.post(API_URL, headers=headers, json={"inputs": text})
    result = response.json()

    # Handle case where Hugging Face returns a list of dicts
    if isinstance(result, list) and len(result) > 0:
        if isinstance(result[0], list) and len(result[0]) > 0:
            # old format: [[{label, score}, ...]]
            label = result[0][0]["label"]
            score = result[0][0]["score"]
            return label, score
        elif isinstance(result[0], dict):
            # new format: [{label, score}, {label, score}, ...]
            label = result[0]["label"]
            score = result[0]["score"]
            return label, score

    return None, None


# ---------------- PII redaction ----------------
PHONE_RE = re.compile(r'(\+?\d[\d\s-]{7,}\d)')
EMAIL_RE = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')

def redact_pii(text: str) -> str:
    text = PHONE_RE.sub("[PHONE]", text)
    text = EMAIL_RE.sub("[EMAIL]", text)
    return text

# ---------------- Keyword check ----------------
def keyword_check(text: str, fuzzy_threshold=0.85) -> bool:
    t = text.lower()
    for pat in KEYWORD_PATTERNS:
        if pat.search(t):
            return True
    words = re.findall(r'\w+', t)
    for kw in KEYWORDS_LIST:
        kw_words = re.findall(r'\w+', kw.lower())
        if not kw_words:
            continue
        L = len(kw_words)
        for i in range(0, max(1, len(words) - L + 1)):
            ngram = " ".join(words[i:i+L])
            ratio = SequenceMatcher(None, kw.lower(), ngram).ratio()
            if ratio >= fuzzy_threshold:
                return True
    return False

# ---------------- Main check ----------------
def check_crisis(text: str, redact: bool = True) -> dict:
    original = text
    if redact:
        text = redact_pii(text)

    kw_flag = keyword_check(text)
    if kw_flag:
        return {
            "original_text": original,
            "redacted_text": text,
            "emotion": None,
            "score": None,
            "top_scores": None,
            "keyword_flag": True,
            "model_flag": False,
            "crisis": True,
            "reason": "keyword_override",
            "note": ""
        }

    label, score = query_hf_model(text)
    model_flag = label in ["sadness", "fear"] and score and score > 0.8
    top_scores = [(label, float(score))] if label and score is not None else None

    return {
        "original_text": original,
        "redacted_text": text,
        "emotion": label,
        "score": score,
        "top_scores": top_scores,
        "keyword_flag": False,
        "model_flag": model_flag,
        "crisis": model_flag,
        "reason": "model" if model_flag else "none",
        "note": ""
    }

# ---------------- Logging ----------------
def log_mismatch(result: dict, path="mismatches.log"):
    kw_flag = bool(result.get("keyword_flag", False))
    model_flag = bool(result.get("model_flag", False))
    if kw_flag != model_flag:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

# ---------------- Demo ----------------
if __name__ == "__main__":
    tests = [
        "I am very happy today!",
        "I feel so sad and alone.",
        "I want to kill myself.",
        "Kal exam hai, I am very stressed.",
        "Mujhe lagta hai apni zindagi khatam kar doon."
    ]
    for t in tests:
        print(check_crisis(t))
