import streamlit as st
import json
import random
import requests
from datetime import datetime
from typing import List, Dict, Any
from user_management import load_users, save_users, hash_password, load_answers

# === API ENDPOINT ===
API_URL = "https://quiz-rel.onrender.com/api/answers"   

# === SAFE IMPORTS ===
try:
    from user_management import authenticate_user, change_password, is_user_active
except Exception:
    def authenticate_user(u, p): return True, "Login erfolgreich (Dev-Fallback).", False
    def change_password(u, old, new): return True, "Passwort geändert (Dev-Fallback)."
    def is_user_active(u): return True

from admin import show_admin_panel

try:
    from quizzes import QUIZZES
except Exception:
    QUIZZES = {
        "Beispiel-Quiz": {
            "q1": {"frage": "Was ist 2+2?", "optionen": ["3", "4", "5"], "richtig": "4"},
            "q2": {"frage": "Farbe des Himmels?", "optionen": ["Blau", "Grün"], "richtig": "Blau"}
        }
    }

# === API-FUNKTIONEN ===
def load_answers() -> List[Dict[str, Any]]:
    try:
        r = requests.get(API_URL, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        st.error(f"Fehler beim Laden: {e}")
    return []

def save_answer(entry: Dict[str, Any]):
    try:
        r = requests.post(API_URL, json=entry, timeout=5)
        if r.status_code != 200:
            st.error(f"Fehler beim Speichern: {r.text}")
    except Exception as e:
        st.error(f"Fehler beim Speichern: {e}")

# === STYLING ===
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        color: white;
    }
    .stButton>button {
        border-radius: 12px;
        background-color: #4CAF50;
        color: white;
        padding: 0.6em 1.2em;
        font-weight: bold;
    }
    .stProgress .st-bo {
        background-color: #FFD700 !important;
    }
    .stMetric {
        background: rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 10px;
    }
    .quiz-card {
        background: rgba(255,255,255,0.15);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# === SESSION DEFAULTS ===
DEFAULT_KEYS = {
    "authentifiziert": False,
    "username": "",
    "passwort": "",
    "is_admin": False,
    "needs_password_change": False,
    "quiz_step": 0,
    "current_quiz": "",
    "quiz_start_time": None,
    "show_results": False,
    "answered_questions": []
}
for k, v in DEFAULT_KEYS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# === LEADERBOARD ===
def leaderboard(sidebar=False):
    answers = load_answers()
    if not answers:
        if sidebar: st.sidebar.info("Noch keine Daten vorhanden.")
        else: st.info("Noch keine Daten vorhanden.")
        return
    scores = {}
    for a in answers:
        user = a.get("username")
        if user not in scores:
            scores[user] = {"correct": 0, "total": 0}
        scores[user]["total"] += 1
        if a.get("correct"):
            scores[user]["correct"] += 1
    ranking = sorted(scores.items(), key=lambda x: (x[1]["correct"]/(x[1]["total"] or 1)), reverse=True)
    if sidebar:
        st.sidebar.subheader("🏆 Bestenliste")
        for i, (user, s) in enumerate(ranking, 1):
            rate = (s["correct"]/s["total"]*100) if s["total"] else 0
            st.sidebar.write(f"{i}. **{user}** — {s['correct']}/{s['total']} ({rate:.0f}%)")
    else:
        st.subheader("🏆 Bestenliste")
        for i, (user, s) in enumerate(ranking, 1):
            rate = (s["correct"]/s["total"]*100) if s["total"] else 0
            st.markdown(f"{i}. **{user}** — {s['correct']}/{s['total']} ({rate:.0f}%)")

# === LOGIN ===
def login_page():
    st.title("🎮 Willkommen zum Quiz")
    username = st.text_input("Benutzername", key="username_input")
    password = st.text_input("Passwort", type="password", key="password_input")
    if st.button("Login"):
        if not username or not password:
            st.warning("Bitte Benutzername und Passwort eingeben")
            return
        if len(password) < 6:
            st.warning("Passwort muss mindestens 6 zeichen haben")
            return
        success, message, needs_pw_change = authenticate_user(username.strip(), password)
        if success:
            if not is_user_active(username):
                st.error("Du wurdest geblockt!")
                for k in DEFAULT_KEYS:
                    st.session_state[k] = DEFAULT_KEYS[k]
                return
            st.session_state.authentifiziert = True
            st.session_state.username = username.strip()
            st.session_state.passwort = password
            st.session_state.needs_password_change = needs_pw_change
            st.session_state.is_admin = username.lower() == "admin"
            st.success(message)
            st.rerun()
        else:
            st.error(message)

# === QUIZ ===
def quiz_page():
    with st.sidebar:
        if st.button("Abmelden"):
            for k in DEFAULT_KEYS:
                st.session_state[k] = DEFAULT_KEYS[k]
            st.rerun()
        leaderboard(sidebar=True)

    st.header(f"📘 Quiz-Plattform — Angemeldet: {st.session_state.username}")
    quiz_names = list(QUIZZES.keys())
    if not quiz_names:
        st.error("Keine Quiz verfügbar.")
        return
    choice = st.selectbox("Quiz auswählen", quiz_names)

    if st.session_state.current_quiz != choice:
        st.session_state.current_quiz = choice
        st.session_state.quiz_step = 0
        st.session_state.quiz_start_time = datetime.utcnow().isoformat()
        st.session_state.show_results = False
        st.session_state.answered_questions = []

    quiz = QUIZZES[choice]
    questions = list(quiz.values())
    idx = st.session_state.quiz_step
    idx = max(0, min(idx, len(questions)-1))
    question = questions[idx]

    st.progress((idx+1)/len(questions))
    st.markdown(f"<div class='quiz-card'><h4>Frage {idx+1} von {len(questions)}</h4><p><b>{question['frage']}</b></p></div>", unsafe_allow_html=True)
    answer = st.radio("Antwort auswählen:", question.get("optionen", []), key=f"answer_{idx}")

    if st.button(" Weiter"):
        if not answer:
            st.warning("Bitte wähle eine Antwort aus")
        else:
            question_id = f"{choice}_{idx}"
            if question_id not in st.session_state.answered_questions:
                entry = {
                    "timestamp": datetime.utcnow().isoformat()+"Z",
                    "username": st.session_state.username,
                    "quiz": choice,
                    "question": question.get("frage"),
                    "answer": answer,
                    "correct": answer == question.get("richtig")
                }
                save_answer(entry)
                st.session_state.answered_questions.append(question_id)
            if idx < len(questions)-1:
                st.session_state.quiz_step = idx+1
                st.rerun()
            else:
                st.session_state.show_results = True
                st.session_state.quiz_duration = datetime.utcnow() - datetime.fromisoformat(st.session_state.quiz_start_time)
                st.rerun()

    if st.session_state.show_results:
        st.success(" Quiz abgeschlossen!")
        answers = load_answers()
        quiz_answers = [a for a in answers if a.get("username")==st.session_state.username and a.get("quiz")==choice]
        if quiz_answers:
            correct = len([a for a in quiz_answers if a.get("correct")])
            total = len(quiz_answers)
            st.metric("Richtige Antworten", f"{correct}/{total}")
            st.metric("Erfolgsquote", f"{(correct/total)*100:.1f}%")
            leaderboard()

# === MAIN ===
def main():
    if not st.session_state.authentifiziert:
        login_page()
    elif st.session_state.needs_password_change:
        st.warning("🔑 Passwort ändern erforderlich")
        # Passwort-Änderung kannst du identisch wie vorher lassen
    else:
        if st.session_state.is_admin:
            show_admin_panel()
        else:
            if not is_user_active(st.session_state.username):
                st.error("Du wurdest geblockt und wirst ausgeloggt.")
                for k in DEFAULT_KEYS:
                    st.session_state[k] = DEFAULT_KEYS[k]
                return
            quiz_page()

if __name__ == "__main__":
    main()
