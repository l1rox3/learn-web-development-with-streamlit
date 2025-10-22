import streamlit as st
import json
import os
import random
import time
from datetime import datetime
from pages.auth import AuthManager

# =========================================================
# KONFIGURATION
# =========================================================
ANSWERS_DIR = "./data/answers"
QUIZZES_DIR = "./data/quizzes"

st.set_page_config(page_title="Quiz", page_icon="🧩", layout="wide")

# =========================================================
# INITIALISIERUNG
# =========================================================
if "auth_manager" not in st.session_state:
    st.session_state.auth_manager = AuthManager()
auth_manager = st.session_state.auth_manager

if "username" not in st.session_state or not st.session_state.username:
    st.warning("Bitte melde dich zuerst an, um ein Quiz zu starten.")
    st.stop()

username = st.session_state.username

# =========================================================
# FUNKTIONEN
# =========================================================

def load_quizzes():
    """Lädt verfügbare Quizze aus JSON-Dateien."""
    if not os.path.exists(QUIZZES_DIR):
        os.makedirs(QUIZZES_DIR)
        return []
    files = [f for f in os.listdir(QUIZZES_DIR) if f.endswith(".json")]
    quizzes = []
    for f in files:
        with open(os.path.join(QUIZZES_DIR, f), "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                quizzes.append(data)
            except Exception as e:
                print(f"Fehler in {f}: {e}")
    return quizzes


def save_result(username, quiz_name, correct, total, time_seconds):
    """Speichert die Ergebnisse des Benutzers."""
    os.makedirs(ANSWERS_DIR, exist_ok=True)
    path = os.path.join(ANSWERS_DIR, f"{username}.json")
    data = {"quizzes": []}

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                pass

    if "quizzes" not in data:
        data["quizzes"] = []

    data["quizzes"].append({
        "quiz_name": quiz_name,
        "correct": correct,
        "total": total,
        "time_seconds": round(time_seconds, 2),
        "timestamp": datetime.now().isoformat()
    })

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def render_quiz(quiz):
    """Zeigt das Quiz interaktiv an."""
    st.markdown(f"<h1 style='text-align:center;'>{quiz['title']}</h1>", unsafe_allow_html=True)
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    questions = quiz["questions"]
    random.shuffle(questions)

    score = 0
    start_time = time.time()

    for i, q in enumerate(questions, start=1):
        st.markdown(f"<h3>{i}. {q['question']}</h3>", unsafe_allow_html=True)

        # Große, klickbare Antwortboxen
        cols = st.columns(2)
        random.shuffle(q["options"])
        selected = None

        for idx, opt in enumerate(q["options"]):
            col = cols[idx % 2]
            with col:
                key = f"{i}-{opt}"
                # große Karte
                if st.button(opt, key=key, use_container_width=True):
                    selected = opt
                    if "selected_answer" not in st.session_state:
                        st.session_state.selected_answer = {}
                    st.session_state.selected_answer[i] = opt
                    st.rerun()

        # Wenn Antwort schon gewählt
        if "selected_answer" in st.session_state and i in st.session_state.selected_answer:
            chosen = st.session_state.selected_answer[i]
            correct = q["answer"]
            if chosen == correct:
                st.success(f"✅ {chosen} – Richtig!")
                score += 1
            else:
                st.error(f"❌ {chosen} – Falsch! Richtige Antwort: **{correct}**")

        st.markdown("<hr>", unsafe_allow_html=True)
        time.sleep(0.05)

    end_time = time.time()
    total_time = end_time - start_time

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align:center;'>Ergebnis</h2>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='text-align:center; font-size: 1.5rem; background: #111; padding: 1rem; border-radius: 1rem;'>"
        f"Punkte: <b>{score}</b> / {len(questions)}<br>"
        f"Zeit: <b>{round(total_time, 1)} Sekunden</b>"
        "</div>",
        unsafe_allow_html=True,
    )

    save_result(username, quiz["title"], score, len(questions), total_time)


# =========================================================
# HAUPTBEREICH
# =========================================================

st.markdown("""
<style>
    div[data-testid="stButton"] button {
        font-size: 1.2rem !important;
        padding: 1.2rem !important;
        border-radius: 1rem !important;
        margin: 0.5rem 0 !important;
        transition: 0.2s ease-in-out;
    }
    div[data-testid="stButton"] button:hover {
        transform: scale(1.02);
        background: linear-gradient(90deg, #1e90ff, #00bfff);
        color: white !important;
        box-shadow: 0 0 15px rgba(30,144,255,0.5);
    }
    h1, h2, h3 {
        text-align: center !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎯 Wähle ein Quiz")

quizzes = load_quizzes()
if not quizzes:
    st.warning("Noch keine Quizze gefunden. Lege im Ordner `/data/quizzes` JSON-Dateien an.")
    st.stop()

quiz_titles = [q["title"] for q in quizzes]
selected_quiz = st.selectbox("Quiz auswählen:", quiz_titles, index=0)

quiz = next(q for q in quizzes if q["title"] == selected_quiz)

if st.button("🚀 Quiz starten", use_container_width=True, type="primary"):
    st.session_state.selected_answer = {}
    st.session_state.current_quiz = quiz
    st.rerun()

if "current_quiz" in st.session_state and st.session_state.current_quiz:
    render_quiz(st.session_state.current_quiz)
