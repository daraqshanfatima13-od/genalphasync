# api.py
import os
import json
from fastapi import FastAPI, HTTPException, Header, Request
from pydantic import BaseModel
from datetime import datetime
from crisis_detector import check_crisis, log_mismatch, redact_pii  # uses your working file

app = FastAPI(title="Gen-α-Sync Analyzer")

# Simple API key auth (set this as env var before running / deploy)
API_KEY = os.environ.get("API_KEY", "dev-secret")  # override in production/render

# Request model
class AnalyzeRequest(BaseModel):
    text: str

# Health check
@app.get("/")
def read_root():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

# Analyze endpoint
@app.post("/analyze")
async def analyze(req: AnalyzeRequest, x_api_key: str | None = Header(None)):
    # 1) Check API key
    print("DEBUG: received header =", x_api_key, "expected =", API_KEY)

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    print("DEBUG: received header =", x_api_key)
    print("DEBUG: expected API_KEY =", API_KEY)


    text = req.text
    # 2) Run detection
    result = check_crisis(text)

    # 3) Log mismatches for future inspection (non-blocking)
    try:
        log_mismatch(result)
    except Exception as e:
        # don't fail the request if logging fails
        print("log_mismatch error:", e)

    # 4) Write a small request log for auditing (safe: PII already redacted inside check_crisis)
    try:
        safe_log = {
            "time": datetime.utcnow().isoformat(),
            "text": result.get("redacted_text", text),
            "crisis": result.get("crisis", False),
            "reason": result.get("reason", "")
        }
        with open("requests.log", "a", encoding="utf-8") as f:
            f.write(json.dumps(safe_log, ensure_ascii=False) + "\n")
    except Exception as e:
        print("request log error:", e)

    # 5) Return result
    return result
