import streamlit as st
import json
import random
import requests
from datetime import datetime, timezone
from typing import List, Dict, Any

# === IMPORTS ===
try:
    # Importiere aus auth.py (NICHT user_management.py)
    from auth import AuthManager, LoginResult, UserRole, load_answers, save_answer
    _auth = AuthManager()
except Exception as e:
    st.error(f"Fehler beim Laden des Auth-Systems: {e}")
    st.stop()

try:
    from admin import show_admin_panel
except Exception:
    def show_admin_panel():
        st.warning("Admin-Panel nicht verfügbar")

try:
    from quizzes import QUIZZES
except Exception:
    QUIZZES = {
        "Beispiel-Quiz": {
            "q1": {"frage": "Was ist 2+2?", "optionen": ["3", "4", "5"], "richtig": "4"},
            "q2": {"frage": "Farbe des Himmels?", "optionen": ["Blau", "Grün"], "richtig": "Blau"}
        }
    }

# === API ENDPOINT (Optional) ===
API_URL = "https://quiz-rel.onrender.com/api/answers"

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
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.05);
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
        backdrop-filter: blur(10px);
    }
    .warning-box {
        background: rgba(255,165,0,0.2);
        border-left: 4px solid orange;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# === SESSION DEFAULTS ===
DEFAULT_KEYS = {
    "authentifiziert": False,
    "username": "",
    "user_role": None,
    "needs_password_change": False,
    "quiz_step": 0,
    "current_quiz": "",
    "quiz_start_time": None,
    "show_results": False,
    "answered_questions": [],
    "quiz_duration": None
}

for k, v in DEFAULT_KEYS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# === HELPER FUNKTIONEN ===
def is_user_active(username: str) -> bool:
    """Prüft ob Benutzer aktiv ist"""
    users = _auth.load_users()
    if username in users:
        return users[username].active
    return False

def is_admin(username: str) -> bool:
    """Prüft ob Benutzer Admin ist"""
    users = _auth.load_users()
    if username in users:
        return users[username].role == UserRole.ADMIN
    return False

# === LEADERBOARD ===
def leaderboard(sidebar=False):
    """Zeigt die Bestenliste an"""
    answers = load_answers()
    
    if not answers:
        msg = "📊 Noch keine Daten vorhanden."
        if sidebar:
            st.sidebar.info(msg)
        else:
            st.info(msg)
        return
    
    # Berechne Scores
    scores = {}
    for a in answers:
        user = a.get("username")
        if user not in scores:
            scores[user] = {"correct": 0, "total": 0}
        scores[user]["total"] += 1
        if a.get("correct"):
            scores[user]["correct"] += 1
    
    # Sortiere nach Erfolgsrate
    ranking = sorted(
        scores.items(), 
        key=lambda x: (x[1]["correct"] / (x[1]["total"] or 1), x[1]["correct"]), 
        reverse=True
    )
    
    if sidebar:
        st.sidebar.subheader("🏆 Bestenliste")
        for i, (user, s) in enumerate(ranking[:10], 1):  # Top 10
            rate = (s["correct"] / s["total"] * 100) if s["total"] else 0
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            st.sidebar.write(f"{medal} **{user}** — {s['correct']}/{s['total']} ({rate:.0f}%)")
    else:
        st.subheader("🏆 Bestenliste")
        cols = st.columns([1, 3, 2, 2])
        cols[0].write("**Rang**")
        cols[1].write("**Benutzer**")
        cols[2].write("**Richtig**")
        cols[3].write("**Quote**")
        
        for i, (user, s) in enumerate(ranking, 1):
            cols = st.columns([1, 3, 2, 2])
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else str(i)
            rate = (s["correct"] / s["total"] * 100) if s["total"] else 0
            cols[0].write(medal)
            cols[1].write(user)
            cols[2].write(f"{s['correct']}/{s['total']}")
            cols[3].write(f"{rate:.1f}%")

# === LOGIN PAGE ===
def login_page():
    """Login-Seite mit Benutzer-Registrierung"""
    st.title("🎮 Willkommen zum Quiz")
    st.markdown("---")
    
    # Info-Box
    with st.expander("ℹ️ Wie funktioniert die Anmeldung?"):
        st.markdown("""
        **Neue Benutzer:**
        - Wähle einen Benutzernamen (4-20 Zeichen, nur Buchstaben, Zahlen, _ und -)
        - Verwende das Standard-Passwort: `4-26-2011`
        - Nach dem ersten Login musst du dein Passwort ändern
        
        **Regeln für Benutzernamen:**
        - Mindestens 4 Zeichen
        - Maximal 20 Zeichen
        - Keine verbotenen Wörter
        - Nur Buchstaben, Zahlen, Unterstrich und Bindestrich
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        username = st.text_input(
            "Benutzername", 
            key="username_input",
            placeholder="Gib deinen Benutzernamen ein..."
        )
    
    with col2:
        password = st.text_input(
            "Passwort", 
            type="password", 
            key="password_input",
            placeholder="Standard: 4-26-2011"
        )
    
    if st.button("🔐 Anmelden", use_container_width=True):
        # Validierung
        if not username or not password:
            st.warning("⚠️ Bitte Benutzername und Passwort eingeben")
            return
        
        # Authentifizierung über AuthManager
        result, message, role = _auth.authenticate_user(username.strip(), password)
        
        # Ergebnis auswerten
        if result == LoginResult.INVALID_USERNAME:
            st.error(f"❌ {message}")
            return
        
        if result == LoginResult.INVALID_CREDENTIALS:
            st.error(f"❌ {message}")
            return
        
        if result == LoginResult.ACCOUNT_DISABLED:
            st.error(f"🚫 {message}")
            return
        
        if result == LoginResult.ACCOUNT_LOCKED:
            st.error(f"🔒 {message}")
            return
        
        # Login erfolgreich
        if result in [LoginResult.SUCCESS, LoginResult.PASSWORD_CHANGE_REQUIRED]:
            # Prüfe nochmal ob Account aktiv ist
            if not is_user_active(username.strip()):
                st.error("🚫 Dieser Account wurde deaktiviert!")
                return
            
            # Session State setzen
            st.session_state.authentifiziert = True
            st.session_state.username = username.strip()
            st.session_state.user_role = role
            st.session_state.needs_password_change = (result == LoginResult.PASSWORD_CHANGE_REQUIRED)
            
            st.success(f"✅ {message}")
            st.rerun()
    
    # Leaderboard anzeigen
    st.markdown("---")
    leaderboard(sidebar=False)

# === PASSWORT ÄNDERN ===
def password_change_page():
    """Seite zum Passwort ändern"""
    st.title("🔑 Passwort ändern")
    st.warning("⚠️ Du musst dein Passwort ändern, bevor du fortfahren kannst!")
    
    st.markdown("---")
    
    with st.form("password_change_form"):
        old_password = st.text_input(
            "Aktuelles Passwort", 
            type="password",
            help="Falls du das Standard-Passwort verwendest, gib es hier ein"
        )
        
        new_password = st.text_input(
            "Neues Passwort", 
            type="password",
            help="Mindestens 6 Zeichen"
        )
        
        confirm_password = st.text_input(
            "Neues Passwort bestätigen", 
            type="password"
        )
        
        submitted = st.form_submit_button("💾 Passwort ändern", use_container_width=True)
        
        if submitted:
            # Validierung
            if not old_password or not new_password or not confirm_password:
                st.error("❌ Bitte alle Felder ausfüllen!")
                return
            
            if new_password != confirm_password:
                st.error("❌ Die Passwörter stimmen nicht überein!")
                return
            
            if len(new_password) < 6:
                st.error("❌ Das neue Passwort muss mindestens 6 Zeichen haben!")
                return
            
            # Passwort ändern
            success, msg = _auth.change_password(
                st.session_state.username,
                old_password,
                new_password
            )
            
            if success:
                st.success(f"✅ {msg}")
                st.session_state.needs_password_change = False
                st.balloons()
                st.rerun()
            else:
                st.error(f"❌ {msg}")
    
    # Logout Option
    if st.button("🚪 Abmelden"):
        for k in DEFAULT_KEYS:
            st.session_state[k] = DEFAULT_KEYS[k]
        st.rerun()

# === QUIZ PAGE ===
def quiz_page():
    """Haupt-Quiz-Seite"""
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.username}")
        
        if is_admin(st.session_state.username):
            st.success("🔧 Admin-Rechte")
        
        st.markdown("---")
        
        if st.button("🚪 Abmelden", use_container_width=True):
            for k in DEFAULT_KEYS:
                st.session_state[k] = DEFAULT_KEYS[k]
            st.rerun()
        
        st.markdown("---")
        leaderboard(sidebar=True)
    
    # Header
    st.header(f"📘 Quiz-Plattform")
    
    # Quiz-Auswahl
    quiz_names = list(QUIZZES.keys())
    
    if not quiz_names:
        st.error("❌ Keine Quiz verfügbar.")
        return
    
    choice = st.selectbox(
        "📚 Wähle ein Quiz aus:",
        quiz_names,
        help="Wähle das Quiz, das du spielen möchtest"
    )
    
    # Quiz-Wechsel behandeln
    if st.session_state.current_quiz != choice:
        st.session_state.current_quiz = choice
        st.session_state.quiz_step = 0
        st.session_state.quiz_start_time = datetime.now(timezone.utc).isoformat()
        st.session_state.show_results = False
        st.session_state.answered_questions = []
    
    quiz = QUIZZES[choice]
    questions = list(quiz.values())
    idx = st.session_state.quiz_step
    idx = max(0, min(idx, len(questions) - 1))
    question = questions[idx]
    
    # Fortschrittsbalken
    progress = (idx + 1) / len(questions)
    st.progress(progress)
    st.caption(f"Frage {idx + 1} von {len(questions)}")
    
    # Frage anzeigen
    st.markdown(
        f"""
        <div class='quiz-card'>
            <h3>❓ {question['frage']}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Antwortmöglichkeiten
    answer = st.radio(
        "Wähle deine Antwort:",
        question.get("optionen", []),
        key=f"answer_{idx}_{choice}"
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("➡️ Weiter", use_container_width=True):
            if not answer:
                st.warning("⚠️ Bitte wähle eine Antwort aus!")
            else:
                # Antwort speichern
                question_id = f"{choice}_{idx}"
                
                if question_id not in st.session_state.answered_questions:
                    entry = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "username": st.session_state.username,
                        "quiz": choice,
                        "question": question.get("frage"),
                        "answer": answer,
                        "correct": answer == question.get("richtig")
                    }
                    
                    # Lokal speichern
                    from auth import save_answer as local_save_answer
                    local_save_answer(entry)
                    
                    st.session_state.answered_questions.append(question_id)
                
                # Nächste Frage oder Ergebnisse
                if idx < len(questions) - 1:
                    st.session_state.quiz_step = idx + 1
                    st.rerun()
                else:
                    st.session_state.show_results = True
                    end_time = datetime.now(timezone.utc)
                    start_time = datetime.fromisoformat(st.session_state.quiz_start_time.replace('Z', '+00:00'))
                    st.session_state.quiz_duration = end_time - start_time
                    st.rerun()
    
    # Ergebnisse anzeigen
    if st.session_state.show_results:
        st.markdown("---")
        st.success("🎉 Quiz abgeschlossen!")
        
        # Statistiken berechnen
        answers = load_answers()
        quiz_answers = [
            a for a in answers 
            if a.get("username") == st.session_state.username 
            and a.get("quiz") == choice
        ]
        
        if quiz_answers:
            correct = len([a for a in quiz_answers if a.get("correct")])
            total = len(quiz_answers)
            rate = (correct / total * 100) if total > 0 else 0
            
            # Metriken anzeigen
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("✅ Richtige Antworten", f"{correct}/{total}")
            
            with col2:
                st.metric("📊 Erfolgsquote", f"{rate:.1f}%")
            
            with col3:
                if st.session_state.quiz_duration:
                    duration_sec = st.session_state.quiz_duration.total_seconds()
                    st.metric("⏱️ Zeit", f"{int(duration_sec)}s")
            
            # Bewertung
            if rate >= 90:
                st.success("🌟 Hervorragend!")
            elif rate >= 70:
                st.info("👍 Gut gemacht!")
            elif rate >= 50:
                st.warning("📚 Noch Luft nach oben!")
            else:
                st.error("💪 Weiter üben!")
        
        # Leaderboard
        st.markdown("---")
        leaderboard(sidebar=False)
        
        # Neues Quiz starten
        if st.button("🔄 Neues Quiz starten", use_container_width=True):
            st.session_state.quiz_step = 0
            st.session_state.quiz_start_time = datetime.now(timezone.utc).isoformat()
            st.session_state.show_results = False
            st.session_state.answered_questions = []
            st.rerun()

# === MAIN ===
def main():
    """Hauptfunktion"""
    
    # Nicht authentifiziert
    if not st.session_state.authentifiziert:
        login_page()
        return
    
    # Passwort ändern erforderlich
    if st.session_state.needs_password_change:
        password_change_page()
        return
    
    # Account-Status prüfen
    if not is_user_active(st.session_state.username):
        st.error("🚫 Dein Account wurde deaktiviert!")
        for k in DEFAULT_KEYS:
            st.session_state[k] = DEFAULT_KEYS[k]
        st.rerun()
        return
    
    # Admin-Panel oder Quiz
    if is_admin(st.session_state.username):
        show_admin_panel()
    else:
        quiz_page()

if __name__ == "__main__":
    main()