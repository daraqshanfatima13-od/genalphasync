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
from transformers import pipeline

# ----- Load model once -----
emotion_model = pipeline(
    "text-classification",
    model="bhadresh-savani/distilbert-base-uncased-emotion",
    return_all_scores=False
)

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
    out = emotion_model(text)[0]  # e.g. {'label': 'sadness', 'score': 0.92}
    label = out['label'].lower()
    score = float(out['score'])
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
import json

def log_mismatch(result: dict, path="mismatches.log"):
    """
    Save mismatches (keyword vs model) into a file.
    """
    if result["reason"] == "keyword" and result["emotion"] not in [None, "sadness", "fear"]:
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
    """
    Save disagreements between keyword_flag and model_flag into a file.
    Example: keyword found but model said 'joy'.
    """
    if result.get("keyword_flag") != result.get("model_flag"):
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")
