"""
Quiz-Modul für die Streamlit Quiz-App
"""
import streamlit as st
import os
import json
import random
from datetime import datetime

# Pfad zu den gespeicherten Antworten
ANSWERS_FILE = "./data/answers.json"

# ---------------- Quiz-Definitionen ----------------
QUIZZES = {
    "Kleidung": {
        "kleidung1": {
            "frage": "Welches Kleidungsstück ist bei hinduistischen Frauen weit verbreitet?",
            "optionen": ["Sari", "Kimono", "Dirndl", "Kaftan"],
            "richtig": "Sari"
        },
        "kleidung2": {
            "frage": "Welche Farbe wird traditionell bei hinduistischen Hochzeiten getragen?",
            "optionen": ["Schwarz", "Weiß", "Rot", "Blau"],
            "richtig": "Rot"
        }
    },
    "Heilige Tiere": {
        "tier1": {
            "frage": "Welches Tier wird als Reittier (Vahana) von Lord Shiva betrachtet?",
            "optionen": ["Elefant", "Stier Nandi", "Pfau", "Löwe"],
            "richtig": "Stier Nandi"
        },
        "tier2": {
            "frage": "Welches Tier wird mit Lord Ganesha in Verbindung gebracht?",
            "optionen": ["Maus", "Schlange", "Affe", "Tiger"],
            "richtig": "Maus"
        },
        "tier3": {
            "frage": "Welches Tier gilt als heilig und wird als 'Mutter' verehrt?",
            "optionen": ["Schaf", "Kuh", "Ziege", "Pferd"],
            "richtig": "Kuh"
        }
    }
}

# Kombiniertes Quiz
QUIZZES["Kombiniert"] = {**QUIZZES["Kleidung"], **QUIZZES["Heilige Tiere"]}

# ---------------- Antworten laden/speichern ----------------
def load_answers():
    if not os.path.exists(ANSWERS_FILE):
        return []
    answers = []
    try:
        with open(ANSWERS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        answers.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        print(f"Fehler beim Laden der Antworten: {e}")
    return answers

def save_answer(entry: dict):
    os.makedirs(os.path.dirname(ANSWERS_FILE), exist_ok=True)
    answers = load_answers()
    if "timestamp" not in entry:
        entry["timestamp"] = datetime.utcnow().isoformat() + "Z"
    answers.append(entry)
    try:
        with open(ANSWERS_FILE, "w", encoding="utf-8") as f:
            for ans in answers:
                f.write(json.dumps(ans, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Fehler beim Speichern der Antwort: {e}")

# ---------------- Quiz-Funktionen ----------------
def get_random_question(quiz_name: str):
    if quiz_name not in QUIZZES:
        return None, None
    quiz = QUIZZES[quiz_name]
    question_id = random.choice(list(quiz.keys()))
    question = quiz[question_id]
    options = question["optionen"].copy()
    random.shuffle(options)
    question["optionen"] = options
    return question_id, question

def calculate_quiz_stats(quiz_name: str = None):
    entries = load_answers()
    stats = {
        "total_answers": 0,
        "total_users": 0,
        "quiz_scores": {},
        "user_scores": {}
    }
    users = set()
    for entry in entries:
        if quiz_name and entry.get("quiz") != quiz_name:
            continue
        stats["total_answers"] += 1
        users.add(entry.get("username", "Unbekannt"))
        quiz = entry.get("quiz", "Unbekannt")
        if quiz not in stats["quiz_scores"]:
            stats["quiz_scores"][quiz] = {"total": 0, "correct": 0}
        stats["quiz_scores"][quiz]["total"] += 1
        if entry.get("correct", False):
            stats["quiz_scores"][quiz]["correct"] += 1
        username = entry.get("username", "Unbekannt")
        if username not in stats["user_scores"]:
            stats["user_scores"][username] = {"total": 0, "correct": 0}
        stats["user_scores"][username]["total"] += 1
        if entry.get("correct", False):
            stats["user_scores"][username]["correct"] += 1
    stats["total_users"] = len(users)
    return stats

# ---------------- Streamlit Quiz-Anzeige ----------------
def show_quiz(username: str):
    st.header(f"Quiz für {username}")
    quiz_names = list(QUIZZES.keys())
    choice = st.selectbox("📚 Quiz auswählen", quiz_names)

    if "quiz_step" not in st.session_state or st.session_state.get("current_quiz") != choice:
        st.session_state["quiz_step"] = 0
        st.session_state["current_quiz"] = choice
        st.session_state["answered_questions"] = set()
        st.session_state["quiz_start_time"] = datetime.utcnow()
        st.session_state["show_results"] = False

    quiz = QUIZZES[choice]
    questions = list(quiz.values())
    idx = st.session_state["quiz_step"]

    if idx < len(questions):
        question = questions[idx]
        st.subheader(f"Frage {idx+1}: {question['frage']}")
        answer = st.radio("Antwort wählen", question["optionen"])
        if st.button("▶ Weiter"):
            if not answer:
                st.warning("Bitte wähle eine Antwort aus!")
            else:
                qid = f"{choice}_{idx}"
                if qid not in st.session_state["answered_questions"]:
                    save_answer({
                        "username": username,
                        "quiz": choice,
                        "question": question["frage"],
                        "answer": answer,
                        "correct": answer == question["richtig"]
                    })
                    st.session_state["answered_questions"].add(qid)
                st.session_state["quiz_step"] += 1
                st.experimental_rerun()
    else:
        st.success("🎉 Quiz abgeschlossen!")
        st.balloons()
        stats = calculate_quiz_stats(choice)
        user_score = stats["user_scores"].get(username, {"correct": 0, "total": 0})
        st.write(f"Richtige Antworten: {user_score['correct']} / {user_score['total']}")
        st.write("### Bestenliste")
        leaderboard = sorted(stats["user_scores"].items(), key=lambda x: x[1]["correct"], reverse=True)
        for rank, (user, score) in enumerate(leaderboard, 1):
            st.write(f"{rank}. {user} – {score['correct']} / {score['total']}")
        if st.button("Quiz neu starten"):
            st.session_state["quiz_step"] = 0
            st.session_state["answered_questions"] = set()
            st.session_state["show_results"] = False
            st.experimental_rerun()
