import random
from datetime import datetime
import json
import os

def randomize_options(question):
    """Mischt die Antwortoptionen eines Quiz-Elements."""
    options = question["optionen"].copy()
    correct = question["richtig"]
    random.shuffle(options)
    return {
        "frage": question["frage"],
        "optionen": options,
        "richtig": correct
    }

def save_quiz_answer(entry: dict, answers_file: str):
    """Speichert eine Antwort in der angegebenen Datei."""
    os.makedirs(os.path.dirname(answers_file), exist_ok=True)
    
    # Lade existierende Antworten
    answers = []
    if os.path.exists(answers_file):
        with open(answers_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    answers.append(json.loads(line.strip()))
                except:
                    continue
    
    # Füge neue Antwort hinzu
    answers.append(entry)
    
    # Speichere alle Antworten
    with open(answers_file, "w", encoding="utf-8") as f:
        for answer in answers:
            f.write(json.dumps(answer, ensure_ascii=False) + "\n")

def load_quiz_answers(answers_file: str):
    """Lädt alle gespeicherten Antworten (Liste von dicts)."""
    if not os.path.exists(answers_file):
        return []
    entries = []
    with open(answers_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except Exception:
                continue
    return entries