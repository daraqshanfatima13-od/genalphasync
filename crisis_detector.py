# crisis_detector.py
# put at top of crisis_detector.py
import re
from difflib import SequenceMatcher

def load_keywords(path="keywords.txt"):
    try:
        with open(path, encoding="utf-8") as f:
            kws = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        kws = []
    # compile simple regex patterns (word boundaries)
    patterns = [re.compile(r"\b" + re.escape(k) + r"\b", flags=re.I) for k in kws]
    return kws, patterns

# load once at module start
KEYWORDS_LIST, KEYWORD_PATTERNS = load_keywords()
import re
import json

import requests
import os

HF_API_KEY = os.environ.get("HF_API_KEY")
API_URL = "https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base"
headers = {"Authorization": f"Bearer {HF_API_KEY}"}

def query_hf_model(text: str):
    response = requests.post(API_URL, headers=headers, json={"inputs": text})
    result = response.json()
    if isinstance(result, list) and len(result) > 0:
        label = result[0][0]["label"]
        score = result[0][0]["score"]
        return label, score
    return None, None


# ----- Crisis keywords (expand these) -----
CRISIS_KEYWORDS = [
    "suicide", "kill myself", "end my life", "i want to die",
    "hurt myself", "marna hai", "apni zindagi khatam", "marna chahta/chahti",
    "khatam karna", "i will kill myself", "i can't go on", "no reason to live"
    "suicide",
    "kill myself",
    "end my life",
    "i want to die",
    "hurt myself",
    "marna hai",
    "mujhe marna hai",
    "zindagi khatam",
    "main marna chahta hoon",
    "main marna chahti hoon"
]

# ----- Simple PII redaction (phone numbers, emails) -----
PHONE_RE = re.compile(r'(\+?\d[\d\s-]{7,}\d)')   # very simple phone regex
EMAIL_RE = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')

def redact_pii(text: str) -> str:
    text = PHONE_RE.sub("[PHONE]", text)
    text = EMAIL_RE.sub("[EMAIL]", text)
    return text

def keyword_check(text: str, fuzzy_threshold=0.85) -> bool:
    t = text.lower()
    # 1) exact / regex match
    for pat in KEYWORD_PATTERNS:
        if pat.search(t):
            return True

    # 2) fuzzy match on n-grams (handles small typos)
    words = re.findall(r'\w+', t)  # split into words
    for kw in KEYWORDS_LIST:
        kw_words = re.findall(r'\w+', kw.lower())
        if not kw_words:
            continue
        L = len(kw_words)
        # slide over text words with same length and compare
        for i in range(0, max(1, len(words) - L + 1)):
            ngram = " ".join(words[i:i+L])
            ratio = SequenceMatcher(None, kw.lower(), ngram).ratio()
            if ratio >= fuzzy_threshold:
                return True
    return False


# ----- Model-based check -----
def model_check(text: str, threshold: float = 0.80) -> dict:
    """
    Returns dict: {'label': label, 'score': score, 'is_risky': bool}
    We consider 'sadness' or 'fear' with score > threshold as risky.
    """
    label, score = query_hf_model(text)
    is_risky = (label in ["sadness", "fear"]) and (score > threshold)
    return {"label": label, "score": score, "is_risky": is_risky}


# ----- Full check -----
def check_crisis(text: str, redact: bool = True) -> dict:
    """
    Returns:
    {
      "original_text": "...",
      "redacted_text": "...",
      "emotion": "sadness",
      "score": 0.9,
      "keyword_flag": True/False,
      "model_flag": True/False,
      "crisis": True/False
    }
    """
    original = text
    if redact:
        text = redact_pii(text)

    kw_flag = keyword_check(text)
    model_result = model_check(text)
    model_flag = model_result["is_risky"]

    crisis = kw_flag or model_flag

    return {
        "original_text": original,
        "redacted_text": text,
        "emotion": model_result["label"],
        "score": model_result["score"],
        "keyword_flag": kw_flag,
        "model_flag": model_flag,
        "crisis": crisis
    }

# ----- Simple escalation (demo) -----
def escalate_alert(result: dict):
    """
    Demo escalation: write a JSON file or print. In real system:
    - Send SMS/email to counselor (with secure process)
    - Create a ticket in dashboard for urgent human review
    """
    if result["crisis"]:
        # create an alert file (demo)
        with open("last_crisis_alert.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print("!!! CRISIS DETECTED !!! — alert written to last_crisis_alert.json")
    else:
        print("No crisis detected.")

# ----- Quick test runner -----
if __name__ == "__main__":
    test_messages = [
        "I am very happy today!",
        "I feel so sad and alone.",
        "I want to kill myself.",
        "Kal exam hai, I am very stressed.",
        "Mujhe lagta hai apni zindagi khatam kar doon.",
        "My phone is 9876543210, call me",  # tests phone redaction
        "contact me at test.user@example.com"
    ]

    for m in test_messages:
        res = check_crisis(m)
        print("Original:", res["original_text"])
        print("Redacted:", res["redacted_text"])
        print("Emotion:", res["emotion"], "Score:", res["score"])
        print("Keyword flag:", res["keyword_flag"], "Model flag:", res["model_flag"])
        print("Final crisis:", res["crisis"])
        print("-" * 40)
        # Demo escalate
        escalate_alert(res)
def check_crisis(text: str, redact: bool = True) -> dict:
    """
    Returns a dict with:
      original_text, redacted_text, emotion, score, top_scores,
      keyword_flag, model_flag, crisis (final), reason
    Keyword override: if any crisis keyword found => immediate crisis True
    """
    original = text
    if redact:
        text = redact_pii(text)

    # 1) Keyword check (immediate override)
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

    # 2) No keyword found -> use model
    try:
        # If you're using HF inference API, call query_hf_model(text)
        # If you're using local pipeline, call model_check(text)
        # For example, if you implemented query_hf_model:
        emotion_label, emotion_score = query_hf_model(text)
        if emotion_label is None:
            # model couldn't produce result
            model_flag = False
            top_scores = None
        else:
            # simple rule: sadness/fear with threshold => risky
            model_flag = (emotion_label.lower() in ["sadness", "fear"] and float(emotion_score) > 0.8)
            top_scores = [(emotion_label, float(emotion_score))]
    except Exception as e:
        # model failed -> treat as non-crisis but record note
        return {
            "original_text": original,
            "redacted_text": text,
            "emotion": None,
            "score": None,
            "top_scores": None,
            "keyword_flag": False,
            "model_flag": False,
            "crisis": False,
            "reason": "model_error",
            "note": str(e)
        }

    return {
        "original_text": original,
        "redacted_text": text,
        "emotion": emotion_label,
        "score": float(emotion_score) if emotion_score is not None else None,
        "top_scores": top_scores,
        "keyword_flag": False,
        "model_flag": model_flag,
        "crisis": model_flag,
        "reason": "model" if model_flag else "none",
        "note": ""
    }

import json
def log_mismatch(result: dict, path="mismatches.log"):
    """
    Save disagreements where keyword_flag != model_flag,
    but be robust to missing keys.
    """
    try:
        keyword_flag = bool(result.get("keyword_flag", False))
        model_flag = bool(result.get("model_flag", False))
    except Exception:
        # If result is malformed, write the raw JSON for manual inspection
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"raw_result": result}, ensure_ascii=False) + "\n")
        return

    # Only log when they disagree (useful for later inspection)
    if keyword_flag != model_flag:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

def log_mismatch(result: dict, path="mismatches.log"):
    """
    Save disagreements where keyword_flag != model_flag,
    but be robust to missing keys.
    """
    try:
        keyword_flag = bool(result.get("keyword_flag", False))
        model_flag = bool(result.get("model_flag", False))
    except Exception:
        # If result is malformed, write the raw JSON for manual inspection
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"raw_result": result}, ensure_ascii=False) + "\n")
        return

    # Only log when they disagree (useful for later inspection)
    if keyword_flag != model_flag:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    test_messages = [
        "I am very happy today!",             # joy
        "I feel so sad and alone.",           # sadness
        "[crisis phrase example 1]",          # should trigger keyword override
        "Kal exam hai, I am very stressed.",  # stress but not crisis
        "[crisis phrase example 2]"           # another risky phrase
    ]

    for m in test_messages:
        res = check_crisis(m)
        print(res)
        log_mismatch(res)
        escalate_alert(res)
import json

def log_mismatch(result: dict, path="mismatches.log"):
    kw_flag = bool(result.get("keyword_flag", False))
    model_flag = bool(result.get("model_flag", False))
    reason = result.get("reason", "unknown")

    if kw_flag != model_flag:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "text": result.get("original_text"),
                "emotion": result.get("emotion"),
                "keyword_flag": kw_flag,
                "model_flag": model_flag,
                "reason": reason
            }, ensure_ascii=False) + "\n")

