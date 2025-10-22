"""
Quiz-Modul für die Streamlit Quiz-App
"""
import streamlit as st
import os
import json
import random
from datetime import datetime
import time
from pages.auth import AuthManager, UserRole, DEFAULT_PASSWORD

auth_manager = AuthManager()
# ⚠️ WICHTIG: Session-Validierung bei JEDEM Seitenaufruf!
if "username" in st.session_state and st.session_state.username.strip():
    status = auth_manager.check_user_status(st.session_state.username)
    
    if status["should_logout"]:
        # Benutzer wurde deaktiviert/gelöscht/gesperrt
        st.error(f"🔒 {status['message']}")
        st.warning("Du wurdest automatisch ausgeloggt.")
        
        # Session komplett löschen
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        # Warte kurz damit User die Nachricht sieht
        import time
        time.sleep(2)
        
        # Zurück zum Login
        st.rerun()

# ---------------------- KONFIGURATION ----------------------
ANSWERS_DIR = "./data/answers"

# ---------------------- QUIZ-DEFINITIONEN ----------------------
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

QUIZZES["Kombiniert"] = {**QUIZZES["Kleidung"], **QUIZZES["Heilige Tiere"]}

# ---------------------- THEME ----------------------
def get_theme():
    """Lädt das aktuelle Theme aus den Einstellungen"""
    settings_file = "./data/settings.json"
    if os.path.exists(settings_file):
        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                settings = json.load(f)
                theme_name = settings.get("current_theme", "Light")
        except:
            theme_name = "Light"
    else:
        theme_name = "Light"
    
    themes = {
        "Light": {
            "bg": "#ffffff",
            "surface": "#f8f9fa",
            "border": "#e9ecef",
            "text": "#1a1a1a",
            "text_secondary": "#6c757d",
            "accent": "#2563eb",
            "accent_light": "#dbeafe",
            "success": "#10b981",
            "warning": "#f59e0b"
        },
        "Dark": {
            "bg": "#0a0a0a",
            "surface": "#1a1a1a",
            "border": "#2a2a2a",
            "text": "#ffffff",
            "text_secondary": "#a0a0a0",
            "accent": "#3b82f6",
            "accent_light": "#1e3a8a",
            "success": "#10b981",
            "warning": "#f59e0b"
        },
        "Minimal": {
            "bg": "#fafafa",
            "surface": "#ffffff",
            "border": "#d4d4d4",
            "text": "#0a0a0a",
            "text_secondary": "#737373",
            "accent": "#000000",
            "accent_light": "#f5f5f5",
            "success": "#16a34a",
            "warning": "#ea580c"
        }
    }
    return themes.get(theme_name, themes["Light"])

def apply_quiz_theme():
    """Wendet das minimalistische Theme an"""
    t = get_theme()
    
    css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        * {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        
        .stApp {{
            background: {t['bg']};
        }}
        
        .block-container {{
            padding-top: 3rem;
            padding-bottom: 3rem;
            max-width: 900px;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            color: {t['text']} !important;
            font-weight: 600 !important;
            letter-spacing: -0.02em;
        }}
        
        p, span, div, label {{
            color: {t['text']} !important;
        }}
        
        /* Start Screen */
        .start-card {{
            background: {t['surface']};
            border: 1px solid {t['border']};
            border-radius: 20px;
            padding: 4rem 3rem;
            margin: 3rem 0;
            text-align: center;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
        }}
        
        .start-title {{
            font-size: 2.5rem;
            font-weight: 700;
            color: {t['text']} !important;
            margin-bottom: 1rem;
        }}
        
        .start-subtitle {{
            font-size: 1.125rem;
            color: {t['text_secondary']} !important;
            margin-bottom: 2rem;
        }}
        
        /* Question Card */
        .question-card {{
            background: {t['surface']};
            border: 1px solid {t['border']};
            border-radius: 16px;
            padding: 2.5rem;
            margin: 2rem 0;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }}
        
        .question-number {{
            color: {t['text_secondary']} !important;
            font-size: 0.875rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 1rem;
        }}
        
        .question-text {{
            font-size: 1.5rem;
            font-weight: 600;
            color: {t['text']} !important;
            line-height: 1.4;
            margin-bottom: 2rem;
        }}
        
        /* Radio Options */
        .stRadio > div {{
            gap: 0.75rem;
        }}
        
        .stRadio > div > label {{
            background: {t['surface']};
            border: 2px solid {t['border']};
            border-radius: 12px;
            padding: 1.25rem 1.75rem;
            margin: 0;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            font-size: 1rem;
        }}
        
        .stRadio > div > label:hover {{
            border-color: {t['accent']};
            background: {t['accent_light']};
            transform: translateX(4px);
        }}
        
        /* Buttons */
        .stButton > button {{
            background: {t['accent']};
            color: white !important;
            border: none;
            border-radius: 10px;
            padding: 0.875rem 2rem;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.2s ease;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
        }}
        
        /* Progress Bar */
        .progress-container {{
            background: {t['border']};
            height: 8px;
            border-radius: 4px;
            margin: 2rem 0 1rem 0;
            overflow: hidden;
        }}
        
        .progress-bar {{
            background: linear-gradient(90deg, {t['accent']}, {t['success']});
            height: 100%;
            transition: width 0.4s ease;
            border-radius: 4px;
        }}
        
        /* Timer Display */
        .timer-display {{
            background: {t['surface']};
            border: 2px solid {t['accent']};
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }}
        
        .timer-label {{
            font-size: 0.875rem;
            color: {t['text_secondary']} !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}
        
        .timer-value {{
            font-size: 3rem;
            font-weight: 700;
            color: {t['accent']} !important;
            font-variant-numeric: tabular-nums;
            line-height: 1;
        }}
        
        /* Stats Card */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }}
        
        .stats-card {{
            background: {t['surface']};
            border: 1px solid {t['border']};
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            transition: all 0.3s ease;
        }}
        
        .stats-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
        }}
        
        .stats-value {{
            font-size: 3rem;
            font-weight: 700;
            color: {t['accent']} !important;
            line-height: 1;
            margin: 0.5rem 0;
        }}
        
        .stats-label {{
            font-size: 0.875rem;
            color: {t['text_secondary']} !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }}
        
        /* Leaderboard */
        .leaderboard-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 3rem 0 1.5rem 0;
        }}
        
        .leaderboard-title {{
            font-size: 1.5rem;
            font-weight: 700;
            color: {t['text']} !important;
        }}
        
        .leaderboard-item {{
            background: {t['surface']};
            border: 2px solid {t['border']};
            border-radius: 12px;
            padding: 1.25rem 1.75rem;
            margin: 0.75rem 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.2s ease;
        }}
        
        .leaderboard-item:hover {{
            transform: translateX(4px);
            border-color: {t['accent']};
        }}
        
        .leaderboard-item.current-user {{
            background: {t['accent_light']};
            border-color: {t['accent']};
            border-width: 2px;
        }}
        
        .leaderboard-left {{
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }}
        
        .leaderboard-rank {{
            font-weight: 700;
            color: {t['accent']} !important;
            font-size: 1.5rem;
            min-width: 3rem;
            text-align: center;
        }}
        
        .leaderboard-rank.top-1 {{
            color: #fbbf24 !important;
            font-size: 1.75rem;
        }}
        
        .leaderboard-rank.top-2 {{
            color: #94a3b8 !important;
        }}
        
        .leaderboard-rank.top-3 {{
            color: #fb923c !important;
        }}
        
        .leaderboard-name {{
            font-weight: 600;
            color: {t['text']} !important;
            font-size: 1.125rem;
        }}
        
        .leaderboard-badge {{
            background: {t['accent']};
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-left: 0.75rem;
        }}
        
        .leaderboard-right {{
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 0.25rem;
        }}
        
        .leaderboard-score {{
            color: {t['text']} !important;
            font-size: 1.125rem;
            font-weight: 600;
        }}
        
        .leaderboard-time {{
            color: {t['text_secondary']} !important;
            font-size: 0.875rem;
        }}
        
        /* Select Box */
        .stSelectbox > div > div > select {{
            background: {t['surface']} !important;
            border: 1px solid {t['border']} !important;
            border-radius: 10px !important;
            color: {t['text']} !important;
            font-size: 1rem !important;
            padding: 0.875rem !important;
            font-weight: 500 !important;
        }}
        
        /* Success/Error Messages */
        .stSuccess, .stError, .stWarning {{
            background: {t['surface']} !important;
            border: 1px solid {t['border']} !important;
            border-radius: 10px;
            padding: 1rem !important;
        }}
        
        /* Hide Streamlit Elements */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# ---------------------- DATEN-FUNKTIONEN ----------------------
def get_user_file(username: str):
    """Gibt den Pfad zur Benutzer-Datei zurück"""
    os.makedirs(ANSWERS_DIR, exist_ok=True)
    return os.path.join(ANSWERS_DIR, f"{username}.json")

def load_user_data(username: str):
    """Lädt die Daten eines Benutzers"""
    user_file = get_user_file(username)
    if not os.path.exists(user_file):
        return {"username": username, "quizzes": []}
    
    try:
        with open(user_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Fehler beim Laden von {username}: {e}")
        return {"username": username, "quizzes": []}

def save_user_data(username: str, data: dict):
    """Speichert die Daten eines Benutzers"""
    user_file = get_user_file(username)
    try:
        with open(user_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Fehler beim Speichern von {username}: {e}")

def save_quiz_result(username: str, quiz_name: str, answers: dict, time_taken: float):
    """Speichert ein Quiz-Ergebnis"""
    user_data = load_user_data(username)
    
    correct = sum(1 for q in answers.values() if q["correct"])
    total = len(answers)
    
    quiz_entry = {
        "quiz_name": quiz_name,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "correct": correct,
        "total": total,
        "time_seconds": round(time_taken, 2),
        "answers": answers
    }
    
    user_data["quizzes"].append(quiz_entry)
    save_user_data(username, user_data)

def get_leaderboard(quiz_name: str = None):
    """Erstellt eine Bestenliste basierend auf Punkten und Durchschnittszeit"""
    if not os.path.exists(ANSWERS_DIR):
        return []
    
    leaderboard = []
    
    for filename in os.listdir(ANSWERS_DIR):
        if not filename.endswith(".json"):
            continue
        
        username = filename[:-5]
        user_data = load_user_data(username)
        
        # Filtere Quiz-Ergebnisse
        quizzes = user_data.get("quizzes", [])
        if quiz_name:
            quizzes = [q for q in quizzes if q.get("quiz_name") == quiz_name]
        
        if not quizzes:
            continue
        
        # Berechne Statistiken
        total_correct = sum(q.get("correct", 0) for q in quizzes)
        total_questions = sum(q.get("total", 0) for q in quizzes)
        total_time = sum(q.get("time_seconds", 0) for q in quizzes)
        avg_time = total_time / len(quizzes) if quizzes else 0
        
        leaderboard.append({
            "username": username,
            "correct": total_correct,
            "total": total_questions,
            "avg_time": avg_time,
            "attempts": len(quizzes)
        })
    
    # Sortiere: Erst nach Punkten, dann nach durchschnittlicher Zeit
    leaderboard.sort(key=lambda x: (-x["correct"], x["avg_time"]))
    
    return leaderboard

def get_user_rank(username: str, leaderboard: list):
    """Gibt den Rang eines Benutzers zurück"""
    for rank, entry in enumerate(leaderboard, 1):
        if entry["username"] == username:
            return rank
    return None

def format_time(seconds: float):
    """Formatiert Sekunden in MM:SS Format"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

# ---------------------- QUIZ-ANZEIGE ----------------------
def show_quiz(username: str):
    """Zeigt das Quiz-Interface"""
    apply_quiz_theme()
    t = get_theme()
    
    # Quiz-Auswahl
    quiz_names = list(QUIZZES.keys())
    choice = st.selectbox("Kategorie wählen", quiz_names, label_visibility="collapsed")
    
    # Session State initialisieren
    if "quiz_started" not in st.session_state:
        st.session_state["quiz_started"] = False
    
    if "quiz_step" not in st.session_state or st.session_state.get("current_quiz") != choice:
        st.session_state["quiz_step"] = 0
        st.session_state["current_quiz"] = choice
        st.session_state["answered_questions"] = {}
        st.session_state["quiz_started"] = False
    
    # Start-Screen oder Quiz
    if not st.session_state["quiz_started"]:
        show_start_screen(username, choice, t)
    else:
        show_quiz_questions(username, choice, t)

def show_start_screen(username: str, quiz_name: str, theme: dict):
    """Zeigt den Start-Bildschirm"""
    quiz = QUIZZES[quiz_name]
    total_questions = len(quiz)
    
    st.markdown(f'''
    <div class="start-card">
        <div class="start-title">📝 {quiz_name}</div>
        <div class="start-subtitle">
            Bereit für {total_questions} Fragen?<br>
            Deine Zeit wird gemessen!
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Quiz starten", use_container_width=True, key="start_quiz"):
            st.session_state["quiz_started"] = True
            st.session_state["quiz_start_time"] = time.time()
            st.rerun()

def show_quiz_questions(username: str, quiz_name: str, theme: dict):
    """Zeigt die Quiz-Fragen mit Timer"""
    quiz = QUIZZES[quiz_name]
    questions = list(quiz.items())
    total_questions = len(questions)
    current_step = st.session_state["quiz_step"]
    
    # Live Timer berechnen
    if "quiz_start_time" in st.session_state:
        elapsed = time.time() - st.session_state["quiz_start_time"]
    else:
        elapsed = 0
    
    # Header mit Timer
    st.markdown(f"<h1 style='margin-bottom: 0.5rem;'>{quiz_name}</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Fortschrittsanzeige
        progress = (current_step / total_questions) * 100
        st.markdown(f'''
        <div class="progress-container">
            <div class="progress-bar" style="width: {progress}%"></div>
        </div>
        <p style='color: {theme['text_secondary']} !important; font-size: 0.875rem; margin-top: 0.5rem;'>
            Frage {current_step + 1} von {total_questions}
        </p>
        ''', unsafe_allow_html=True)
    
    with col2:
        # Live Timer
        st.markdown(f'''
        <div class="timer-display">
            <div class="timer-label">Zeit</div>
            <div class="timer-value">{format_time(elapsed)}</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Quiz-Fragen oder Ergebnis
    if current_step < total_questions:
        show_question(username, quiz_name, questions, current_step, theme)
        # Auto-refresh für Timer
        time.sleep(0.1)
        st.rerun()
    else:
        show_results(username, quiz_name, elapsed, theme)

def show_question(username: str, quiz_name: str, questions: list, step: int, theme: dict):
    """Zeigt eine einzelne Frage"""
    question_id, question_data = questions[step]
    
    # Frage anzeigen
    st.markdown(f'''
    <div class="question-card">
        <div class="question-number">Frage {step + 1}</div>
        <div class="question-text">{question_data['frage']}</div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Antwortoptionen
    answer = st.radio(
        "Wähle deine Antwort",
        question_data["optionen"],
        key=f"q_{step}",
        label_visibility="collapsed"
    )
    
    # Navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if step > 0:
            if st.button("← Zurück", use_container_width=True):
                st.session_state["quiz_step"] -= 1
                st.rerun()
    
    with col3:
        if st.button("Weiter →", use_container_width=True):
            if answer:
                # Antwort speichern
                is_correct = answer == question_data["richtig"]
                st.session_state["answered_questions"][question_id] = {
                    "question": question_data["frage"],
                    "answer": answer,
                    "correct": is_correct
                }
                
                st.session_state["quiz_step"] += 1
                st.rerun()
            else:
                st.warning("Bitte wähle eine Antwort")

def show_results(username: str, quiz_name: str, time_taken: float, theme: dict):
    """Zeigt die Ergebnisse"""
    # Ergebnis speichern
    answered = st.session_state.get("answered_questions", {})
    save_quiz_result(username, quiz_name, answered, time_taken)
    
    # Bestenliste laden und Rang prüfen
    leaderboard = get_leaderboard(quiz_name)
    user_rank = get_user_rank(username, leaderboard)
    
    # Konfetti wenn Top 10
    if user_rank and user_rank <= 10:
        st.balloons()
    
    st.markdown(f"<h2 style='text-align: center; margin: 2rem 0;'>🎉 Quiz abgeschlossen!</h2>", unsafe_allow_html=True)
    
    # Rang-Anzeige
    if user_rank and user_rank <= 10:
        rank_emoji = "🥇" if user_rank == 1 else "🥈" if user_rank == 2 else "🥉" if user_rank == 3 else "🏆"
        st.markdown(f"<h3 style='text-align: center; color: {theme['accent']} !important;'>{rank_emoji} Platz {user_rank} in der Bestenliste!</h3>", unsafe_allow_html=True)
    
    # Eigene Statistiken
    correct = sum(1 for q in answered.values() if q["correct"])
    total = len(answered)
    percentage = (correct / total * 100) if total > 0 else 0
    
    # Statistik-Cards
    st.markdown(f'''
    <div class="stats-grid">
        <div class="stats-card">
            <div class="stats-label">Richtig</div>
            <div class="stats-value">{correct}</div>
        </div>
        <div class="stats-card">
            <div class="stats-label">Gesamt</div>
            <div class="stats-value">{total}</div>
        </div>
        <div class="stats-card">
            <div class="stats-label">Prozent</div>
            <div class="stats-value">{percentage:.0f}%</div>
        </div>
        <div class="stats-card">
            <div class="stats-label">Zeit</div>
            <div class="stats-value" style="font-size: 2rem;">{format_time(time_taken)}</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Bestenliste
    st.markdown(f'''
    <div class="leaderboard-header">
        <div class="leaderboard-title">🏆 Top 10</div>
    </div>
    ''', unsafe_allow_html=True)
    
    if leaderboard:
        for rank, entry in enumerate(leaderboard[:10], 1):
            is_current = entry["username"] == username
            rank_class = ""
            rank_icon = f"#{rank}"
            
            if rank == 1:
                rank_class = "top-1"
                rank_icon = "🥇"
            elif rank == 2:
                rank_class = "top-2"
                rank_icon = "🥈"
            elif rank == 3:
                rank_class = "top-3"
                rank_icon = "🥉"
            
            current_class = "current-user" if is_current else ""
            badge = '<span class="leaderboard-badge">Du</span>' if is_current else ''
            
            st.markdown(f'''
            <div class="leaderboard-item {current_class}">
                <div class="leaderboard-left">
                    <div class="leaderboard-rank {rank_class}">{rank_icon}</div>
                    <div class="leaderboard-name">{entry['username']}{badge}</div>
                </div>
                <div class="leaderboard-right">
                    <div class="leaderboard-score">{entry['correct']} / {entry['total']} Punkte</div>
                    <div class="leaderboard-time">Ø {format_time(entry['avg_time'])} • {entry['attempts']} Versuche</div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
    else:
        st.info("Noch keine Einträge vorhanden")
    
    # Aktionen
    st.markdown("<div style='margin-top: 3rem;'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Nochmal spielen", use_container_width=True):
            st.session_state["quiz_step"] = 0
            st.session_state["answered_questions"] = {}
            st.session_state["quiz_started"] = False
            st.rerun()
    
    with col2:
        if st.button("← Zurück", use_container_width=True):
            st.switch_page("main.py")

# ---------------------- MAIN ----------------------
def main():
    """Hauptfunktion für Quiz-Seite"""
    if not st.session_state.get("logged_in", False):
        st.error("Bitte zuerst anmelden")
        st.switch_page("main.py")
        return
    
    username = st.session_state.get("username", "Unbekannt")
    show_quiz(username)

if __name__ == "__main__":
    main()