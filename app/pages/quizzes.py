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
# CUSTOM CSS - GRAUER HINTERGRUND
# =========================================================
st.markdown("""
<style>
    .main {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    
    .quiz-header {
        background-color: #3a3a3a;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
        border: 1px solid #555555;
    }
    
    .quiz-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: white;
        margin: 0;
    }
    
    .progress-container {
        background: #3a3a3a;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        border: 1px solid #555555;
    }
    
    .progress-bar {
        height: 8px;
        background: #ffffff;
        border-radius: 4px;
        transition: width 0.3s ease;
    }
    
    .progress-text {
        color: white;
        font-size: 1rem;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    .question-card {
        background: #3a3a3a;
        border-radius: 10px;
        padding: 2rem;
        margin: 2rem 0;
        border: 1px solid #555555;
    }
    
    .question-number {
        color: #bbbbbb;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 1rem;
    }
    
    .question-text {
        color: white;
        font-size: 1.5rem;
        font-weight: 600;
        line-height: 1.4;
        margin-bottom: 2rem;
    }
    
    div[data-testid="stButton"] button {
        font-size: 1rem !important;
        padding: 1.2rem 1.5rem !important;
        border-radius: 8px !important;
        margin: 0.3rem 0 !important;
        transition: all 0.2s ease !important;
        background: #3a3a3a !important;
        border: 1px solid #555555 !important;
        color: white !important;
        font-weight: 500 !important;
        text-align: left !important;
    }
    
    div[data-testid="stButton"] button:hover {
        background: #4a4a4a !important;
        border-color: #777777 !important;
    }
    
    div[data-testid="stButton"] button:disabled {
        background: #2a2a2a !important;
        border-color: #444444 !important;
        color: #666666 !important;
    }
    
    .result-card {
        background: #3a3a3a;
        border-radius: 10px;
        padding: 2.5rem;
        text-align: center;
        margin: 2rem 0;
        border: 1px solid #555555;
    }
    
    .result-score {
        font-size: 3rem;
        font-weight: 700;
        color: white;
        margin: 1rem 0;
    }
    
    .result-text {
        font-size: 1.1rem;
        color: #cccccc;
        margin: 0.5rem 0;
    }
    
    .run-id-badge {
        background: #4a4a4a;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        color: #bbbbbb;
        font-size: 0.8rem;
        display: inline-block;
        margin-top: 1rem;
        font-family: monospace;
        border: 1px solid #555555;
    }
    
    .feedback-correct {
        background: #2a3a2a;
        padding: 1.2rem;
        border-radius: 8px;
        color: #4CAF50;
        font-size: 1.1rem;
        margin: 1rem 0;
        font-weight: 600;
        border: 1px solid #3d553d;
        animation: slideIn 0.3s ease;
    }
    
    .feedback-wrong {
        background: #3a2a2a;
        padding: 1.2rem;
        border-radius: 8px;
        color: #f44336;
        font-size: 1.1rem;
        margin: 1rem 0;
        font-weight: 600;
        border: 1px solid #553d3d;
        animation: slideIn 0.3s ease;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .timer-display {
        background: #3a3a3a;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        color: white;
        font-size: 1.1rem;
        font-weight: 600;
        text-align: center;
        border: 1px solid #555555;
        margin-bottom: 1rem;
    }
    
    .leaderboard-card {
        background: #3a3a3a;
        border-radius: 10px;
        padding: 1.5rem;
        border: 1px solid #555555;
        margin: 2rem 0;
    }
    
    .leaderboard-title {
        color: white;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .leaderboard-entry {
        background: #4a4a4a;
        padding: 1rem 1.2rem;
        border-radius: 6px;
        margin: 0.3rem 0;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #555555;
    }
    
    .leaderboard-rank {
        font-size: 1.2rem;
        font-weight: 700;
        color: #ffffff;
        min-width: 40px;
    }
    
    .gold { color: #FFD700; }
    .silver { color: #C0C0C0; }
    .bronze { color: #CD7F32; }
    
    .option-correct {
        border-left: 4px solid #4CAF50 !important;
        background: #2a3a2a !important;
    }
    
    .option-wrong {
        border-left: 4px solid #f44336 !important;
        background: #3a2a2a !important;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# QUIZ DATEN - Hinduismus
# =========================================================
HINDUISMUS_QUIZ = {
    "title": "Kleidung und Tiere im Hinduismus",
    "questions": [
        {
            "question": "Welche Bedeutung hat Kleidung im Hinduismus?",
            "options": [
                "Sie steht für Respekt gegenüber Gott und Tradition",
                "Sie ist nur für religiöse Führer wichtig",
                "Sie hat keine religiöse Bedeutung",
                "Sie muss immer weiß sein"
            ],
            "answer": "Sie steht für Respekt gegenüber Gott und Tradition"
        },
        {
            "question": "Wann spielt Kleidung im Hinduismus eine besonders wichtige Rolle?",
            "options": [
                "Bei Festen und in Tempeln",
                "Nur bei Hochzeiten",
                "Nur beim Gebet zu Hause",
                "Nie, Kleidung ist unwichtig"
            ],
            "answer": "Bei Festen und in Tempeln"
        },
        {
            "question": "Gibt es im Hinduismus feste Kleidungsvorschriften?",
            "options": [
                "Nein, es gibt keine festen Vorschriften",
                "Ja, alle müssen Weiß tragen",
                "Ja, nur Männer tragen traditionelle Kleidung",
                "Ja, Kleidung ist streng vorgeschrieben"
            ],
            "answer": "Nein, es gibt keine festen Vorschriften"
        },
        {
            "question": "Was ist ein Sari?",
            "options": [
                "Ein ca. 6m langer Stoffstreifen, mehrfach um den Körper gewickelt",
                "Ein weites Hemd für Männer",
                "Eine Kombination aus Hose und Oberteil",
                "Ein langes Jackett mit Stehkragen"
            ],
            "answer": "Ein ca. 6m langer Stoffstreifen, mehrfach um den Körper gewickelt"
        },
        {
            "question": "Was kann ein Sari über die Trägerin verraten?",
            "options": [
                "Die Herkunft der Frau",
                "Ihr Alter",
                "Ihren Familienstand",
                "Ihre Religion"
            ],
            "answer": "Die Herkunft der Frau"
        },
        {
            "question": "Was gehört oft zu einem Nasenpiercing im Hinduismus?",
            "options": [
                "Eine Kette, die mit einem Ohrring verbunden ist",
                "Ein Armband",
                "Ein Stirnband",
                "Ein Ring am Finger"
            ],
            "answer": "Eine Kette, die mit einem Ohrring verbunden ist"
        },
        {
            "question": "Was ist ein Kurta?",
            "options": [
                "Ein weites, langes Hemd für Männer ohne Kragen",
                "Ein Tuch für den Kopf",
                "Ein Rock für Frauen",
                "Eine kurze Jacke"
            ],
            "answer": "Ein weites, langes Hemd für Männer ohne Kragen"
        },
        {
            "question": "Wie lang ist ein typischer Kurta?",
            "options": [
                "Er reicht bis zum Knie",
                "Er reicht bis zur Hüfte",
                "Er reicht bis zum Boden",
                "Er endet an der Taille"
            ],
            "answer": "Er reicht bis zum Knie"
        },
        {
            "question": "Was ist ein Salwar Kameez?",
            "options": [
                "Eine Kombination aus Hose und langem Oberteil",
                "Ein Stoffstreifen für Frauen",
                "Ein Hemd für Männer",
                "Eine Jacke mit Kragen"
            ],
            "answer": "Eine Kombination aus Hose und langem Oberteil"
        },
        {
            "question": "Was ist ein Dhoti?",
            "options": [
                "Ein langes Stück Stoff, in der Taille zusammengeknotet",
                "Ein Sari für Männer",
                "Eine Kombination aus Hose und Jacke",
                "Ein Stirntuch"
            ],
            "answer": "Ein langes Stück Stoff, in der Taille zusammengeknotet"
        },
        {
            "question": "Was ist ein Sherwani?",
            "options": [
                "Ein langes Jackett mit Stehkragen, das über dem Dhoti getragen wird",
                "Ein leichter Sommermantel",
                "Ein traditioneller Hut",
                "Ein religiöser Schal"
            ],
            "answer": "Ein langes Jackett mit Stehkragen, das über dem Dhoti getragen wird"
        },
        {
            "question": "Welche Rolle spielen Tiere im Hinduismus?",
            "options": [
                "Sie gelten als heilig und werden verehrt",
                "Sie werden geopfert",
                "Sie sind bedeutungslos",
                "Sie dienen nur als Arbeitstiere"
            ],
            "answer": "Sie gelten als heilig und werden verehrt"
        },
        {
            "question": "Warum werden Tiere im Hinduismus verehrt?",
            "options": [
                "Weil sie symbolische und religiöse Bedeutung haben",
                "Weil sie selten sind",
                "Weil sie gefährlich sind",
                "Weil sie schön aussehen"
            ],
            "answer": "Weil sie symbolische und religiöse Bedeutung haben"
        },
        {
            "question": "Was wird im Hinduismus NICHT mit Tieren gemacht?",
            "options": [
                "Sie werden getötet oder gegessen",
                "Sie werden verehrt",
                "Sie gelten als heilig",
                "Sie haben religiöse Bedeutung"
            ],
            "answer": "Sie werden getötet oder gegessen"
        },
        {
            "question": "Welche fünf Gaben liefert die heilige Kuh?",
            "options": [
                "Ghee, Lassi, Mist, Pflanzendünger, Urin",
                "Milch, Butter, Käse, Joghurt, Sahne",
                "Honig, Öl, Milch, Wasser, Salz",
                "Fleisch, Leder, Knochen, Fell, Milch"
            ],
            "answer": "Ghee, Lassi, Mist, Pflanzendünger, Urin"
        },
        {
            "question": "Für welchen Gott steht der Elefant?",
            "options": [
                "Ganesha - Symbol für Glück, Weisheit und Neubeginn",
                "Shiva - Symbol für Kraft und Ewigkeit",
                "Vishnu - Symbol für Schutz",
                "Brahma - Symbol für Schöpfung"
            ],
            "answer": "Ganesha - Symbol für Glück, Weisheit und Neubeginn"
        },
        {
            "question": "Für welchen Gott steht die Schlange?",
            "options": [
                "Shiva - Symbol für Kraft und Ewigkeit",
                "Ganesha - Symbol für Glück und Neubeginn",
                "Vishnu - Symbol für Schutz",
                "Seraswati - Symbol für Schönheit"
            ],
            "answer": "Shiva - Symbol für Kraft und Ewigkeit"
        },
        {
            "question": "Für welchen Gott steht der Pfau?",
            "options": [
                "Seraswati - Symbol für Stolz und Schönheit",
                "Ganesha - Symbol für Glück und Neubeginn",
                "Shiva - Symbol für Kraft",
                "Vishnu - Symbol für Schutz"
            ],
            "answer": "Seraswati - Symbol für Stolz und Schönheit"
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
    st.session_state.answered_questions = set()


def render_progress_bar(current, total):
    """Zeigt eine Fortschrittsanzeige."""
    progress = (current / total) * 100
    st.markdown(f"""
    <div class="progress-container">
        <div style="background: #555555; border-radius: 4px; overflow: hidden;">
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
    
    # Sicherstellen, dass answered_questions existiert
    if 'answered_questions' not in st.session_state:
        st.session_state.answered_questions = set()
    
    question = questions[idx]
    total = len(questions)
    
    render_progress_bar(idx + 1, total)
    
    st.markdown(f"""
    <div class="question-card">
        <div class="question-number">Frage {idx + 1} von {total}</div>
        <div class="question-text">{question['question']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Prüfe ob diese Frage bereits beantwortet wurde
    question_already_answered = idx in st.session_state.answered_questions
    
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
        
        # Automatischer Übergang zur nächsten Frage
        if st.button("➡️ Nächste Frage", use_container_width=True, type="primary"):
            st.session_state.current_question_idx += 1
            st.session_state.show_feedback = False
            st.rerun()
    
    else:
        # OPTIONEN MISCHEN - damit die richtige Antwort nicht immer oben links steht
        options = question["options"].copy()
        random.shuffle(options)
        
        # Wenn Frage bereits beantwortet, zeige die korrekte Antwort an
        if question_already_answered:
            st.info("ℹ️ Diese Frage hast du bereits beantwortet.")
            
            # Finde die gegebene Antwort für diese Frage
            user_answer = None
            for answer in st.session_state.quiz_answers:
                if answer["question"] == question["question"]:
                    user_answer = answer
                    break
            
            if user_answer:
                st.markdown(f"""
                <div style="margin: 1rem 0; padding: 1rem; background: #4a4a4a; border-radius: 8px; border: 1px solid #555555;">
                    <strong>Deine Antwort:</strong> {user_answer['selected']}<br>
                    <strong>Korrekte Antwort:</strong> {user_answer['correct']}<br>
                    <strong>Status:</strong> {"✅ Richtig" if user_answer['is_correct'] else "❌ Falsch"}
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("➡️ Nächste Frage", use_container_width=True, type="primary"):
                st.session_state.current_question_idx += 1
                st.rerun()
                
        else:
            # Frage noch nicht beantwortet - zeige Buttons an
            st.markdown("<div style='margin: 2rem 0;'>", unsafe_allow_html=True)
            cols = st.columns(2)
            
            for i, option in enumerate(options):
                col = cols[i % 2]
                with col:
                    if st.button(f"{option}", key=f"opt_{idx}_{i}", use_container_width=True):
                        is_correct = option == question["answer"]
                        if is_correct:
                            st.session_state.quiz_score += 1
                        
                        st.session_state.quiz_answers.append({
                            "question": question["question"],
                            "selected": option,
                            "correct": question["answer"],
                            "is_correct": is_correct
                        })
                        
                        # Markiere diese Frage als beantwortet
                        st.session_state.answered_questions.add(idx)
                        st.session_state.show_feedback = True
                        st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)


def render_leaderboard():
    """Zeigt das Leaderboard mit allen Runs."""
    st.markdown('<div class="leaderboard-card">', unsafe_allow_html=True)
    st.markdown('<div class="leaderboard-title">🏆 Bestenliste</div>', unsafe_allow_html=True)
    
    all_results = load_all_results()
    
    if not all_results:
        st.markdown('<p style="color: #bbbbbb; text-align: center;">Noch keine Ergebnisse vorhanden</p>', unsafe_allow_html=True)
    else:
        # Sortiere nach Prozentsatz (absteigend), dann nach Zeit (aufsteigend)
        all_results.sort(key=lambda x: (-x["percentage"], x["time_seconds"]))
        
        for i, result in enumerate(all_results[:10], 1):  # Top 10
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
                        <div style="font-weight: 600; font-size: 1rem;">{result['username']}</div>
                        <div style="font-size: 0.8rem; color: #bbbbbb;">
                            {result['quiz_name']} • {result['run_id']}
                        </div>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.1rem; font-weight: 700; color: #ffffff;">
                        {result['percentage']:.1f}%
                    </div>
                    <div style="font-size: 0.8rem; color: #bbbbbb;">
                        {result['correct']}/{result['total']} • {time_min}:{time_sec:02d}
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
        <div class="result-text">Erfolgsquote: {percentage:.1f}%</div>
        <div class="result-text">Zeit: {int(time_taken // 60)}:{int(time_taken % 60):02d} Minuten</div>
        <div class="run-id-badge">Run-ID: {run_id}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if percentage == 100:
        st.success("🌟 Perfekt! Du hast alle Fragen richtig beantwortet!")
    elif percentage >= 80:
        st.success("👏 Ausgezeichnet! Sehr gute Leistung!")
    elif percentage >= 60:
        st.info("👍 Gut gemacht!")
    else:
        st.warning("💪 Übe weiter!")
    
    with st.expander("📋 Detaillierte Antworten anzeigen"):
        for i, answer in enumerate(st.session_state.quiz_answers, 1):
            status = "✅ Richtig" if answer["is_correct"] else "❌ Falsch"
            st.markdown(f"""
            **Frage {i}:** {answer['question']}  
            **{status}**  
            • Deine Antwort: {answer['selected']}  
            • Richtige Antwort: {answer['correct']}
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
                       'quiz_run_id', 'show_feedback', 'answered_questions']:
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
        <div class="run-id-badge">Run: {st.session_state.quiz_run_id}</div>
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
    <div style="background: #3a3a3a; border-radius: 10px; padding: 2rem; 
                border: 1px solid #555555; margin: 2rem 0;">
        <h2 style="color: white; text-align: center; margin-bottom: 1.5rem;">
            📚 {HINDUISMUS_QUIZ['title']}
        </h2>
        <div style="color: #cccccc; margin: 1rem 0; font-size: 1rem;">
            📝 <strong>Anzahl Fragen:</strong> {len(HINDUISMUS_QUIZ['questions'])}<br>
            🎯 <strong>Zufällige Reihenfolge:</strong> Ja<br>
            🔀 <strong>Antworten gemischt:</strong> Ja<br>
            ⏱️ <strong>Zeitmessung:</strong> Automatisch<br>
            🆔 <strong>Run-ID:</strong> Eindeutig pro Durchlauf<br>
            🔒 <strong>Beantwortete Fragen:</strong> Können nicht erneut beantwortet werden
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Quiz starten", use_container_width=True, type="primary"):
        initialize_quiz_session()
        st.rerun()
    
    st.markdown("---")
    render_leaderboard()