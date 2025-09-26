import json
import os
from datetime import datetime

def load_answers(answers_file: str):
    """Lädt gespeicherte Antworten aus der Antwortdatei."""
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
            except:
                continue
    return entries

def save_answer(entry: dict, answers_file: str):
    """Speichert eine Antwort in der Antwortdatei."""
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