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
# AUTH CHECK
# =========================================================
if "auth_manager" not in st.session_state:
    st.session_state.auth_manager = AuthManager()
auth_manager = st.session_state.auth_manager

if "username" in st.session_state and st.session_state.username.strip():
    status = auth_manager.check_user_status(st.session_state.username)
    
    if status["should_logout"]:
        st.error(f"🔒 {status['message']}")
        st.warning("Du wurdest automatisch ausgeloggt.")
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        time.sleep(2)
        st.rerun()

if "username" not in st.session_state or not st.session_state.username:
    st.warning("Bitte melde dich zuerst an, um ein Quiz zu starten.")
    st.stop()

username = st.session_state.username

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>
    /* Haupt-Container */
    .main {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    
    /* Quiz Header */
    .quiz-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .quiz-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: white;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Progress Bar */
    .progress-container {
        background: rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .progress-bar {
        height: 12px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        transition: width 0.3s ease;
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.5);
    }
    
    .progress-text {
        color: white;
        font-size: 1.1rem;
        margin-top: 0.5rem;
        font-weight: 600;
    }
    
    /* Question Card */
    .question-card {
        background: rgba(255,255,255,0.05);
        border-radius: 20px;
        padding: 2.5rem;
        margin: 2rem 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    }
    
    .question-number {
        color: #667eea;
        font-size: 1rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 1rem;
    }
    
    .question-text {
        color: white;
        font-size: 1.8rem;
        font-weight: 600;
        line-height: 1.4;
        margin-bottom: 2rem;
    }
    
    /* Answer Buttons */
    div[data-testid="stButton"] button {
        font-size: 1.1rem !important;
        padding: 1.5rem 2rem !important;
        border-radius: 15px !important;
        margin: 0.5rem 0 !important;
        transition: all 0.3s ease !important;
        background: rgba(255,255,255,0.08) !important;
        border: 2px solid rgba(255,255,255,0.2) !important;
        color: white !important;
        font-weight: 600 !important;
        text-align: left !important;
    }
    
    div[data-testid="stButton"] button:hover {
        transform: translateY(-3px) !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border-color: #667eea !important;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Result Card */
    .result-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 25px;
        padding: 3rem;
        text-align: center;
        margin: 3rem 0;
        box-shadow: 0 15px 50px rgba(0,0,0,0.4);
    }
    
    .result-score {
        font-size: 4rem;
        font-weight: 800;
        color: white;
        margin: 1rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .result-text {
        font-size: 1.3rem;
        color: rgba(255,255,255,0.9);
        margin: 0.5rem 0;
    }
    
    /* Feedback */
    .feedback-correct {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        font-size: 1.2rem;
        margin: 1rem 0;
        font-weight: 600;
        box-shadow: 0 5px 20px rgba(17, 153, 142, 0.4);
    }
    
    .feedback-wrong {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        font-size: 1.2rem;
        margin: 1rem 0;
        font-weight: 600;
        box-shadow: 0 5px 20px rgba(235, 51, 73, 0.4);
    }
    
    /* Timer */
    .timer-display {
        background: rgba(255,255,255,0.1);
        padding: 1rem 2rem;
        border-radius: 15px;
        color: white;
        font-size: 1.3rem;
        font-weight: 700;
        text-align: center;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* Quiz Selection */
    .quiz-select-card {
        background: rgba(255,255,255,0.05);
        padding: 2rem;
        border-radius: 20px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

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


def initialize_quiz_session(quiz):
    """Initialisiert eine neue Quiz-Session."""
    questions = quiz["questions"].copy()
    random.shuffle(questions)
    
    st.session_state.quiz_active = True
    st.session_state.quiz_questions = questions
    st.session_state.current_question_idx = 0
    st.session_state.quiz_score = 0
    st.session_state.quiz_answers = []
    st.session_state.quiz_start_time = time.time()
    st.session_state.answered_current = False


def render_progress_bar(current, total):
    """Zeigt eine Fortschrittsanzeige."""
    progress = (current / total) * 100
    st.markdown(f"""
    <div class="progress-container">
        <div style="background: rgba(255,255,255,0.2); border-radius: 10px; overflow: hidden;">
            <div class="progress-bar" style="width: {progress}%;"></div>
        </div>
        <div class="progress-text">
            Frage {current} von {total} | {int(progress)}% abgeschlossen
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_current_question():
    """Zeigt die aktuelle Frage an."""
    idx = st.session_state.current_question_idx
    questions = st.session_state.quiz_questions
    
    if idx >= len(questions):
        render_quiz_results()
        return
    
    question = questions[idx]
    total = len(questions)
    
    # Progress Bar
    render_progress_bar(idx + 1, total)
    
    # Question Card
    st.markdown(f"""
    <div class="question-card">
        <div class="question-number">Frage {idx + 1} von {total}</div>
        <div class="question-text">{question['question']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Answer Options
    if not st.session_state.answered_current:
        options = question["options"].copy()
        random.shuffle(options)
        
        st.markdown("<div style='margin: 2rem 0;'>", unsafe_allow_html=True)
        cols = st.columns(2)
        
        for i, option in enumerate(options):
            col = cols[i % 2]
            with col:
                if st.button(f"🔹 {option}", key=f"opt_{idx}_{i}", use_container_width=True):
                    st.session_state.selected_answer = option
                    st.session_state.answered_current = True
                    
                    # Check answer
                    is_correct = option == question["answer"]
                    if is_correct:
                        st.session_state.quiz_score += 1
                    
                    st.session_state.quiz_answers.append({
                        "question": question["question"],
                        "selected": option,
                        "correct": question["answer"],
                        "is_correct": is_correct
                    })
                    
                    st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    else:
        # Show feedback
        answer = st.session_state.quiz_answers[-1]
        
        if answer["is_correct"]:
            st.markdown(f"""
            <div class="feedback-correct">
                ✅ Richtig! "{answer['selected']}" ist die korrekte Antwort!
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="feedback-wrong">
                ❌ Leider falsch! Du hast "{answer['selected']}" gewählt.<br>
                Die richtige Antwort ist: <strong>"{answer['correct']}"</strong>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin: 2rem 0;'>", unsafe_allow_html=True)
        
        if st.session_state.current_question_idx < len(st.session_state.quiz_questions) - 1:
            if st.button("➡️ Nächste Frage", use_container_width=True, type="primary"):
                st.session_state.current_question_idx += 1
                st.session_state.answered_current = False
                st.rerun()
        else:
            if st.button("🏁 Quiz beenden", use_container_width=True, type="primary"):
                st.session_state.current_question_idx += 1
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)


def render_quiz_results():
    """Zeigt die Endergebnisse an."""
    score = st.session_state.quiz_score
    total = len(st.session_state.quiz_questions)
    time_taken = time.time() - st.session_state.quiz_start_time
    percentage = (score / total) * 100
    
    # Save result
    save_result(
        username,
        st.session_state.current_quiz["title"],
        score,
        total,
        time_taken
    )
    
    # Result display
    st.markdown(f"""
    <div class="result-card">
        <h1 style="color: white; margin: 0;">🎉 Quiz abgeschlossen!</h1>
        <div class="result-score">{score} / {total}</div>
        <div class="result-text">📊 Erfolgsquote: {percentage:.1f}%</div>
        <div class="result-text">⏱️ Zeit: {int(time_taken // 60)}:{int(time_taken % 60):02d} Minuten</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Performance message
    if percentage == 100:
        st.balloons()
        st.success("🌟 Perfekt! Du hast alle Fragen richtig beantwortet!")
    elif percentage >= 80:
        st.success("👏 Ausgezeichnet! Sehr gute Leistung!")
    elif percentage >= 60:
        st.info("👍 Gut gemacht! Mit etwas Übung wird es noch besser!")
    else:
        st.warning("💪 Nicht aufgeben! Versuche es noch einmal!")
    
    # Restart button
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Quiz wiederholen", use_container_width=True):
            initialize_quiz_session(st.session_state.current_quiz)
            st.rerun()
    
    with col2:
        if st.button("📋 Neues Quiz wählen", use_container_width=True):
            for key in ['quiz_active', 'quiz_questions', 'current_question_idx', 
                       'quiz_score', 'quiz_answers', 'quiz_start_time', 
                       'answered_current', 'current_quiz']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()


# =========================================================
# HAUPTBEREICH
# =========================================================

# Check if quiz is active
if st.session_state.get('quiz_active', False):
    # Show quiz header
    st.markdown(f"""
    <div class="quiz-header">
        <div class="quiz-title">🧩 {st.session_state.current_quiz['title']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show timer
    if st.session_state.current_question_idx < len(st.session_state.quiz_questions):
        elapsed = int(time.time() - st.session_state.quiz_start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        st.markdown(f"""
        <div class="timer-display">
            ⏱️ Zeit: {minutes}:{seconds:02d}
        </div>
        """, unsafe_allow_html=True)
    
    render_current_question()

else:
    # Quiz selection screen
    st.markdown("""
    <div class="quiz-header">
        <div class="quiz-title">🎯 Quiz Auswahl</div>
    </div>
    """, unsafe_allow_html=True)
    
    quizzes = load_quizzes()
    
    if not quizzes:
        st.warning("⚠️ Noch keine Quizze gefunden. Lege im Ordner `/data/quizzes` JSON-Dateien an.")
        st.stop()
    
    st.markdown('<div class="quiz-select-card">', unsafe_allow_html=True)
    
    quiz_titles = [q["title"] for q in quizzes]
    selected_quiz_title = st.selectbox(
        "Wähle ein Quiz:",
        quiz_titles,
        index=0,
        label_visibility="collapsed"
    )
    
    selected_quiz = next(q for q in quizzes if q["title"] == selected_quiz_title)
    
    # Show quiz info
    num_questions = len(selected_quiz["questions"])
    st.markdown(f"""
    <div style="color: rgba(255,255,255,0.7); margin: 1rem 0; font-size: 1.1rem;">
        📝 Anzahl Fragen: {num_questions}<br>
        🎯 Fragen werden in zufälliger Reihenfolge angezeigt<br>
        ⏱️ Die Zeit wird automatisch gemessen
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Quiz starten", use_container_width=True, type="primary"):
        st.session_state.current_quiz = selected_quiz
        initialize_quiz_session(selected_quiz)
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)