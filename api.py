from fastapi import FastAPI
from pydantic import BaseModel
from crisis_detector import check_crisis   # only import check_crisis for now
from crisis_detector import check_crisis, log_mismatch
from crisis_detector import check_crisis, log_mismatch


app = FastAPI()

class Message(BaseModel):
    text: str

@app.post("/analyze")
def analyze(msg: Message):
    result = check_crisis(msg.text)
    log_mismatch(result)   # logs disagreements for future improvement
    return result


