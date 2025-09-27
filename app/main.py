import streamlit as st
import json
import os
import random
import requests
from datetime import datetime
from typing import List, Dict, Any
from streamlit.components.v1 import html
from user_management import authenticate_user, load_users
import admin  # dein admin.py mit show_admin_panel()
from quizzes import load_answers   # dein quiz.py mit show_quiz()
from admin import show_admin_panel

API_URL = "https://quiz-rel/api"

try:
    from user_management import authenticate_user, change_password, is_user_active
except Exception:
    def authenticate_user(u, p):
        return False, "Lokales Dev-User-System nicht verfügbar.", False
    def change_password(u, old, new):
        return False, "User-Management nicht implementiert."
    def is_user_active(u):
        return True

try:
    from admin import show_admin_panel
except Exception:
    def show_admin_panel():
        st.info("Admin-Panel nicht verfügbar (Dev-Fallback).")

try:
    from quizzes import QUIZZES, save_answer as quizzes_save_answer, load_answers as quizzes_load_answers
except Exception:
    QUIZZES = {
        "Beispiel-Quiz": {
            "q1": {"frage": "Was ist 2+2?", "optionen": ["3", "4", "5"], "richtig": "4"},
            "q2": {"frage": "Farbe des Himmels?", "optionen": ["Blau", "Grün"], "richtig": "Blau"}
        }
    }
    _DATA_DIR = os.path.join(os.getcwd(), "data")
    os.makedirs(_DATA_DIR, exist_ok=True)
    _ANSWERS_FILE = os.path.join(_DATA_DIR, "answers.json")

    def quizzes_load_answers() -> List[Dict[str, Any]]:
        if not os.path.exists(_ANSWERS_FILE):
            return []
        try:
            with open(_ANSWERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def quizzes_save_answer(entry: Dict[str, Any]):
        answers = quizzes_load_answers()
        answers.append(entry)
        with open(_ANSWERS_FILE, "w", encoding="utf-8") as f:
            json.dump(answers, f, ensure_ascii=False, indent=2)

DATA_DIR = "/workspaces/learn-web-development-with-streamlit/data"
ANSWERS_FILE = os.path.join(DATA_DIR, "answers.json")
BAD_WORDS_FILE = os.path.join(DATA_DIR, "bad_words.txt")
os.makedirs(DATA_DIR, exist_ok=True)

def safe_rerun():
    try:
        st.experimental_rerun()
    except Exception:
        try:
            st.rerun()
        except Exception:
            pass

def load_answers() -> List[Dict[str, Any]]:
    try:
        r = requests.get(API_URL)
        return r.json()
    except Exception:
        return []

def save_answer(entry: Dict[str, Any]):
    try:
        requests.post(API_URL, json=entry)
    except Exception as e:
        st.error(f"Fehler beim Speichern: {e}")


def load_bad_words() -> List[str]:
    if not os.path.exists(BAD_WORDS_FILE):
        return []
    try:
        with open(BAD_WORDS_FILE, "r", encoding="utf-8") as f:
            return [w.strip().lower() for w in f if w.strip()]
    except Exception:
        return []

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

def login_page():
    st.title("Willkommen zum Quiz")
    username = st.text_input("Benutzername", key="username_input")
    password = st.text_input("Passwort", type="password", key="password_input")
    if st.button("Login"):
        if not username or not password:
            st.warning("Bitte Benutzername und Passwort eingeben")
            return
        success, message, needs_pw_change = authenticate_user(username.strip(), password)
        if success:
            if not is_user_active(username):
                st.error("Du wurdest vom System geblockt!")
                for k in DEFAULT_KEYS:
                    st.session_state[k] = DEFAULT_KEYS[k]
                return
            st.session_state.authentifiziert = True
            st.session_state.username = username.strip()
            st.session_state.passwort = password
            st.session_state.needs_password_change = needs_pw_change
            st.session_state.is_admin = username.lower() == "admin"
            st.success(message)
            safe_rerun()
        else:
            st.error(message)

def password_change_page():
    st.warning("Sie müssen Ihr Passwort ändern")
    new_pw = st.text_input("Neues Passwort", type="password", key="new_pw_input")
    confirm_pw = st.text_input("Passwort bestätigen", type="password", key="confirm_pw_input")
    if st.button("Passwort ändern"):
        if new_pw != confirm_pw:
            st.error("Passwörter stimmen nicht überein")
            return
        if len(new_pw) < 6:
            st.error("Passwort muss mindestens 6 Zeichen lang sein")
            return
        success, msg = change_password(st.session_state.username, st.session_state.passwort, new_pw)
        if success:
            st.success(msg)
            st.session_state.passwort = new_pw
            st.session_state.needs_password_change = False
            safe_rerun()
        else:
            st.error(msg)

def leaderboard():
    st.subheader("🏆 Bestenliste")
    answers = load_answers()
    if not answers:
        st.info("Noch keine Daten vorhanden.")
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
    for i, (user, s) in enumerate(ranking, 1):
        rate = (s["correct"]/s["total"]*100) if s["total"] else 0
        st.markdown(f"{i}. **{user}** — {s['correct']}/{s['total']} richtig ({rate:.1f}%)")

def quiz_page():
    with st.sidebar:
        st.markdown("### Einstellungen")
        bg1 = st.color_picker("Hintergrundfarbe 1", "#1e3c72")
        bg2 = st.color_picker("Hintergrundfarbe 2", "#2a5298")
        if st.button("Abmelden", key="logout_button"):
            for k in DEFAULT_KEYS:
                st.session_state[k] = DEFAULT_KEYS[k]
            safe_rerun()

    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(-45deg, {bg1}, {bg2}, {bg2}, {bg1});
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
        }}
        @keyframes gradientBG {{
            0% {{background-position:0% 50%}}
            50% {{background-position:100% 50%}}
            100% {{background-position:0% 50%}}
        }}
        </style>
    """, unsafe_allow_html=True)

    st.header(f"Quiz-Plattform — Angemeldet: {st.session_state.username}")
    quiz_names = list(QUIZZES.keys())
    if not quiz_names:
        st.error("Keine Quiz verfügbar.")
        return
    choice = st.selectbox("Quiz auswählen", quiz_names, index=quiz_names.index(st.session_state.current_quiz) if st.session_state.current_quiz in quiz_names else 0)

    if st.session_state.current_quiz != choice:
        st.session_state.current_quiz = choice
        st.session_state.quiz_step = 0
        st.session_state.quiz_start_time = datetime.utcnow().isoformat()
        st.session_state.show_results = False
        st.session_state.answered_questions = []

    quiz = QUIZZES[choice]
    questions = list(quiz.values())
    idx = int(st.session_state.quiz_step) if str(st.session_state.quiz_step).isdigit() else 0
    idx = max(0, min(idx, len(questions)-1))
    question = questions[idx]

    st.progress((idx+1)/len(questions))
    st.subheader(f"Frage {idx+1} von {len(questions)}")
    st.write(f"**{question['frage']}**")
    answer = st.radio("", question.get("optionen", []), key=f"answer_{idx}")

    if st.button("Weiter", key=f"next_{idx}"):
        if not answer:
            st.warning("Bitte wähle eine Antwort aus")
        else:
            bad_words = load_bad_words()
            if any(bw in answer.lower() for bw in bad_words):
                fake_ip = f"192.168.{random.randint(1,255)}.{random.randint(1,255)}"
                st.error(f"Unangemessene Sprache erkannt. IP: {fake_ip}")
                return
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
                try:
                    quizzes_save_answer(entry)
                except Exception:
                    save_answer(entry)
                st.session_state.answered_questions.append(question_id)
            if idx < len(questions)-1:
                st.session_state.quiz_step = idx+1
                safe_rerun()
            else:
                st.session_state.show_results = True
                st.session_state.quiz_duration = datetime.utcnow() - datetime.fromisoformat(st.session_state.quiz_start_time)
                safe_rerun()

    if st.session_state.show_results:
        st.success("Quiz abgeschlossen!")
        answers = load_answers()
        quiz_answers = [a for a in answers if a.get("username")==st.session_state.username and a.get("quiz")==choice]
        if quiz_answers:
            correct = len([a for a in quiz_answers if a.get("correct")])
            total = len(quiz_answers)
            st.metric("Richtige Antworten", f"{correct}/{total}")
            st.metric("Erfolgsquote", f"{(correct/total)*100:.1f}%")
            if st.session_state.get("quiz_duration"):
                st.metric("Zeit", f"{st.session_state.quiz_duration.total_seconds()/60:.1f} Minuten")
            st.markdown("### Deine Antworten")
            for i, a in enumerate(quiz_answers, 1):
                status = "✅" if a.get("correct") else "❌"
                st.markdown(f"**Frage {i}:** {a.get('question')}  \
Deine Antwort: {a.get('answer')} {status}")
        if st.button("Quiz neu starten", key="restart_quiz"):
            st.session_state.quiz_step = 0
            st.session_state.quiz_start_time = datetime.utcnow().isoformat()
            st.session_state.show_results = False
            st.session_state.answered_questions = []
            safe_rerun()
        leaderboard()

def main():
    if not st.session_state.authentifiziert:
        login_page()
    elif st.session_state.needs_password_change:
        password_change_page()
    else:
        if st.session_state.is_admin:
            show_admin_panel()
        else:
            # Prüfen, ob Benutzer geblockt ist
            if not is_user_active(st.session_state.username):
                st.error("Du wurdest geblockt und wirst ausgeloggt.")
                for k in DEFAULT_KEYS:
                    st.session_state[k] = DEFAULT_KEYS[k]
                return
            quiz_page()


if __name__ == "__main__":
    main()
