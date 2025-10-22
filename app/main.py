# main.py
"""
Saubere, optimierte Version von main.py für die Quiz-App.

Features:
- Login / Registrierung via AuthManager
- Dashboard (Start Quiz, Theme, Admin)
- Passwortwechsel, Theme-Selector
- Bestenliste (Leaderboard) aus ./data/answers/*.json
- Verbesserte Session-Initialisierung & Fehlerbehandlung
- Modernisiertes, aber kompaktes CSS/Theming
"""

import json
import logging
import os
from typing import Dict, List, Optional

import streamlit as st

# Lokale Module (wie in deinem Projekt)
from pages.auth import AuthManager, UserRole, DEFAULT_PASSWORD


# ---------------------- Konfiguration ----------------------
st.set_page_config(page_title="Quiz", page_icon="📝", layout="wide")

LOG = logging.getLogger("quiz.main")
LOG.setLevel(logging.INFO)

auth_manager = AuthManager()
ANSWERS_DIR = "./data/answers"
SETTINGS_FILE = "./data/settings.json"

# ---------------------- Themes ----------------------
THEMES: Dict[str, Dict[str, str]] = {
    "Light": {
        "name": "Light",
        "bg": "#ffffff",
        "surface": "#f8f9fa",
        "border": "#e9ecef",
        "text": "#1a1a1a",
        "text_secondary": "#646b71",
        "accent": "#43474F",
        "accent_hover": "#2b2d33",
        "accent_light": "#f1f2f3",
    },
    "Dark": {
        "name": "Dark",
        "bg": "#0a0a0a",
        "surface": "#1a1a1a",
        "border": "#2a2a2a",
        "text": "#ffffff",
        "text_secondary": "#a0a0a0",
        "accent": "#3b82f6",
        "accent_hover": "#60a5fa",
        "accent_light": "#1e3a8a",
    },
    "Minimal": {
        "name": "Minimal",
        "bg": "#fafafa",
        "surface": "#ffffff",
        "border": "#d4d4d4",
        "text": "#0a0a0a",
        "text_secondary": "#737373",
        "accent": "#000000",
        "accent_hover": "#404040",
        "accent_light": "#f5f5f5",
    },
}


# ---------------------- Settings (load / save) ----------------------
def load_settings() -> Dict:
    """Lädt die App-Einstellungen (z. B. aktuelles Theme)."""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
                if isinstance(settings, dict) and "current_theme" in settings:
                    return settings
    except Exception as exc:  # pragma: no cover - best effort
        LOG.exception("Fehler beim Laden der Einstellungen: %s", exc)
    return {"current_theme": "Light", "custom_theme": None}


def save_settings(settings: Dict) -> None:
    """Speichert die App-Einstellungen sicher ab."""
    try:
        os.makedirs(os.path.dirname(SETTINGS_FILE) or "./data", exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except Exception as exc:
        LOG.exception("Fehler beim Speichern der Einstellungen: %s", exc)


def get_current_theme() -> Dict[str, str]:
    settings = load_settings()
    theme_name = settings.get("current_theme", "Light")
    return THEMES.get(theme_name, THEMES["Light"])


# ---------------------- Styling (apply theme) ----------------------
def apply_theme() -> None:
    """Stellt CSS basierend auf dem aktuellen Theme bereit."""
    t = get_current_theme()
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

    html, body, .stApp {{
        background: {t['bg']};
        color: {t['text']};
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif;
        transition: background 0.25s ease;
    }}

    .block-container {{
        padding-top: 3rem;
        padding-bottom: 3rem;
        max-width: 1150px;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: {t['surface']};
        border-right: 1px solid {t['border']};
        padding: 1rem;
    }}
    [data-testid="stSidebar"] * {{ color: {t['text']}; }}

    /* Buttons */
    .stButton > button {{
        background: linear-gradient(135deg, {t['accent']} 0%, {t['accent_hover']} 100%) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1rem !important;
        font-weight: 600 !important;
        box-shadow: 0 6px 18px rgba(0,0,0,0.12);
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }}
    .stButton > button:hover {{ transform: translateY(-3px); }}

    /* Inputs */
    input, textarea, select {{
        background: {t['surface']} !important;
        border: 1px solid {t['border']} !important;
        border-radius: 8px !important;
        color: {t['text']} !important;
        padding: 0.5rem !important;
    }}

    /* Cards */
    .card, .action-card, .stats-card, .leaderboard-item {{
        background: {t['surface']};
        border: 1px solid {t['border']};
        border-radius: 14px;
        padding: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .card:hover, .action-card:hover, .stats-card:hover {{
        transform: translateY(-6px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.09);
    }}

    /* Typo */
    h1 {{ font-weight: 700; letter-spacing: -0.02em; }}
    h2, h3, h4 {{ font-weight: 600; }}
    p, span, div, label {{ color: {t['text']} !important; }}

    /* Leaderboard */
    .leaderboard-item {{
        display:flex;
        justify-content:space-between;
        align-items:center;
        gap: 1rem;
    }}
    .leaderboard-rank {{ font-weight:800; color: {t['accent']}; }}

    /* Theme preview */
    .theme-preview {{
        border: 2px solid {t['border']};
        border-radius: 8px;
        padding: 0.75rem;
        cursor: pointer;
    }}
    .theme-preview.active {{ border-color: {t['accent']}; background: {t['accent']}10; }}

    /* Hide default Streamlit header/footer */
    #MainMenu, header, footer {{ visibility: hidden; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# ---------------------- Session init ----------------------
def init_session() -> None:
    """Initialisiert benötigte session_state Keys einmalig."""
    if "initialized" in st.session_state:
        return

    st.session_state.setdefault("logged_in", False)
    st.session_state.setdefault("username", "")
    st.session_state.setdefault("role", UserRole.USER)
    st.session_state.setdefault("using_default", False)
    st.session_state.setdefault("skip_password_change", False)
    st.session_state.setdefault("show_theme_selector", False)
    st.session_state.setdefault("initialized", True)
    LOG.debug("Session initialisiert")


# ---------------------- Leaderboard / Data helpers ----------------------
def load_user_data(username: str) -> Dict:
    """Lädt user-spezifische Ergebnisse aus ANSWERS_DIR/<username>.json."""
    user_file = os.path.join(ANSWERS_DIR, f"{username}.json")
    if not os.path.exists(user_file):
        return {"username": username, "quizzes": []}
    try:
        with open(user_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        LOG.exception("Fehler beim Laden von Benutzerdaten für %s", username)
        return {"username": username, "quizzes": []}


def get_available_quizzes() -> List[str]:
    """Ermittelt die verschiedenen Quiz-Namen, die in ANSWERS_DIR gespeichert sind."""
    if not os.path.exists(ANSWERS_DIR):
        return []
    quiz_names = set()
    for filename in os.listdir(ANSWERS_DIR):
        if not filename.endswith(".json"):
            continue
        ud = load_user_data(filename[:-5])
        for q in ud.get("quizzes", []):
            name = q.get("quiz_name", "")
            if name:
                quiz_names.add(name)
    return sorted(quiz_names)


def get_leaderboard(quiz_name: Optional[str] = None) -> List[Dict]:
    """Erstellt eine Bestenliste (sortiert nach korrekten Punkten und avg_time)."""
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
        total_correct = sum(int(q.get("correct", 0)) for q in quizzes)
        total_questions = sum(int(q.get("total", 0)) for q in quizzes)
        total_time = sum(float(q.get("time_seconds", 0)) for q in quizzes)
        avg_time = total_time / len(quizzes) if quizzes else 0
        leaderboard.append(
            {
                "username": username,
                "correct": total_correct,
                "total": total_questions,
                "avg_time": avg_time,
                "attempts": len(quizzes),
            }
        )
    leaderboard.sort(key=lambda x: (-x["correct"], x["avg_time"]))
    return leaderboard


def format_time(seconds: float) -> str:
    """Format seconds as MM:SS."""
    try:
        s = int(seconds)
    except Exception:
        s = 0
    minutes = s // 60
    secs = s % 60
    return f"{minutes:02d}:{secs:02d}"


# ---------------------- UI / Components ----------------------
def render_sidebar() -> None:
    """Sidebar mit Navigation und Benutzer-Informationen."""
    with st.sidebar:
        t = get_current_theme()
        st.markdown("### Navigation")
        if st.session_state.get("logged_in", False):
            st.markdown(
                f'''
                <div style="padding:0.6rem;border-radius:8px;border:1px solid {t['border']};">
                    <div style="font-weight:600;color:{t['text']};">{st.session_state.username}</div>
                    <div style="font-size:0.85rem;color:{t['text_secondary']};">
                        {st.session_state.role.value}
                    </div>
                </div>
                ''',
                unsafe_allow_html=True,
            )

            if st.button("🏠 Dashboard", use_container_width=True):
                st.session_state.show_theme_selector = False
                st.experimental_rerun()

            if st.session_state.role == UserRole.ADMIN:
                if st.button("📝 Quiz (Admin)", use_container_width=True):
                    # existierendes pages/quizzes.py nutzen
                    try:
                        st.switch_page("pages/quizzes.py")
                    except Exception:
                        # Fallback: neu laden, falls switch_page nicht funktioniert
                        st.info("Wechsel zu Quiz (Admin) versucht.")
                        st.experimental_rerun()

                if st.button("⚙️ Admin", use_container_width=True):
                    try:
                        st.switch_page("pages/admin.py")
                    except Exception:
                        st.info("Wechsel zu Admin versucht.")
            st.markdown("---")
            if st.button("Abmelden", use_container_width=True):
                # sichere Abmeldung
                for k in list(st.session_state.keys()):
                    # behalte ggf. persistent flags? hier alles löschen
                    st.session_state.pop(k, None)
                st.experimental_rerun()
        else:
            st.info("Nicht angemeldet")


# ---------------------- Pages ----------------------
def show_password_change() -> None:
    """Erzwingt Änderung des Standardpassworts (falls verwendet)."""
    apply_theme()
    t = get_current_theme()

    st.markdown("<h1 style='margin-bottom: 0.5rem;'>🔐 Passwort ändern</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color: {t['text_secondary']} !important; margin-bottom: 2rem;'>Ändern Sie Ihr Standard-Passwort</p>",
        unsafe_allow_html=True,
    )

    st.warning("Sie verwenden noch das Standard-Passwort")

    old_pw = st.text_input("Aktuelles Passwort", type="password", key="pc_old_pw")
    new_pw = st.text_input("Neues Passwort", type="password", key="pc_new_pw")
    confirm_pw = st.text_input("Passwort bestätigen", type="password", key="pc_confirm_pw")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Passwort ändern", use_container_width=True):
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
                        st.experimental_rerun()
                    else:
                        st.error(msg)
                except Exception:
                    LOG.exception("Fehler beim Ändern des Passworts.")
                    st.error("Beim Ändern des Passworts ist ein Fehler aufgetreten.")
    with col2:
        if st.button("Später ändern", use_container_width=True):
            st.session_state.skip_password_change = True
            st.experimental_rerun()


def show_login() -> None:
    """Login-Seite (Einfach, klar)."""
    apply_theme()
    t = get_current_theme()

    st.markdown("<h1 style='margin-bottom: 0.25rem;'>Quiz</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color: {t['text_secondary']} !important; margin-bottom: 1.5rem;'>Anmelden oder registrieren</p>",
        unsafe_allow_html=True,
    )

    tab1, = st.tabs(["Anmelden"])
    with tab1:
        username = st.text_input("Benutzername", key="login_user", placeholder="dein.name")
        password = st.text_input("Passwort", type="password", key="login_pass")

        if st.button("Anmelden", use_container_width=True):
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
                st.experimental_rerun()
            else:
                st.error(message)


def show_leaderboard_page() -> None:
    """Zeigt die Bestenliste / Leaderboard-Seite."""
    apply_theme()
    t = get_current_theme()

    st.markdown("<h2 style='margin-bottom: 1rem;'>🏆 Bestenliste</h2>", unsafe_allow_html=True)

    available_quizzes = get_available_quizzes()
    if not available_quizzes:
        st.info("Noch keine Quiz-Ergebnisse vorhanden. Spiele dein erstes Quiz!")
        return

    col1, col2 = st.columns([2, 1])
    with col1:
        quiz_filter = st.selectbox("Kategorie wählen", ["Alle Quizze"] + available_quizzes, key="leaderboard_filter")

    selected_quiz = None if quiz_filter == "Alle Quizze" else quiz_filter
    leaderboard = get_leaderboard(selected_quiz)

    if not leaderboard:
        st.info("Keine Einträge für diese Kategorie")
        return

    # Summary stats
    total_players = len(leaderboard)
    total_attempts = sum(entry["attempts"] for entry in leaderboard)
    total_correct = sum(entry["correct"] for entry in leaderboard)
    total_questions = sum(entry["total"] for entry in leaderboard)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f'''
            <div class="stats-card">
                <div class="stats-label">Spieler</div>
                <div class="stats-value">{total_players}</div>
            </div>
            ''',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'''
            <div class="stats-card">
                <div class="stats-label">Versuche</div>
                <div class="stats-value">{total_attempts}</div>
            </div>
            ''',
            unsafe_allow_html=True,
        )
    with col3:
        success_rate = (total_correct / total_questions * 100) if total_questions > 0 else 0
        st.markdown(
            f'''
            <div class="stats-card">
                <div class="stats-label">Erfolgsrate</div>
                <div class="stats-value">{success_rate:.0f}%</div>
            </div>
            ''',
            unsafe_allow_html=True,
        )
    with col4:
        avg_time = sum(entry["avg_time"] for entry in leaderboard) / len(leaderboard) if leaderboard else 0
        st.markdown(
            f'''
            <div class="stats-card">
                <div class="stats-label">Ø Zeit</div>
                <div class="stats-value" style="font-size:1.5rem">{format_time(avg_time)}</div>
            </div>
            ''',
            unsafe_allow_html=True,
        )

    # Top 10
    st.markdown("<h3 style='margin-top: 1.5rem;'>🥇 Top 10</h3>", unsafe_allow_html=True)
    current_username = st.session_state.get("username", "")
    for rank, entry in enumerate(leaderboard[:10], 1):
        is_current = entry["username"] == current_username
        rank_icon = " "
        if rank == 1:
            rank_icon = "🥇"
        elif rank == 2:
            rank_icon = "🥈"
        elif rank == 3:
            rank_icon = "🥉"
        else:
            rank_icon = f"#{rank}"

        current_class = "current-user" if is_current else ""
        badge = '<span style="background:#000;color:#fff;padding:0.15rem 0.5rem;border-radius:6px;margin-left:0.5rem;font-weight:700;">Du</span>' if is_current else ""
        st.markdown(
            f'''
            <div class="leaderboard-item {current_class}">
                <div style="display:flex;align-items:center;gap:1rem">
                    <div style="font-weight:800;color:{get_current_theme()['accent']};min-width:3rem;text-align:center">{rank_icon}</div>
                    <div style="font-weight:700">{entry['username']}{badge}</div>
                </div>
                <div style="text-align:right">
                    <div style="font-weight:700">{entry['correct']} / {entry['total']} Punkte</div>
                    <div style="font-size:0.85rem;color:{get_current_theme()['text_secondary']}">Ø {format_time(entry['avg_time'])} • {entry['attempts']} Versuche</div>
                </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )


def show_dashboard() -> None:
    """Haupt-Dashboard nach dem Login."""
    apply_theme()
    t = get_current_theme()

    # Force password change if default used
    if st.session_state.get("using_default", False) and not st.session_state.get("skip_password_change", False):
        show_password_change()
        return

    st.markdown(f"<h1 style='margin-bottom: 0.2rem;'>Hallo, {st.session_state.username}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: {t['text_secondary']} !important;'>Bereit für ein Quiz?</p>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🏠 Dashboard", "🏆 Bestenliste", "🎨 Einstellungen"])
    with tab1:
        col1, col2, col3 = st.columns(3, gap="large")
        with col1:
            st.markdown(
                '''
                <div class="action-card">
                    <h3>📝 Quiz</h3>
                    <p>Wissen testen</p>
                </div>
                ''',
                unsafe_allow_html=True,
            )
            if st.button("Starten", use_container_width=True, key="quiz_btn"):
                try:
                    st.switch_page("pages/quizzes.py")
                except Exception:
                    st.info("Wechsel zum Quiz gestartet.")
                    st.experimental_rerun()

        with col2:
            if st.session_state.role == UserRole.ADMIN:
                st.markdown(
                    '''
                    <div class="action-card">
                        <h3>🎨 Theme</h3>
                        <p>Design anpassen</p>
                    </div>
                    ''',
                    unsafe_allow_html=True,
                )
                if st.button("Ändern", use_container_width=True, key="theme_btn"):
                    st.session_state.show_theme_selector = True
                    st.experimental_rerun()

        with col3:
            if st.session_state.role == UserRole.ADMIN:
                st.markdown(
                    '''
                    <div class="action-card">
                        <h3>⚙️ Admin</h3>
                        <p>Verwaltung</p>
                    </div>
                    ''',
                    unsafe_allow_html=True,
                )
                if st.button("Öffnen", use_container_width=True, key="admin_btn"):
                    try:
                        st.switch_page("pages/admin.py")
                    except Exception:
                        st.info("Wechsel zu Admin gestartet.")
                        st.experimental_rerun()
            else:
                st.markdown(
                    '''
                    <div class="action-card">
                        <h3>📊 Statistik</h3>
                        <p>Ergebnisse</p>
                    </div>
                    ''',
                    unsafe_allow_html=True,
                )
                if st.button("Anzeigen", use_container_width=True, key="results_btn"):
                    # Hinweis: bleibt im Dashboard, Benutzer kann zum Leaderboard-Tab wechseln
                    st.info("Siehe Bestenliste-Tab")

    with tab2:
        show_leaderboard_page()

    with tab3:
        show_theme_selector()

import subprocess
import threading
import time
import os

# ===============================
#   Git Auto Sync Funktionen
# ===============================

def git_commit_push():
    """Änderungen automatisch committen und pushen."""
    try:
        subprocess.run(["git", "add", "."], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "commit", "-m", "auto update"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "push"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass  # still laufen lassen

def git_pull_loop(interval=15):
    """Läuft dauerhaft im Hintergrund und zieht Änderungen."""
    while True:
        try:
            subprocess.run(["git", "pull", "--no-edit"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
        time.sleep(interval)

# ===============================
#   Autorun Funktion
# ===============================

def autorun():
    """Startet automatischen Git Sync im Hintergrund."""
    if not os.environ.get("GIT_SYNC_ACTIVE"):
        threading.Thread(target=git_pull_loop, args=(15,), daemon=True).start()
        os.environ["GIT_SYNC_ACTIVE"] = "1"

    # Wenn Dateien geändert werden, automatisch committen/pushen
    watcher_thread = threading.Thread(target=file_watcher, daemon=True)
    watcher_thread.start()

def file_watcher():
    """Überwacht Änderungen an Dateien und pusht sie automatisch."""
    last_snapshot = snapshot_dir(".")
    while True:
        time.sleep(5)
        new_snapshot = snapshot_dir(".")
        if new_snapshot != last_snapshot:
            last_snapshot = new_snapshot
            git_commit_push()

def snapshot_dir(path):
    """Erstellt einen einfachen Hash-Snapshot des Verzeichniszustands."""
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

# ===============================
#   Main Entry
# ===============================



def show_theme_selector() -> None:
    """Ermöglicht Auswahl und Speicherung des Themes."""
    t = get_current_theme()
    st.markdown("<h2 style='margin-bottom: 0.8rem;'>Theme wählen</h2>", unsafe_allow_html=True)
    settings = load_settings()
    current_theme = settings.get("current_theme", "Light")

    cols = st.columns(3)
    for idx, (theme_name, theme_data) in enumerate(THEMES.items()):
        with cols[idx]:
            is_active = theme_name == current_theme
            active_class = "active" if is_active else ""
            st.markdown(
                f'''
                <div class="theme-preview {active_class}" style="background:{theme_data['bg']};border-color:{theme_data['border']};">
                    <h4 style="color:{theme_data['text']};margin:0;">{theme_data['name']}</h4>
                </div>
                ''',
                unsafe_allow_html=True,
            )
            if st.button(("✓ Aktiv" if is_active else "Wählen"), key=f"theme_{theme_name}", use_container_width=True, disabled=is_active):
                settings["current_theme"] = theme_name
                save_settings(settings)
                st.experimental_rerun()


# ---------------------- Main ----------------------
def main() -> None:
    init_session()
    apply_theme()
    render_sidebar()

    if st.session_state.logged_in:
        try:
            show_dashboard()
        except Exception:
            LOG.exception("Fehler beim Anzeigen des Dashboards")
            st.error("Beim Laden des Dashboards ist ein Fehler aufgetreten.")
    else:
        try:
            show_login()
        except Exception:
            LOG.exception("Fehler beim Anzeigen der Login-Seite")
            st.error("Beim Laden der Login-Seite ist ein Fehler aufgetreten.")


if __name__ == "__main__":
    main()
    autorun()
