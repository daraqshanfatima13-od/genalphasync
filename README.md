Gen-α-Sync Analyzer 🧠⚡
AI-powered emotional wellness & crisis detection API built with FastAPI.

🚀 Features
✅ Detects crisis keywords (English, Hindi, Hinglish).
✅ Uses a Hugging Face emotion model as backup.
✅ Supports PII redaction (phone numbers, emails).
✅ Provides reason for detection (keyword_override / model).
✅ API key authentication for safety.
✅ Simple logging (requests.log, mismatches.log).

📂 Project Structure
genalphasync/
│── api.py                # FastAPI app (main API)
│── crisis_detector.py     # Crisis + emotion detection logic
│── keywords.txt           # Crisis keywords list
│── requirements.txt       # Dependencies
│── requests.log           # (auto-created) request logs
│── mismatches.log         # (auto-created) model vs keyword mismatches

⚙️ Setup
1. Clone the repo
git clone <your-repo-url>
cd genalphasync
2. Create virtual environment
python -m venv genenv
genenv\Scripts\activate   # (Windows)
3. Install dependencies
pip install -r requirements.txt
4. Set API keys
In Windows PowerShell:
export HF_API_KEY=your_huggingface_token_here
Reopen terminal after setting env vars.

▶️ Run the API
uvicorn api:app --reload --port 8000
Open:
👉 Docs UI → http://127.0.0.1:8000/docs
👉 Healthcheck → http://127.0.0.1:8000/

📌 Example Usage
Request
POST /analyze
Headers:
  x-api-key: my-team-secret123
Body:
{
  "text": "I feel so sad and alone"
}

Response
{
  "original_text": "I feel so sad and alone",
  "redacted_text": "I feel so sad and alone",
  "emotion": "sadness",
  "score": 0.98,
  "keyword_flag": false,
  "model_flag": true,
  "crisis": true,
  "reason": "model",
  "note": ""
}

✅ Crisis Test Checklist
Input	Expected Result
"I am very happy"	joy → not crisis
"I want to die"	keyword_override → crisis
"I feel so sad and alone"	model sadness → crisis
"Kal exam hai, I am very stressed"	anger/stress → not crisis

🛠️ Tech Stack
FastAPI (backend API)
Uvicorn (server)
Hugging Face Transformers API (emotion model)

📖 Authors
Built with ❤️ by the Gen-α-Sync Team
