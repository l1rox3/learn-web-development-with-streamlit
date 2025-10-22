import streamlit as st
import sys
import os
import json

# Füge Parent-Directory zum Path hinzu für Imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.auth import AuthManager, UserRole
from datetime import datetime
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
st.set_page_config(
    page_title="Admin",
    page_icon="⚙️",
    layout="wide"
)

auth_manager = AuthManager()
ANSWERS_DIR = "./data/answers"

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
            "text_secondary": "#646b71",
            "accent": "#43474F",
            "accent_hover": "#2b2d33",
            "accent_light": "#f1f2f3",
            "success": "#10b981",
            "error": "#ef4444",
            "warning": "#f59e0b"
        },
        "Dark": {
            "bg": "#0a0a0a",
            "surface": "#1a1a1a",
            "border": "#2a2a2a",
            "text": "#ffffff",
            "text_secondary": "#a0a0a0",
            "accent": "#3b82f6",
            "accent_hover": "#60a5fa",
            "accent_light": "#1e3a8a",
            "success": "#10b981",
            "error": "#ef4444",
            "warning": "#f59e0b"
        },
        "Minimal": {
            "bg": "#fafafa",
            "surface": "#ffffff",
            "border": "#d4d4d4",
            "text": "#0a0a0a",
            "text_secondary": "#737373",
            "accent": "#000000",
            "accent_hover": "#404040",
            "accent_light": "#f5f5f5",
            "success": "#16a34a",
            "error": "#dc2626",
            "warning": "#ea580c"
        }
    }
    return themes.get(theme_name, themes["Light"])

def apply_admin_theme():
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
            max-width: 1400px;
        }}
        
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background: {t['surface']};
            border-right: 1px solid {t['border']};
        }}
        
        [data-testid="stSidebar"] * {{
            color: {t['text']};
        }}
        
        /* Typography */
        h1, h2, h3, h4, h5, h6 {{
            color: {t['text']} !important;
            font-weight: 600 !important;
            letter-spacing: -0.02em;
        }}
        
        p, span, div, label {{
            color: {t['text']} !important;
        }}
        
        /* Buttons */
        .stButton > button {{
            background: {t['accent']};
            color: white !important;
            border: none;
            border-radius: 8px;
            padding: 0.625rem 1.5rem;
            font-weight: 500;
            font-size: 0.9375rem;
            transition: all 0.2s ease;
        }}
        
        .stButton > button:hover {{
            background: {t['accent_hover']};
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}
        
        /* Success Button */
        .success-btn button {{
            background: {t['success']} !important;
        }}
        
        /* Error Button */
        .error-btn button {{
            background: {t['error']} !important;
        }}
        
        /* Inputs */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select {{
            background: {t['bg']} !important;
            border: 1px solid {t['border']} !important;
            border-radius: 8px !important;
            color: {t['text']} !important;
            font-size: 0.9375rem !important;
            padding: 0.625rem !important;
        }}
        
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus {{
            border-color: {t['accent']} !important;
            box-shadow: 0 0 0 3px {t['accent']}20 !important;
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0;
            background: transparent;
            border-bottom: 1px solid {t['border']};
        }}
        
        .stTabs [data-baseweb="tab"] {{
            border-radius: 0;
            color: {t['text_secondary']} !important;
            font-weight: 500;
            padding: 0.75rem 1.5rem;
            border: none;
            background: transparent;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: transparent;
            color: {t['text']} !important;
            border-bottom: 2px solid {t['accent']};
        }}
        
        /* User Card */
        .user-card {{
            background: {t['surface']};
            border: 1px solid {t['border']};
            border-radius: 12px;
            padding: 1.5rem;
            margin: 0.75rem 0;
            transition: all 0.2s ease;
        }}
        
        .user-card:hover {{
            border-color: {t['accent']};
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }}
        
        .user-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }}
        
        .user-name {{
            font-size: 1.125rem;
            font-weight: 600;
            color: {t['text']} !important;
        }}
        
        .user-badge {{
            background: {t['accent_light']};
            color: {t['accent']};
            padding: 0.25rem 0.75rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .user-badge.admin {{
            background: {t['warning']}20;
            color: {t['warning']};
        }}
        
        .user-badge.active {{
            background: {t['success']}20;
            color: {t['success']};
        }}
        
        .user-badge.blocked {{
            background: {t['error']}20;
            color: {t['error']};
        }}
        
        /* Stats Grid */
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
        
        /* Expander */
        .streamlit-expanderHeader {{
            background: {t['surface']} !important;
            border: 1px solid {t['border']} !important;
            border-radius: 8px !important;
        }}
        
        /* Info boxes */
        .stSuccess, .stWarning, .stInfo, .stError {{
            background: {t['surface']} !important;
            border: 1px solid {t['border']} !important;
            border-radius: 8px;
            padding: 1rem !important;
        }}
        
        /* Hide Streamlit branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# ---------------------- DATEN-FUNKTIONEN ----------------------
def load_user_data(username: str):
    """Lädt die Daten eines Benutzers"""
    user_file = os.path.join(ANSWERS_DIR, f"{username}.json")
    if not os.path.exists(user_file):
        return {"username": username, "quizzes": []}
    
    try:
        with open(user_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"username": username, "quizzes": []}

def get_leaderboard(quiz_name: str = None):
    """Erstellt eine Bestenliste"""
    if not os.path.exists(ANSWERS_DIR):
        return []
    
    leaderboard = []
    
    for filename in os.listdir(ANSWERS_DIR):
        if not filename.endswith(".json"):
            continue
        
        username = filename[:-5]
        user_data = load_user_data(username)
        
        quizzes = user_data.get("quizzes", [])
        if quiz_name:
            quizzes = [q for q in quizzes if q.get("quiz_name") == quiz_name]
        
        if not quizzes:
            continue
        
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
    
    leaderboard.sort(key=lambda x: (-x["correct"], x["avg_time"]))
    return leaderboard

def get_available_quizzes():
    """Gibt alle verfügbaren Quiz-Namen zurück"""
    if not os.path.exists(ANSWERS_DIR):
        return []
    
    quiz_names = set()
    for filename in os.listdir(ANSWERS_DIR):
        if not filename.endswith(".json"):
            continue
        
        user_data = load_user_data(filename[:-5])
        for quiz in user_data.get("quizzes", []):
            quiz_names.add(quiz.get("quiz_name", ""))
    
    return sorted(list(quiz_names))

def format_time(seconds: float):
    """Formatiert Sekunden in MM:SS Format"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

def get_user_stats():
    """Gibt Statistiken über alle Benutzer zurück"""
    users = auth_manager.load_users()
    total_users = len(users)
    active_users = sum(1 for u in users.values() if u.active)
    admin_users = sum(1 for u in users.values() if u.role == UserRole.ADMIN)
    
    # Quiz-Statistiken
    total_quizzes = 0
    if os.path.exists(ANSWERS_DIR):
        for filename in os.listdir(ANSWERS_DIR):
            if filename.endswith(".json"):
                user_data = load_user_data(filename[:-5])
                total_quizzes += len(user_data.get("quizzes", []))
    
    return {
        "total": total_users,
        "active": active_users,
        "admins": admin_users,
        "blocked": total_users - active_users,
        "total_quizzes": total_quizzes
    }

# ---------------------- BENUTZERVERWALTUNG ----------------------
def show_user_management(current_admin):
    """Benutzerverwaltung"""
    t = get_theme()
    
    st.markdown("<h2 style='margin-bottom: 1rem;'>👥 Benutzerverwaltung</h2>", unsafe_allow_html=True)
    
    # Statistiken
    stats = get_user_stats()
    
    st.markdown(f'''
    <div class="stats-grid">
        <div class="stats-card">
            <div class="stats-label">Gesamt</div>
            <div class="stats-value">{stats['total']}</div>
        </div>
        <div class="stats-card">
            <div class="stats-label">Aktiv</div>
            <div class="stats-value">{stats['active']}</div>
        </div>
        <div class="stats-card">
            <div class="stats-label">Admins</div>
            <div class="stats-value">{stats['admins']}</div>
        </div>
        <div class="stats-card">
            <div class="stats-label">Blockiert</div>
            <div class="stats-value">{stats['blocked']}</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Neuen Benutzer hinzufügen
    with st.expander("➕ Neuen Benutzer hinzufügen"):
        col1, col2, col3 = st.columns([3, 3, 2])
        
        with col1:
            new_username = st.text_input("Benutzername", key="new_user")
        
        with col2:
            new_password = st.text_input("Passwort", value="4-26-2011", type="password", key="new_pass")
        
        with col3:
            st.write("")
            st.write("")
            if st.button("Hinzufügen", use_container_width=True):
                users = auth_manager.load_users()
                if new_username in users:
                    st.error("Benutzer existiert bereits!")
                else:
                    is_valid, error_msg = auth_manager.is_valid_username(new_username)
                    if not is_valid:
                        st.error(error_msg)
                    else:
                        password_hash, salt = auth_manager.hash_password(new_password)
                        from pages.auth import User
                        
                        users[new_username] = User(
                            username=new_username,
                            password_hash=password_hash,
                            role=UserRole.USER,
                            active=True,
                            created_at=datetime.now(),
                            using_default=True,
                            salt=salt
                        )
                        auth_manager.save_users(users)
                        st.success(f"✓ Benutzer '{new_username}' hinzugefügt")
                        st.rerun()
    
    st.markdown("<h3 style='margin-top: 2rem; margin-bottom: 1rem;'>Benutzer</h3>", unsafe_allow_html=True)
    st.button("Aktualisieren", on_click=st.rerun)
    # Bestehende Benutzer
    users = auth_manager.load_users()
    
    for username, user in users.items():
        if username == current_admin:
            continue
        
        # Status badges
        status_badge = "active" if user.active else "blocked"
        status_text = "Aktiv" if user.active else "Blockiert"
        role_badge = "admin" if user.role == UserRole.ADMIN else "user"
        role_text = "Admin" if user.role == UserRole.ADMIN else "User"
        
        st.markdown(f'''
        <div class="user-card">
            <div class="user-card-header">
                <div>
                    <span class="user-name">{username}</span>
                </div>
                <div style="display: flex; gap: 0.5rem;">
                    <span class="user-badge {status_badge}">{status_text}</span>
                    <span class="user-badge {role_badge}">{role_text}</span>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Aktionen
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if user.active:
                st.markdown('<div class="error-btn">', unsafe_allow_html=True)
                if st.button("🚫 Blockieren", key=f"block_{username}", use_container_width=True):
                    user.active = False
                    auth_manager.save_users(users)
                    st.success(f"✓ '{username}' blockiert")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="success-btn">', unsafe_allow_html=True)
                if st.button("✓ Entblocken", key=f"unblock_{username}", use_container_width=True):
                    user.active = True
                    auth_manager.save_users(users)
                    st.success(f"✓ '{username}' entblockt")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            if user.role == UserRole.ADMIN:
                if st.button("👤 Admin entfernen", key=f"remove_admin_{username}", use_container_width=True):
                    user.role = UserRole.USER
                    auth_manager.save_users(users)
                    st.success(f"✓ '{username}' ist kein Admin mehr")
                    st.rerun()
            else:
                if st.button("👑 Admin machen", key=f"make_admin_{username}", use_container_width=True):
                    user.role = UserRole.ADMIN
                    auth_manager.save_users(users)
                    st.success(f"✓ '{username}' ist jetzt Admin")
                    st.rerun()
 
# ---------------------- BESTENLISTE ----------------------
def show_leaderboard_tab():
    """Bestenliste im Admin-Panel"""
    t = get_theme()
    
    st.markdown("<h2 style='margin-bottom: 1rem;'>🏆 Bestenliste</h2>", unsafe_allow_html=True)
    
    # Quiz-Filter
    available_quizzes = get_available_quizzes()
    
    if not available_quizzes:
        st.info("Noch keine Quiz-Ergebnisse vorhanden")
        return
    
    col1, col2 = st.columns([2, 1])
    with col1:
        quiz_filter = st.selectbox(
            "Kategorie wählen",
            ["Alle Quizze"] + available_quizzes,
            key="admin_leaderboard_filter"
        )
    
    # Bestenliste laden
    selected_quiz = None if quiz_filter == "Alle Quizze" else quiz_filter
    leaderboard = get_leaderboard(selected_quiz)
    
    if not leaderboard:
        st.info("Keine Einträge für diese Kategorie")
        return
    
    # Statistiken
    total_players = len(leaderboard)
    total_attempts = sum(entry["attempts"] for entry in leaderboard)
    total_correct = sum(entry["correct"] for entry in leaderboard)
    total_questions = sum(entry["total"] for entry in leaderboard)
    
    st.markdown(f'''
    <div class="stats-grid">
        <div class="stats-card">
            <div class="stats-label">Spieler</div>
            <div class="stats-value">{total_players}</div>
        </div>
        <div class="stats-card">
            <div class="stats-label">Versuche</div>
            <div class="stats-value">{total_attempts}</div>
        </div>
        <div class="stats-card">
            <div class="stats-label">Erfolgsrate</div>
            <div class="stats-value">{(total_correct/total_questions*100):.0f}%</div>
        </div>
        <div class="stats-card">
            <div class="stats-label">Ø Zeit</div>
            <div class="stats-value" style="font-size: 2rem;">{format_time(sum(e["avg_time"] for e in leaderboard)/len(leaderboard))}</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Rangliste
    st.markdown("<h3 style='margin-top: 2rem; margin-bottom: 1rem;'>Rangliste</h3>", unsafe_allow_html=True)
    
    for rank, entry in enumerate(leaderboard, 1):
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
        
        st.markdown(f'''
        <div class="leaderboard-item">
            <div class="leaderboard-left">
                <div class="leaderboard-rank {rank_class}">{rank_icon}</div>
                <div class="leaderboard-name">{entry['username']}</div>
            </div>
            <div class="leaderboard-right">
                <div class="leaderboard-score">{entry['correct']} / {entry['total']} Punkte</div>
                <div class="leaderboard-time">Ø {format_time(entry['avg_time'])} • {entry['attempts']} Versuche</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

# ---------------------- ANTWORTEN-ÜBERSICHT ----------------------
def show_answers_tab():
    """Zeigt alle Antworten im Detail"""
    st.markdown("<h2 style='margin-bottom: 1rem;'>📋 Antworten-Übersicht</h2>", unsafe_allow_html=True)
    
    if not os.path.exists(ANSWERS_DIR):
        st.info("Noch keine Antworten vorhanden")
        return
    
    # Benutzer-Filter
    usernames = []
    for filename in os.listdir(ANSWERS_DIR):
        if filename.endswith(".json"):
            usernames.append(filename[:-5])
    
    if not usernames:
        st.info("Noch keine Antworten vorhanden")
        return
    
    selected_user = st.selectbox("Benutzer auswählen", ["Alle"] + sorted(usernames))
    
    # Daten laden
    if selected_user == "Alle":
        users_to_show = usernames
    else:
        users_to_show = [selected_user]
    
    for username in users_to_show:
        user_data = load_user_data(username)
        quizzes = user_data.get("quizzes", [])
        
        if not quizzes:
            continue
        
        with st.expander(f"👤 {username} - {len(quizzes)} Quiz(ze)"):
            for idx, quiz in enumerate(quizzes, 1):
                st.markdown(f"**Quiz {idx}: {quiz.get('quiz_name', 'Unbekannt')}**")
                st.markdown(f"- Zeitstempel: {quiz.get('timestamp', 'Unbekannt')[:19]}")
                st.markdown(f"- Ergebnis: {quiz.get('correct', 0)} / {quiz.get('total', 0)} richtig")
                st.markdown(f"- Zeit: {format_time(quiz.get('time_seconds', 0))}")
                
                answers = quiz.get("answers", {})
                if answers:
                    st.markdown("**Antworten:**")
                    for q_id, answer_data in answers.items():
                        correct_icon = "✅" if answer_data.get("correct") else "❌"
                        st.markdown(f"{correct_icon} {answer_data.get('question', 'Keine Frage')}")
                        st.markdown(f"  → Antwort: {answer_data.get('answer', 'Keine Antwort')}")
                
                st.markdown("---")

# ---------------------- SIDEBAR ----------------------
def show_sidebar():
    with st.sidebar:
        t = get_theme()
        
        st.markdown("### Admin-Panel")
        
        if st.session_state.get("logged_in", False):
            st.markdown(f'''
            <div class="user-badge" style="padding: 1rem; margin: 1rem 0; border: 1px solid {t['border']};">
                <div style="font-weight: 600; color: {t['text']};">{st.session_state.username}</div>
                <div style="font-size: 0.875rem; color: {t['text_secondary']}; margin-top: 0.25rem;">
                    Administrator
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
            if st.button("← Zurück", use_container_width=True):
                st.switch_page("main.py")
            
            st.markdown("---")
            
            if st.button("Abmelden", use_container_width=True):
                st.session_state.clear()
                st.switch_page("main.py")

# ---------------------- HAUPTPROGRAMM ----------------------
def main():
    apply_admin_theme()
    
    # Prüfen ob eingeloggt und Admin
    if not st.session_state.get("logged_in", False):
        st.warning("Sie sind nicht eingeloggt!")
        if st.button("Zur Anmeldung"):
            st.switch_page("main.py")
        return
    
    if st.session_state.get("role") != UserRole.ADMIN:
        st.error("Sie haben keine Admin-Berechtigung!")
        if st.button("Zurück"):
            st.switch_page("main.py")
        return
    
    show_sidebar()
    
    current_admin = st.session_state.username
    
    # Header
    t = get_theme()
    st.markdown("<h1 style='margin-bottom: 0.5rem;'>⚙️ Admin-Panel</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: {t['text_secondary']}; margin-bottom: 2rem;'>Verwaltung und Übersicht</p>", unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["👥 Benutzer", "🏆 Bestenliste", "📋 Antworten"])
    
    with tab1:
        show_user_management(current_admin)
    
    with tab2:
        show_leaderboard_tab()
    
    with tab3:
        show_answers_tab()

if __name__ == "__main__":
    main()