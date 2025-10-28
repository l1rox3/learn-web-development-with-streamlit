"""
Quiz App - Main Dashboard
Saubere, optimierte Version mit modernem Gradient-Design

Features:
- Login / Registrierung
- Dashboard mit Quiz, Theme & Admin
- Bestenliste mit Statistiken
- Theme-Selector
- Passwortwechsel
- PDF Datenquelle
- Git Auto-Sync

Created by l1rox3 • 2025
"""

import json
import logging
import os
import subprocess
import threading
import time
from typing import Dict, List, Optional

import streamlit as st
from pages.auth import AuthManager, UserRole, DEFAULT_PASSWORD

# =========================================================
# KONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Quiz Dashboard",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

LOG = logging.getLogger("quiz.main")
LOG.setLevel(logging.INFO)

ANSWERS_DIR = "./data/answers"
SETTINGS_FILE = "./data/settings.json"
PDF_PATH = "./data/data.pdf"

# =========================================================
# SESSION VALIDIERUNG
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

# =========================================================
# THEMES
# =========================================================
THEMES: Dict[str, Dict[str, str]] = {
    "Purple Dream": {
        "name": "Purple Dream",
        "bg": "linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)",
        "surface": "rgba(255,255,255,0.05)",
        "border": "rgba(255,255,255,0.1)",
        "text": "#ffffff",
        "text_secondary": "rgba(255,255,255,0.7)",
        "accent": "#667eea",
        "accent_hover": "#764ba2",
        "card_gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    },
    "Ocean Blue": {
        "name": "Ocean Blue",
        "bg": "linear-gradient(135deg, #0a192f 0%, #112240 50%, #1a365d 100%)",
        "surface": "rgba(255,255,255,0.05)",
        "border": "rgba(255,255,255,0.1)",
        "text": "#ffffff",
        "text_secondary": "rgba(255,255,255,0.7)",
        "accent": "#3b82f6",
        "accent_hover": "#60a5fa",
        "card_gradient": "linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)",
    },
    "Dark Minimal": {
        "name": "Dark Minimal",
        "bg": "linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0a0a0a 100%)",
        "surface": "rgba(255,255,255,0.05)",
        "border": "rgba(255,255,255,0.1)",
        "text": "#ffffff",
        "text_secondary": "rgba(255,255,255,0.6)",
        "accent": "#ffffff",
        "accent_hover": "#e5e5e5",
        "card_gradient": "linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%)",
    },
}

# =========================================================
# SETTINGS FUNKTIONEN
# =========================================================
def load_settings() -> Dict:
    """Lädt App-Einstellungen."""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
                if isinstance(settings, dict) and "current_theme" in settings:
                    return settings
    except Exception as exc:
        LOG.exception("Fehler beim Laden der Einstellungen: %s", exc)
    return {"current_theme": "Purple Dream", "custom_theme": None}


def save_settings(settings: Dict) -> None:
    """Speichert App-Einstellungen."""
    try:
        os.makedirs(os.path.dirname(SETTINGS_FILE) or "./data", exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except Exception as exc:
        LOG.exception("Fehler beim Speichern der Einstellungen: %s", exc)


def get_current_theme() -> Dict[str, str]:
    """Gibt aktuelles Theme zurück."""
    settings = load_settings()
    theme_name = settings.get("current_theme", "Purple Dream")
    return THEMES.get(theme_name, THEMES["Purple Dream"])

# =========================================================
# STYLING
# =========================================================
def apply_theme() -> None:
    """Wendet modernes Theme mit Gradients an."""
    t = get_current_theme()
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');

    /* Global Styles */
    html, body, .stApp {{
        background: {t['bg']};
        color: {t['text']};
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 1200px;
    }}

    /* Header Styles */
    .main-header {{
        background: {t['card_gradient']};
        padding: 2.5rem;
        border-radius: 25px;
        text-align: center;
        margin-bottom: 2.5rem;
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
    }}

    .main-title {{
        font-size: 3rem;
        font-weight: 800;
        color: white;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        letter-spacing: -0.02em;
    }}

    .main-subtitle {{
        font-size: 1.3rem;
        color: rgba(255,255,255,0.9);
        margin-top: 0.5rem;
        font-weight: 500;
    }}

    /* Cards */
    .action-card {{
        background: {t['surface']};
        border: 1px solid {t['border']};
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
        height: 100%;
    }}

    .action-card:hover {{
        transform: translateY(-8px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.3);
        border-color: {t['accent']};
    }}

    .action-card h3 {{
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }}

    .action-card p {{
        color: {t['text_secondary']};
        font-size: 1.1rem;
    }}

    /* Stats Cards */
    .stats-card {{
        background: {t['surface']};
        border: 1px solid {t['border']};
        border-radius: 18px;
        padding: 1.5rem;
        text-align: center;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }}

    .stats-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }}

    .stats-label {{
        color: {t['text_secondary']};
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }}

    .stats-value {{
        color: {t['text']};
        font-size: 2.5rem;
        font-weight: 800;
    }}

    /* Leaderboard */
    .leaderboard-item {{
        background: {t['surface']};
        border: 1px solid {t['border']};
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.8rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }}

    .leaderboard-item:hover {{
        transform: translateX(8px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
        border-color: {t['accent']};
    }}

    .leaderboard-rank {{
        font-weight: 800;
        color: {t['accent']};
        font-size: 1.5rem;
        min-width: 3.5rem;
        text-align: center;
    }}

    /* Buttons */
    .stButton > button {{
        background: {t['card_gradient']} !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 1rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        transition: all 0.3s ease !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    .stButton > button:hover {{
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.4) !important;
    }}

    /* Inputs */
    input, textarea, select {{
        background: {t['surface']} !important;
        border: 1px solid {t['border']} !important;
        border-radius: 12px !important;
        color: {t['text']} !important;
        padding: 0.8rem !important;
        font-size: 1rem !important;
    }}

    input:focus, textarea:focus, select:focus {{
        border-color: {t['accent']} !important;
        box-shadow: 0 0 0 2px {t['accent']}33 !important;
    }}

    /* PDF Card */
    .pdf-card {{
        background: {t['surface']};
        border: 1px solid {t['border']};
        border-radius: 20px;
        padding: 2rem;
        backdrop-filter: blur(10px);
        margin: 1rem 0;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 1rem;
        background: {t['surface']};
        padding: 0.5rem;
        border-radius: 15px;
        border: 1px solid {t['border']};
    }}

    .stTabs [data-baseweb="tab"] {{
        color: {t['text_secondary']};
        border-radius: 10px;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
    }}

    .stTabs [aria-selected="true"] {{
        background: {t['card_gradient']};
        color: white;
    }}

    /* Theme Preview */
    .theme-preview {{
        border: 2px solid {t['border']};
        border-radius: 15px;
        padding: 1.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
    }}

    .theme-preview:hover {{
        transform: scale(1.05);
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }}

    .theme-preview.active {{
        border-color: {t['accent']};
        background: {t['surface']};
        box-shadow: 0 0 0 3px {t['accent']}33;
    }}

    /* Login Card */
    .login-card {{
        background: {t['surface']};
        border: 1px solid {t['border']};
        border-radius: 25px;
        padding: 3rem;
        max-width: 500px;
        margin: 4rem auto;
        backdrop-filter: blur(10px);
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }}

    /* Footer */
    .footer {{
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: {t['surface']};
        border-top: 1px solid {t['border']};
        padding: 1rem;
        text-align: center;
        backdrop-filter: blur(10px);
        z-index: 999;
    }}

    .footer-text {{
        color: {t['text_secondary']};
        font-size: 0.9rem;
        margin: 0;
    }}

    .footer-link {{
        color: {t['accent']};
        text-decoration: none;
        font-weight: 700;
        transition: all 0.2s ease;
    }}

    .footer-link:hover {{
        color: {t['accent_hover']};
        text-decoration: underline;
    }}

    /* Hide Streamlit Elements */
    #MainMenu, header, footer {{visibility: hidden;}}
    .stDeployButton {{display: none;}}
    
    /* Spacing */
    h1, h2, h3 {{
        color: {t['text']};
        font-weight: 700;
    }}
    
    p, span, div, label {{
        color: {t['text']};
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# =========================================================
# SESSION INIT
# =========================================================
def init_session() -> None:
    """Initialisiert Session State."""
    if "initialized" in st.session_state:
        return

    st.session_state.setdefault("logged_in", False)
    st.session_state.setdefault("username", "")
    st.session_state.setdefault("role", UserRole.USER)
    st.session_state.setdefault("using_default", False)
    st.session_state.setdefault("skip_password_change", False)
    st.session_state.setdefault("show_theme_selector", False)
    st.session_state.setdefault("show_leaderboard", False)
    st.session_state.setdefault("show_pdf_data", False)
    st.session_state.setdefault("initialized", True)
    LOG.debug("Session initialisiert")

# =========================================================
# DATA FUNKTIONEN
# =========================================================
def load_user_data(username: str) -> Dict:
    """Lädt Benutzerdaten mit runs."""
    user_file = os.path.join(ANSWERS_DIR, f"{username}.json")
    if not os.path.exists(user_file):
        return {"username": username, "runs": []}
    try:
        with open(user_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Migration: alte "quizzes" zu "runs"
            if "quizzes" in data and "runs" not in data:
                data["runs"] = data.pop("quizzes")
            if "runs" not in data:
                data["runs"] = []
            return data
    except Exception:
        LOG.exception("Fehler beim Laden von Benutzerdaten für %s", username)
        return {"username": username, "runs": []}


def get_all_runs() -> List[Dict]:
    """Lädt alle Runs aller Benutzer."""
    if not os.path.exists(ANSWERS_DIR):
        return []
    
    all_runs = []
    for filename in os.listdir(ANSWERS_DIR):
        if not filename.endswith(".json"):
            continue
        username = filename[:-5]
        user_data = load_user_data(username)
        for run in user_data.get("runs", []):
            run_copy = run.copy()
            run_copy["username"] = username
            all_runs.append(run_copy)
    
    return all_runs


def get_leaderboard() -> List[Dict]:
    """Erstellt Bestenliste aus allen Runs."""
    all_runs = get_all_runs()
    if not all_runs:
        return []
    
    # Sortiere nach Prozentsatz (absteigend), dann nach Zeit (aufsteigend)
    all_runs.sort(key=lambda x: (-x.get("percentage", 0), x.get("time_seconds", 999999)))
    return all_runs[:50]  # Top 50


def format_time(seconds: float) -> str:
    """Formatiert Sekunden als MM:SS."""
    try:
        s = int(seconds)
    except Exception:
        s = 0
    minutes = s // 60
    secs = s % 60
    return f"{minutes:02d}:{secs:02d}"

# =========================================================
# GIT AUTO-SYNC
# =========================================================
def git_commit_push():
    """Committet und pusht Änderungen."""
    try:
        subprocess.run(["git", "add", "."], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "commit", "-m", "auto update"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "push"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def git_pull_loop(interval=15):
    """Zieht Änderungen im Hintergrund."""
    while True:
        try:
            subprocess.run(["git", "pull", "--no-edit"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
        time.sleep(interval)


def file_watcher():
    """Überwacht Dateiänderungen."""
    last_snapshot = snapshot_dir(".")
    while True:
        time.sleep(5)
        new_snapshot = snapshot_dir(".")
        if new_snapshot != last_snapshot:
            last_snapshot = new_snapshot
            git_commit_push()


def snapshot_dir(path):
    """Erstellt Verzeichnis-Snapshot."""
    snapshot = {}
    for root, _, files in os.walk(path):
        for f in files:
            if ".git" in root:
                continue
            file_path = os.path.join(root, f)
            try:
                snapshot[file_path] = os.path.getmtime(file_path)
            except Exception:
                pass
    return snapshot


def autorun():
    """Startet Auto-Sync."""
    if not os.environ.get("GIT_SYNC_ACTIVE"):
        threading.Thread(target=git_pull_loop, args=(15,), daemon=True).start()
        os.environ["GIT_SYNC_ACTIVE"] = "1"
    watcher_thread = threading.Thread(target=file_watcher, daemon=True)
    watcher_thread.start()

# =========================================================
# UI KOMPONENTEN
# =========================================================
def render_footer():
    """Zeigt Footer mit Credits."""
    t = get_current_theme()
    st.markdown(f"""
    <div class="footer">
        <p class="footer-text">
            Created by <a href="#" class="footer-link">l1rox3</a> • 2025 
            | Made for joyful learning xdxd 
            | <span style="color: {t['accent']};">Quiz App v2.0</span>
        </p>
    </div>
    """, unsafe_allow_html=True)


def show_login() -> None:
    """Login-Seite."""
    apply_theme()
    t = get_current_theme()

    st.markdown(f"""
    <div class="main-header">
        <h1 class="main-title">Quiz Dashboard</h1>
        <p class="main-subtitle">Teste dein Wissen</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; margin-bottom:2rem;'>Anmelden</h2>", unsafe_allow_html=True)

    username = st.text_input("Benutzername", key="login_user", placeholder="dein.name")
    password = st.text_input("Passwort", type="password", key="login_pass", placeholder="••••••••")

    if st.button("🚀 Anmelden", use_container_width=True):
        if not username or not password:
            st.warning("Bitte alle Felder ausfüllen")
            return
        try:
            success, message, using_default = auth_manager.authenticate_user(username, password)
        except Exception as exc:
            LOG.exception("Fehler bei der Authentifizierung: %s", exc)
            st.error("Beim Anmelden ist ein Fehler aufgetreten.")
            return

        if success:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.using_default = using_default
            try:
                users = auth_manager.load_users()
                st.session_state.role = users.get(username).role if username in users else UserRole.USER
            except Exception:
                st.session_state.role = UserRole.USER
            st.success(message)
            st.rerun()
        else:
            st.error(message)

    st.markdown('</div>', unsafe_allow_html=True)
    render_footer()


def show_password_change() -> None:
    """Passwort-Änderung."""
    apply_theme()
    t = get_current_theme()

    st.markdown(f"""
    <div class="main-header">
        <h1 class="main-title">🔐 Passwort ändern</h1>
        <p class="main-subtitle">Ändere dein Standard-Passwort für mehr Sicherheit</p>
    </div>
    """, unsafe_allow_html=True)

    st.warning("⚠️ Du verwendest noch das Standard-Passwort!")

    st.markdown('<div class="login-card">', unsafe_allow_html=True)

    old_pw = st.text_input("Aktuelles Passwort", type="password", key="pc_old_pw")
    new_pw = st.text_input("Neues Passwort", type="password", key="pc_new_pw")
    confirm_pw = st.text_input("Passwort bestätigen", type="password", key="pc_confirm_pw")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Passwort ändern", use_container_width=True):
            if not old_pw or not new_pw or not confirm_pw:
                st.warning("Bitte alle Felder ausfüllen")
            elif new_pw != confirm_pw:
                st.error("Passwörter stimmen nicht überein")
            else:
                try:
                    success, msg = auth_manager.change_password(
                        st.session_state.username, old_pw, new_pw
                    )
                    if success:
                        st.success(msg)
                        st.session_state.using_default = False
                        st.rerun()
                    else:
                        st.error(msg)
                except Exception:
                    LOG.exception("Fehler beim Ändern des Passworts.")
                    st.error("Beim Ändern des Passworts ist ein Fehler aufgetreten.")
    with col2:
        if st.button("⏭️ Später ändern", use_container_width=True):
            st.session_state.skip_password_change = True
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    render_footer()


def show_leaderboard_page() -> None:
    """Bestenliste mit allen Runs."""
    leaderboard = get_leaderboard()
    
    if not leaderboard:
        st.info("📊 Noch keine Quiz-Ergebnisse vorhanden. Spiele dein erstes Quiz!")
        return

    # Global Stats
    all_runs = get_all_runs()
    total_runs = len(all_runs)
    total_correct = sum(r.get("correct", 0) for r in all_runs)
    total_questions = sum(r.get("total", 0) for r in all_runs)
    success_rate = (total_correct / total_questions * 100) if total_questions > 0 else 0
    unique_players = len(set(r.get("username", "") for r in all_runs))

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-label">👥 Spieler</div>
            <div class="stats-value">{unique_players}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-label">🎮 Total Runs</div>
            <div class="stats-value">{total_runs}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-label">📈 Erfolgsrate</div>
            <div class="stats-value">{success_rate:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-label">✅ Richtige</div>
            <div class="stats-value">{total_correct}/{total_questions}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<h3 style='margin-top: 2rem; margin-bottom: 1rem;'>🏆 Top 50 Rangliste</h3>", unsafe_allow_html=True)
    
    current_username = st.session_state.get("username", "")
    for rank, entry in enumerate(leaderboard, 1):
        is_current = entry.get("username") == current_username
        rank_icon = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
        badge = '<span style="background:linear-gradient(135deg, #667eea, #764ba2);color:#fff;padding:0.2rem 0.6rem;border-radius:8px;margin-left:0.5rem;font-weight:700;">Du</span>' if is_current else ""
        
        st.markdown(f"""
        <div class="leaderboard-item">
            <div style="display:flex;align-items:center;gap:1.5rem;flex:1">
                <div class="leaderboard-rank">{rank_icon}</div>
                <div>
                    <div style="font-weight:700;font-size:1.1rem">{entry.get('username', 'Unknown')}{badge}</div>
                    <div style="font-size:0.9rem;color:rgba(255,255,255,0.6)">
                        🆔 {entry.get('run_id', 'N/A')} | {entry.get('quiz_name', 'Unknown Quiz')}
                    </div>
                </div>
            </div>
            <div style="text-align:right">
                <div style="font-weight:700;font-size:1.3rem;color:#667eea">{entry.get('percentage', 0):.1f}%</div>
                <div style="font-size:0.9rem;color:rgba(255,255,255,0.6)">
                    🎯 {entry.get('correct', 0)}/{entry.get('total', 0)} | ⏱️ {format_time(entry.get('time_seconds', 0))}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def show_pdf_data_page() -> None:
    """Zeigt PDF-Datenquelle und alle Ergebnisse."""
    st.markdown("<h3 style='margin-bottom: 1.5rem;'>📄 Quiz-Datenquelle</h3>", unsafe_allow_html=True)
    
    # PDF Info
    if os.path.exists(PDF_PATH):
        file_size = os.path.getsize(PDF_PATH) / 1024  # KB
        st.markdown(f"""
        <div class="pdf-card">
            <h4 style="margin:0 0 1rem 0">📕 Hinduismus - Kleidung und Tiere</h4>
            <p style="color:rgba(255,255,255,0.7);margin:0">
                📁 Pfad: <code>./data/data.pdf</code><br>
                📊 Größe: {file_size:.1f} KB<br>
                ✅ Status: Verfügbar
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Download Button
        with open(PDF_PATH, "rb") as pdf_file:
            st.download_button(
                label="📥 PDF herunterladen",
                data=pdf_file,
                file_name="hinduismus_quiz_data.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.warning("⚠️ PDF-Datei nicht gefunden unter: ./data/data.pdf")
    
    st.markdown("<h3 style='margin: 2rem 0 1rem 0;'>📊 Alle Quiz-Ergebnisse</h3>", unsafe_allow_html=True)
    
    all_runs = get_all_runs()
    
    if not all_runs:
        st.info("Noch keine Quiz-Ergebnisse vorhanden.")
        return
    
    # Statistiken
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-label">Gesamt Durchläufe</div>
            <div class="stats-value">{len(all_runs)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_score = sum(r.get("percentage", 0) for r in all_runs) / len(all_runs)
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-label">Ø Erfolgsrate</div>
            <div class="stats-value">{avg_score:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        perfect_scores = sum(1 for r in all_runs if r.get("percentage", 0) == 100)
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-label">🌟 Perfekt</div>
            <div class="stats-value">{perfect_scores}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Filter
    st.markdown("<div style='margin: 2rem 0 1rem 0;'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        filter_user = st.selectbox(
            "Nach Benutzer filtern:",
            ["Alle"] + sorted(set(r.get("username", "") for r in all_runs))
        )
    with col2:
        sort_by = st.selectbox(
            "Sortieren nach:",
            ["Neueste zuerst", "Beste zuerst", "Schnellste zuerst"]
        )
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Filtern
    filtered_runs = all_runs
    if filter_user != "Alle":
        filtered_runs = [r for r in filtered_runs if r.get("username") == filter_user]
    
    # Sortieren
    if sort_by == "Neueste zuerst":
        filtered_runs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    elif sort_by == "Beste zuerst":
        filtered_runs.sort(key=lambda x: x.get("percentage", 0), reverse=True)
    else:  # Schnellste zuerst
        filtered_runs.sort(key=lambda x: x.get("time_seconds", 999999))
    
    # Anzeige
    for run in filtered_runs:
        timestamp = run.get("timestamp", "")
        if timestamp:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%d.%m.%Y %H:%M")
            except:
                time_str = timestamp[:16]
        else:
            time_str = "Unbekannt"
        
        percentage = run.get("percentage", 0)
        color = "#38ef7d" if percentage >= 80 else "#f45c43" if percentage < 60 else "#667eea"
        
        with st.expander(f"🆔 {run.get('run_id', 'N/A')} | {run.get('username', 'Unknown')} | {percentage:.1f}% | {time_str}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Quiz:** {run.get('quiz_name', 'Unknown')}")
                st.markdown(f"**Benutzer:** {run.get('username', 'Unknown')}")
                st.markdown(f"**Run-ID:** `{run.get('run_id', 'N/A')}`")
            with col2:
                st.markdown(f"**Ergebnis:** {run.get('correct', 0)}/{run.get('total', 0)}")
                st.markdown(f"**Erfolgsrate:** <span style='color:{color};font-weight:700'>{percentage:.1f}%</span>", unsafe_allow_html=True)
                st.markdown(f"**Zeit:** {format_time(run.get('time_seconds', 0))}")
            with col3:
                st.markdown(f"**Datum:** {time_str}")
            
            # Detaillierte Antworten
            detailed = run.get("detailed_answers", [])
            if detailed:
                st.markdown("---")
                st.markdown("**📋 Detaillierte Antworten:**")
                for i, answer in enumerate(detailed, 1):
                    status = "✅" if answer.get("is_correct") else "❌"
                    st.markdown(f"""
                    **{i}. {answer.get('question', 'N/A')}**  
                    {status} Deine Antwort: {answer.get('selected', 'N/A')}  
                    {'✓ Richtig!' if answer.get('is_correct') else f"Richtige Antwort: {answer.get('correct', 'N/A')}"}
                    """)


def show_theme_selector() -> None:
    """Theme-Auswahl."""
    st.markdown("<h3 style='margin-bottom: 1.5rem;'>🎨 Wähle dein Design</h3>", unsafe_allow_html=True)
    settings = load_settings()
    current_theme = settings.get("current_theme", "Purple Dream")

    cols = st.columns(3)
    for idx, (theme_name, theme_data) in enumerate(THEMES.items()):
        with cols[idx]:
            is_active = theme_name == current_theme
            active_class = "active" if is_active else ""
            st.markdown(f"""
            <div class="theme-preview {active_class}">
                <div style="width:100%;height:80px;background:{theme_data['card_gradient']};border-radius:10px;margin-bottom:1rem"></div>
                <h4 style="margin:0;color:{theme_data['text']}">{theme_data['name']}</h4>
            </div>
            """, unsafe_allow_html=True)
            if st.button("✓ Aktiv" if is_active else "Auswählen", key=f"theme_{theme_name}", use_container_width=True, disabled=is_active):
                settings["current_theme"] = theme_name
                save_settings(settings)
                st.success(f"✅ Theme '{theme_name}' aktiviert!")
                time.sleep(0.5)
                st.rerun()


def show_dashboard() -> None:
    """Hauptdashboard."""
    apply_theme()
    
    st.markdown(f"""
    <div class="main-header">
        <h1 class="main-title">👋 Willkommen, {st.session_state.username}!</h1>
        <p class="main-subtitle">Bereit für deine nächste Herausforderung?</p>
    </div>
    """, unsafe_allow_html=True)

    # User Stats
    user_data = load_user_data(st.session_state.username)
    runs = user_data.get("runs", [])
    total_runs = len(runs)
    total_correct = sum(r.get("correct", 0) for r in runs)
    total_questions = sum(r.get("total", 0) for r in runs)
    success_rate = (total_correct / total_questions * 100) if total_questions > 0 else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-label">🎮 Durchläufe</div>
            <div class="stats-value">{total_runs}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-label">✅ Richtige Antworten</div>
            <div class="stats-value">{total_correct}/{total_questions}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-label">📈 Erfolgsrate</div>
            <div class="stats-value">{success_rate:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    # Action Cards - 4 Spalten
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="action-card">
            <h3>📝</h3>
            <h3>Quiz</h3>
            <p>Starte ein Quiz</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Zum Quiz", key="btn_quiz", use_container_width=True):
            st.switch_page("pages/quizzes.py")
    
    with col2:
        st.markdown("""
        <div class="action-card">
            <h3>🏆</h3>
            <h3>Bestenliste</h3>
            <p>Top Spieler</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Rangliste", key="btn_leaderboard", use_container_width=True):
            st.session_state.show_leaderboard = True
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="action-card">
            <h3>📄</h3>
            <h3>Daten</h3>
            <p>PDF & Ergebnisse</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Daten", key="btn_pdf", use_container_width=True):
            st.session_state.show_pdf_data = True
            st.rerun()
    
    with col4:
        st.markdown("""
        <div class="action-card">
            <h3>🎨</h3>
            <h3>Design</h3>
            <p>Theme ändern</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Theme", key="btn_theme", use_container_width=True):
            st.session_state.show_theme_selector = True
            st.rerun()

    # Admin Bereich
    if st.session_state.role == UserRole.ADMIN:
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="action-card">
            <h3>⚙️</h3>
            <h3>Admin-Bereich</h3>
            <p>Benutzerverwaltung und Einstellungen</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Zum Admin-Panel", key="btn_admin", use_container_width=True):
            st.switch_page("pages/admin.py")

    # Logout Button
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    if st.button("Abmelden", key="btn_logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    render_footer()


def main():
    """Hauptfunktion."""
    init_session()
    
    # Auto-Sync starten
    try:
        autorun()
    except Exception as exc:
        LOG.warning("Auto-Sync konnte nicht gestartet werden: %s", exc)

    # Login Check
    if not st.session_state.get("logged_in"):
        show_login()
        return

    # Passwort-Änderung erzwingen
    if st.session_state.get("using_default") and not st.session_state.get("skip_password_change"):
        show_password_change()
        return

    # PDF & Data Page
    if st.session_state.get("show_pdf_data"):
        apply_theme()
        st.markdown(f"""
        <div class="main-header">
            <h1 class="main-title">📄 Quiz-Daten & Ergebnisse</h1>
            <p class="main-subtitle">PDF-Quelle und alle Durchläufe</p>
        </div>
        """, unsafe_allow_html=True)
        
        show_pdf_data_page()
        
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
        if st.button("← Zurück zum Dashboard", use_container_width=True):
            st.session_state.show_pdf_data = False
            st.rerun()
        
        render_footer()
        return

    # Theme Selector
    if st.session_state.get("show_theme_selector"):
        apply_theme()
        st.markdown(f"""
        <div class="main-header">
            <h1 class="main-title">🎨 Design anpassen</h1>
            <p class="main-subtitle">Wähle dein Lieblingstheme</p>
        </div>
        """, unsafe_allow_html=True)
        
        show_theme_selector()
        
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
        if st.button("← Zurück zum Dashboard", use_container_width=True):
            st.session_state.show_theme_selector = False
            st.rerun()
        
        render_footer()
        return

    # Bestenliste
    if st.session_state.get("show_leaderboard"):
        apply_theme()
        st.markdown(f"""
        <div class="main-header">
            <h1 class="main-title">🏆 Bestenliste</h1>
            <p class="main-subtitle">Die besten Quiz-Champions</p>
        </div>
        """, unsafe_allow_html=True)
        
        show_leaderboard_page()
        
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
        if st.button("← Zurück zum Dashboard", use_container_width=True):
            st.session_state.show_leaderboard = False
            st.rerun()
        
        render_footer()
        return

    # Haupt-Dashboard
    show_dashboard()


if __name__ == "__main__":
    main()