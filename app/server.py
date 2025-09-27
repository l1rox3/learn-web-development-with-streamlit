# server.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import json, os

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DB_FILE = "answers.json"
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump([], f)

class Entry(BaseModel):
    timestamp: str
    username: str
    quiz: str
    question: str
    answer: str
    correct: bool

@app.post("/answers")
def save_answer(entry: Entry):
    with open(DB_FILE, "r") as f:
        data = json.load(f)
    # Antwort speichern (überschreiben, falls schon vorhanden)
    data = [a for a in data if not (a["username"] == entry.username and a["question"] == entry.question)]
    data.append(entry.dict())
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)
    return {"status": "ok"}

@app.get("/answers")
def load_answers():
    with open(DB_FILE, "r") as f:
        return json.load(f)
