import streamlit as st
import json
import os
import time
from datetime import datetime
from random import shuffle

# ==============================
#   KONFIGURATION
# ==============================
QUIZ_DIR = "./data/quizzes"
ANSWERS_DIR = "./data/answers"

# ==============================
#   QUIZ LADE-FUNKTIONEN
# ==============================
def load_quizzes():
    if not os.path.exists(QUIZ_DIR):
        os.makedirs(QUIZ_DIR)
    quizzes = []
    for file in os.listdir(QUIZ_DIR):
        if file.endswith(".json"):
            with open(os.path.join(QUIZ_DIR, file), "r", encoding="utf-8") as f:
                data = json.load(f)
                quizzes.append(data)
    return quizzes

def load_user_answers(username):
    os.makedirs(ANSWERS_DIR, exist_ok=True)
    filepath = os.path.join(ANSWERS_DIR, f"{username}.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"quizzes": []}

def save_user_answers(username, quiz_data):
    os.makedirs(ANSWERS_DIR, exist_ok=True)
    filepath = os.path.join(ANSWERS_DIR, f"{username}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(quiz_data, f, indent=2, ensure_ascii=False)

# ==============================
#   QUIZ SEITE
# ==============================
def show_quiz():
    st.markdown("""
        <style>
        .quiz-card {
            background: rgba(255,255,255,0.05);
            border-radius: 1.5rem;
            padding: 1.2rem;
            margin: 0.8rem 0;
            text-align: center;
            transition: all 0.25s ease-in-out;
            cursor: pointer;
            border: 2px solid rgba(255,255,255,0.1);
        }
        .quiz-card:hover {
            background: rgba(255,255,255,0.15);
            transform: scale(1.03);
            border-color: rgba(255,255,255,0.4);
        }
        .quiz-card-selected {
            background: rgba(0,200,100,0.2);
            border-color: rgba(0,255,150,0.8);
            transform: scale(1.04);
        }
        .question-box {
            background: linear-gradient(135deg, #111, #222);
            border-radius: 2rem;
            padding: 2rem;
            box-shadow: 0 0 25px rgba(0,0,0,0.3);
        }
        </style>
    """, unsafe_allow_html=True)

    if "username" not in st.session_state or not st.session_state.username.strip():
        st.warning("Bitte zuerst anmelden!")
        st.stop()

    username = st.session_state.username
    quizzes = load_quizzes()

    if not quizzes:
        st.info("📂 Noch keine Quizze vorhanden.")
        return

    # Quiz-Auswahl
    quiz_names = [quiz["title"] for quiz in quizzes]
    selected_quiz = st.selectbox("🎯 Wähle dein Quiz", quiz_names)
    current_quiz = next(q for q in quizzes if q["title"] == selected_quiz)

    # Quiz starten
    if st.button("🚀 Quiz starten", use_container_width=True):
        st.session_state.current_quiz = current_quiz
        st.session_state.quiz_index = 0
        st.session_state.quiz_answers = []
        st.session_state.quiz_start_time = time.time()
        st.rerun()

    # Wenn Quiz läuft
    if "current_quiz" in st.session_state:
        quiz = st.session_state.current_quiz
        index = st.session_state.quiz_index
        total_questions = len(quiz["questions"])
        current_question = quiz["questions"][index]

        st.markdown(f"### Frage {index + 1} / {total_questions}")
        st.markdown(f"<div class='question-box'><h3>{current_question['question']}</h3></div>", unsafe_allow_html=True)
        
        options = current_question["options"]
        shuffle(options)

        selected = st.session_state.get("selected_answer", None)
        cols = st.columns(2)

        for i, option in enumerate(options):
            col = cols[i % 2]
            with col:
                if st.button(option, key=f"opt_{i}", use_container_width=True):
                    st.session_state.selected_answer = option
                    st.session_state.quiz_answers.append({
                        "question": current_question["question"],
                        "selected": option,
                        "correct": current_question["answer"]
                    })
                    if index + 1 < total_questions:
                        st.session_state.quiz_index += 1
                    else:
                        end_time = time.time()
                        duration = round(end_time - st.session_state.quiz_start_time, 2)
                        correct_count = sum(1 for a in st.session_state.quiz_answers if a["selected"] == a["correct"])
                        
                        user_data = load_user_answers(username)
                        user_data["quizzes"].append({
                            "quiz_name": quiz["title"],
                            "correct": correct_count,
                            "total": total_questions,
                            "time_seconds": duration,
                            "timestamp": datetime.now().isoformat()
                        })
                        save_user_answers(username, user_data)

                        st.session_state.last_result = {
                            "correct": correct_count,
                            "total": total_questions,
                            "time_seconds": duration
                        }
                        # Quiz beenden
                        for k in ["current_quiz", "quiz_index", "quiz_answers", "quiz_start_time"]:
                            st.session_state.pop(k, None)
                    st.rerun()

    # Ergebnisse anzeigen
    if "last_result" in st.session_state:
        res = st.session_state.last_result
        st.markdown("""
        <div style='text-align:center;padding:2rem;background:linear-gradient(135deg,#222,#111);
        border-radius:2rem;margin-top:2rem;'>
            <h2>🎉 Quiz beendet!</h2>
            <h3>{}/{} richtig</h3>
            <p>⏱️ Dauer: {} Sekunden</p>
        </div>
        """.format(res["correct"], res["total"], res["time_seconds"]), unsafe_allow_html=True)

        if st.button("🔁 Nochmal spielen", use_container_width=True):
            del st.session_state["last_result"]
            st.rerun()
