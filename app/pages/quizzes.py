import streamlit as st
import json
import os
import random
import time
from datetime import datetime
from pages.auth import AuthManager
import uuid

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
    .main {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    
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
    
    .run-id-badge {
        background: rgba(255,255,255,0.2);
        padding: 0.5rem 1rem;
        border-radius: 10px;
        color: white;
        font-size: 0.9rem;
        display: inline-block;
        margin-top: 1rem;
        font-family: monospace;
    }
    
    .feedback-correct {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        font-size: 1.2rem;
        margin: 1rem 0;
        font-weight: 600;
        box-shadow: 0 5px 20px rgba(17, 153, 142, 0.4);
        animation: slideIn 0.3s ease;
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
        animation: slideIn 0.3s ease;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
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
    
    .leaderboard-card {
        background: rgba(255,255,255,0.05);
        border-radius: 20px;
        padding: 2rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        margin: 2rem 0;
    }
    
    .leaderboard-title {
        color: white;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .leaderboard-entry {
        background: rgba(255,255,255,0.08);
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .leaderboard-rank {
        font-size: 1.5rem;
        font-weight: 800;
        color: #667eea;
        min-width: 50px;
    }
    
    .gold { color: #FFD700; }
    .silver { color: #C0C0C0; }
    .bronze { color: #CD7F32; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# QUIZ DATEN - Hinduismus
# =========================================================
HINDUISMUS_QUIZ = {
    "title": "Kleidung und Tiere im Hinduismus",
    "questions": [
        {
            "question": "Was ist ein Sari?",
            "options": [
                "Ein ca. 6m langer Stoffstreifen, mehrfach um den Körper gewickelt",
                "Ein weites, langes Hemd für Männer",
                "Eine Kombination aus Hose und langem Oberteil",
                "Ein langes Jackett mit Stehkragen"
            ],
            "answer": "Ein ca. 6m langer Stoffstreifen, mehrfach um den Körper gewickelt"
        },
        {
            "question": "Was ist ein Kurta?",
            "options": [
                "Ein weites, langes Hemd für Männer ohne Kragen",
                "Ein hosenartiges Kleidungsstück",
                "Ein Stoffstreifen für Frauen",
                "Eine Jacke mit Stehkragen"
            ],
            "answer": "Ein weites, langes Hemd für Männer ohne Kragen"
        },
        {
            "question": "Was ist ein Dhoti?",
            "options": [
                "Ein langes Stück Stoff, in der Taille zusammengeknotet",
                "Eine Kombination aus Hose und Oberteil",
                "Ein Stoffstreifen für den Kopf",
                "Ein langes Jackett"
            ],
            "answer": "Ein langes Stück Stoff, in der Taille zusammengeknotet"
        },
        {
            "question": "Was ist ein Sherwani?",
            "options": [
                "Ein langes Jackett mit Stehkragen, über Dhoti getragen",
                "Ein weites Hemd ohne Kragen",
                "Eine Art Hose",
                "Ein Stoffstreifen"
            ],
            "answer": "Ein langes Jackett mit Stehkragen, über Dhoti getragen"
        },
        {
            "question": "Welche 5 Gaben liefert die heilige Kuh?",
            "options": [
                "Ghee (geklärte Butter), Lassi (Joghurtgetränk), Mist als Brennmaterial, Pflanzendünger, Milch",
                "Fleisch, Milch, Leder, Wolle, Knochen",
                "Butter, Käse, Sahne, Joghurt, Quark",
                "Milch, Honig, Öl, Wasser, Salz"
            ],
            "answer": "Ghee (geklärte Butter), Lassi (Joghurtgetränk), Mist als Brennmaterial, Pflanzendünger, Milch"
        },
        {
            "question": "Für welchen Gott steht der Elefant?",
            "options": [
                "Ganesha - Symbol für Glück, Weisheit und Neubeginn",
                "Shiva - Symbol für Kraft und Ewigkeit",
                "Seraswati - Symbol für Stolz und Schönheit",
                "Vishnu - Symbol für Schutz"
            ],
            "answer": "Ganesha - Symbol für Glück, Weisheit und Neubeginn"
        },
        {
            "question": "Für welchen Gott steht die Schlange?",
            "options": [
                "Shiva - Symbol für Kraft und Ewigkeit",
                "Ganesha - Symbol für Glück und Weisheit",
                "Seraswati - Symbol für Stolz und Schönheit",
                "Brahma - Symbol für Schöpfung"
            ],
            "answer": "Shiva - Symbol für Kraft und Ewigkeit"
        },
        {
            "question": "Für welchen Gott steht der Pfau?",
            "options": [
                "Seraswati - Symbol für Stolz und Schönheit",
                "Shiva - Symbol für Kraft",
                "Ganesha - Symbol für Glück",
                "Krishna - Symbol für Liebe"
            ],
            "answer": "Seraswati - Symbol für Stolz und Schönheit"
        },
        {
            "question": "Was bedeutet Kleidung im Hinduismus?",
            "options": [
                "Steht für Respekt gegenüber Gott und Tradition",
                "Ist nur für religiöse Zeremonien wichtig",
                "Muss immer weiß sein",
                "Ist nicht wichtig"
            ],
            "answer": "Steht für Respekt gegenüber Gott und Tradition"
        },
        {
            "question": "Was ist Salwar Kameez?",
            "options": [
                "Eine Kombination aus Hose und langem Oberteil",
                "Ein Stoffstreifen für Frauen",
                "Ein Hemd für Männer",
                "Eine Art Jacke"
            ],
            "answer": "Eine Kombination aus Hose und langem Oberteil"
        },
        {
            "question": "Warum werden Tiere im Hinduismus verehrt?",
            "options": [
                "Sie haben symbolische und religiöse Bedeutung",
                "Sie sind besonders stark",
                "Sie sind selten",
                "Sie sind hübsch"
            ],
            "answer": "Sie haben symbolische und religiöse Bedeutung"
        },
        {
            "question": "Was kann ein Sari über die Trägerin verraten?",
            "options": [
                "Die Herkunft der Frau",
                "Ihr Alter",
                "Ihren Beruf",
                "Ihre Lieblingsspeise"
            ],
            "answer": "Die Herkunft der Frau"
        },
        {
            "question": "Was gehört oft zu einem Nasenpiercing im Hinduismus?",
            "options": [
                "Eine Kette, die mit einem Ohrring verbunden ist",
                "Ein Armband",
                "Eine Halskette",
                "Ein Ring"
            ],
            "answer": "Eine Kette, die mit einem Ohrring verbunden ist"
        },
        {
            "question": "Wie lang ist ein typischer Kurta?",
            "options": [
                "Reicht bis zum Knie",
                "Reicht bis zum Knöchel",
                "Reicht bis zur Hüfte",
                "Reicht bis zum Boden"
            ],
            "answer": "Reicht bis zum Knie"
        },
        {
            "question": "Was wird im Hinduismus NICHT mit Tieren gemacht?",
            "options": [
                "Sie werden getötet oder gegessen",
                "Sie werden verehrt",
                "Sie haben religiöse Bedeutung",
                "Sie gelten als heilig"
            ],
            "answer": "Sie werden getötet oder gegessen"
        }
    ]
}

# =========================================================
# FUNKTIONEN
# =========================================================

def ensure_quiz_exists():
    """Stellt sicher, dass das Hinduismus-Quiz existiert."""
    os.makedirs(QUIZZES_DIR, exist_ok=True)
    quiz_path = os.path.join(QUIZZES_DIR, "hinduismus.json")
    
    if not os.path.exists(quiz_path):
        with open(quiz_path, "w", encoding="utf-8") as f:
            json.dump(HINDUISMUS_QUIZ, f, indent=4, ensure_ascii=False)


def load_all_results():
    """Lädt alle Quiz-Ergebnisse für das Leaderboard."""
    if not os.path.exists(ANSWERS_DIR):
        return []
    
    all_results = []
    for filename in os.listdir(ANSWERS_DIR):
        if filename.endswith(".json"):
            username = filename[:-5]
            path = os.path.join(ANSWERS_DIR, filename)
            
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                if "runs" in data:
                    for run in data["runs"]:
                        all_results.append({
                            "username": username,
                            "run_id": run.get("run_id", "unknown"),
                            "quiz_name": run.get("quiz_name", ""),
                            "correct": run.get("correct", 0),
                            "total": run.get("total", 0),
                            "percentage": run.get("percentage", 0),
                            "time_seconds": run.get("time_seconds", 0),
                            "timestamp": run.get("timestamp", "")
                        })
            except:
                pass
    
    return all_results


def save_result(username, quiz_name, correct, total, time_seconds, run_id, detailed_answers):
    """Speichert die Ergebnisse eines Quiz-Durchlaufs."""
    os.makedirs(ANSWERS_DIR, exist_ok=True)
    path = os.path.join(ANSWERS_DIR, f"{username}.json")
    data = {"runs": []}

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                pass

    if "runs" not in data:
        data["runs"] = []
        if "quizzes" in data:
            for old_quiz in data["quizzes"]:
                old_quiz["run_id"] = str(uuid.uuid4())[:8]
                if "detailed_answers" not in old_quiz:
                    old_quiz["detailed_answers"] = []
                data["runs"].append(old_quiz)
            del data["quizzes"]

    data["runs"].append({
        "run_id": run_id,
        "quiz_name": quiz_name,
        "correct": correct,
        "total": total,
        "percentage": round((correct / total) * 100, 1),
        "time_seconds": round(time_seconds, 2),
        "timestamp": datetime.now().isoformat(),
        "detailed_answers": detailed_answers
    })

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def initialize_quiz_session():
    """Initialisiert eine neue Quiz-Session."""
    questions = HINDUISMUS_QUIZ["questions"].copy()
    random.shuffle(questions)
    
    run_id = str(uuid.uuid4())[:8]
    
    st.session_state.quiz_active = True
    st.session_state.quiz_questions = questions
    st.session_state.current_question_idx = 0
    st.session_state.quiz_score = 0
    st.session_state.quiz_answers = []
    st.session_state.quiz_start_time = time.time()
    st.session_state.quiz_run_id = run_id
    st.session_state.show_feedback = False
    st.session_state.answer_locked = False


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
    """Zeigt die aktuelle Frage an mit automatischem Weiterklick."""
    idx = st.session_state.current_question_idx
    questions = st.session_state.quiz_questions
    
    if idx >= len(questions):
        render_quiz_results()
        return
    
    # Initialisiere answer_locked falls nicht vorhanden
    if 'answer_locked' not in st.session_state:
        st.session_state.answer_locked = False
    
    question = questions[idx]
    total = len(questions)
    
    render_progress_bar(idx + 1, total)
    
    st.markdown(f"""
    <div class="question-card">
        <div class="question-number">Frage {idx + 1} von {total}</div>
        <div class="question-text">{question['question']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.show_feedback:
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
        
        # Automatisches Weiterklicken nach 2 Sekunden
        time.sleep(2)
        st.session_state.current_question_idx += 1
        st.session_state.show_feedback = False
        st.session_state.answer_locked = False
        st.rerun()
    
    else:
        options = question["options"].copy()
        random.shuffle(options)
        
        st.markdown("<div style='margin: 2rem 0;'>", unsafe_allow_html=True)
        cols = st.columns(2)
        
        for i, option in enumerate(options):
            col = cols[i % 2]
            with col:
                # Button nur anklickbar wenn Antwort noch nicht gegeben wurde
                if st.button(f"🔹 {option}", key=f"opt_{idx}_{i}", use_container_width=True, disabled=st.session_state.answer_locked):
                    if not st.session_state.answer_locked:
                        st.session_state.answer_locked = True
                        
                        is_correct = option == question["answer"]
                        if is_correct:
                            st.session_state.quiz_score += 1
                        
                        st.session_state.quiz_answers.append({
                            "question": question["question"],
                            "selected": option,
                            "correct": question["answer"],
                            "is_correct": is_correct
                        })
                        
                        st.session_state.show_feedback = True
                        st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)


def render_leaderboard():
    """Zeigt das Leaderboard mit allen Runs."""
    st.markdown('<div class="leaderboard-card">', unsafe_allow_html=True)
    st.markdown('<div class="leaderboard-title">🏆 Leaderboard</div>', unsafe_allow_html=True)
    
    all_results = load_all_results()
    
    if not all_results:
        st.markdown('<p style="color: rgba(255,255,255,0.6); text-align: center;">Noch keine Ergebnisse vorhanden</p>', unsafe_allow_html=True)
    else:
        # Sortiere nach Prozentsatz (absteigend), dann nach Zeit (aufsteigend)
        all_results.sort(key=lambda x: (-x["percentage"], x["time_seconds"]))
        
        for i, result in enumerate(all_results[:20], 1):  # Top 20
            rank_class = ""
            rank_emoji = f"{i}."
            if i == 1:
                rank_class = "gold"
                rank_emoji = "🥇"
            elif i == 2:
                rank_class = "silver"
                rank_emoji = "🥈"
            elif i == 3:
                rank_class = "bronze"
                rank_emoji = "🥉"
            
            time_min = int(result["time_seconds"] // 60)
            time_sec = int(result["time_seconds"] % 60)
            
            st.markdown(f"""
            <div class="leaderboard-entry">
                <div style="display: flex; align-items: center; gap: 1rem; flex: 1;">
                    <span class="leaderboard-rank {rank_class}">{rank_emoji}</span>
                    <div style="flex: 1;">
                        <div style="font-weight: 600; font-size: 1.1rem;">{result['username']}</div>
                        <div style="font-size: 0.9rem; color: rgba(255,255,255,0.6);">
                            Run: {result['run_id']} | {result['quiz_name']}
                        </div>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.3rem; font-weight: 700; color: #667eea;">
                        {result['percentage']:.1f}%
                    </div>
                    <div style="font-size: 0.9rem; color: rgba(255,255,255,0.6);">
                        {result['correct']}/{result['total']} | {time_min}:{time_sec:02d}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_quiz_results():
    """Zeigt die Endergebnisse an."""
    score = st.session_state.quiz_score
    total = len(st.session_state.quiz_questions)
    time_taken = time.time() - st.session_state.quiz_start_time
    percentage = (score / total) * 100
    run_id = st.session_state.quiz_run_id
    
    save_result(
        username,
        HINDUISMUS_QUIZ["title"],
        score,
        total,
        time_taken,
        run_id,
        st.session_state.quiz_answers
    )
    
    st.markdown(f"""
    <div class="result-card">
        <h1 style="color: white; margin: 0;">🎉 Quiz abgeschlossen!</h1>
        <div class="result-score">{score} / {total}</div>
        <div class="result-text">📊 Erfolgsquote: {percentage:.1f}%</div>
        <div class="result-text">⏱️ Zeit: {int(time_taken // 60)}:{int(time_taken % 60):02d} Minuten</div>
        <div class="run-id-badge">🆔 Run-ID: {run_id}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if percentage == 100:
        st.balloons()
        st.success("🌟 Perfekt! Du hast alle Fragen richtig beantwortet!")
    elif percentage >= 80:
        st.success("👏 Ausgezeichnet! Sehr gute Leistung!")
    elif percentage >= 60:
        st.info("👍 Gut gemacht! Mit etwas Übung wird es noch besser!")
    else:
        st.warning("💪 Nicht aufgeben! Versuche es noch einmal!")
    
    with st.expander("📋 Detaillierte Antworten anzeigen"):
        for i, answer in enumerate(st.session_state.quiz_answers, 1):
            status = "✅ Richtig" if answer["is_correct"] else "❌ Falsch"
            st.markdown(f"""
            **Frage {i}:** {answer['question']}  
            {status}  
            - Deine Antwort: {answer['selected']}  
            - Richtige Antwort: {answer['correct']}
            """)
            st.divider()
    
    # Leaderboard anzeigen
    st.markdown("---")
    render_leaderboard()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Quiz wiederholen", use_container_width=True):
            initialize_quiz_session()
            st.rerun()
    
    with col2:
        if st.button("🏠 Zurück zur Startseite", use_container_width=True):
            for key in ['quiz_active', 'quiz_questions', 'current_question_idx', 
                       'quiz_score', 'quiz_answers', 'quiz_start_time', 
                       'quiz_run_id', 'show_feedback', 'answer_locked']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()


# =========================================================
# HAUPTBEREICH
# =========================================================

# Quiz-Datei sicherstellen
ensure_quiz_exists()

if st.session_state.get('quiz_active', False):
    st.markdown(f"""
    <div class="quiz-header">
        <div class="quiz-title">🧩 {HINDUISMUS_QUIZ['title']}</div>
        <div class="run-id-badge">🆔 Run: {st.session_state.quiz_run_id}</div>
    </div>
    """, unsafe_allow_html=True)
    
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
    st.markdown("""
    <div class="quiz-header">
        <div class="quiz-title">🕉️ Hinduismus Quiz</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.05); border-radius: 20px; padding: 2rem; 
                backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); margin: 2rem 0;">
        <h2 style="color: white; text-align: center; margin-bottom: 1.5rem;">
            📚 {HINDUISMUS_QUIZ['title']}
        </h2>
        <div style="color: rgba(255,255,255,0.7); margin: 1rem 0; font-size: 1.1rem;">
            📝 Anzahl Fragen: {len(HINDUISMUS_QUIZ['questions'])}<br>
            🎯 Fragen werden in zufälliger Reihenfolge angezeigt<br>
            ⏱️ Die Zeit wird automatisch gemessen<br>
            🆔 Jeder Durchlauf erhält eine eindeutige Run-ID<br>
            ⚡ Nach jeder Antwort geht es automatisch weiter
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Quiz starten", use_container_width=True, type="primary"):
        initialize_quiz_session()
        st.rerun()
    
    st.markdown("---")
    render_leaderboard()