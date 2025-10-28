import streamlit as st
import sys
import os
import json
import pandas as pd
from datetime import datetime

# Füge Parent-Directory zum Path hinzu für Imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.auth import AuthManager, UserRole
auth_manager = AuthManager()

# ⚠️ WICHTIG: Session-Validierung bei JEDEM Seitenaufruf!
if "username" in st.session_state and st.session_state.username.strip():
    status = auth_manager.check_user_status(st.session_state.username)
    
    if status["should_logout"]:
        st.error(f"🔒 {status['message']}")
        st.warning("Du wurdest automatisch ausgeloggt.")
        
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        import time
        time.sleep(2)
        st.rerun()

# ---------------------- KONFIGURATION ----------------------
st.set_page_config(
    page_title="Admin Panel",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

ANSWERS_DIR = "./data/answers"

# ---------------------- THEME ----------------------
def get_theme():
    """Modernes Dark Theme"""
    return {
        "bg": "#0f0f0f",
        "surface": "#1a1a1a", 
        "surface_light": "#2a2a2a",
        "border": "#333333",
        "text": "#ffffff",
        "text_secondary": "#a0a0a0",
        "accent": "#3b82f6",
        "accent_hover": "#60a5fa",
        "success": "#10b981",
        "error": "#ef4444",
        "warning": "#f59e0b",
        "card_bg": "#1e1e1e"
    }

def apply_admin_theme():
    """Wendet das moderne Dark Theme an"""
    t = get_theme()
    
    css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        
        .stApp {{
            background: {t['bg']};
            color: {t['text']};
        }}
        
        .main .block-container {{
            padding-top: 2rem;
            padding-bottom: 2rem;
        }}
        
        /* Header */
        .admin-header {{
            background: linear-gradient(135deg, {t['surface']} 0%, {t['card_bg']} 100%);
            border-radius: 16px;
            padding: 2.5rem;
            margin-bottom: 2rem;
            border: 1px solid {t['border']};
            text-align: center;
        }}
        
        .admin-title {{
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, {t['accent']}, {t['success']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}
        
        .admin-subtitle {{
            color: {t['text_secondary']};
            font-size: 1.1rem;
            font-weight: 400;
        }}
        
        /* Cards */
        .stats-card {{
            background: {t['card_bg']};
            border: 1px solid {t['border']};
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
        }}
        
        .stats-card:hover {{
            transform: translateY(-5px);
            border-color: {t['accent']};
            box-shadow: 0 10px 30px rgba(59, 130, 246, 0.1);
        }}
        
        .stats-value {{
            font-size: 2.5rem;
            font-weight: 700;
            color: {t['accent']};
            margin: 0.5rem 0;
        }}
        
        .stats-label {{
            color: {t['text_secondary']};
            font-size: 0.9rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        /* User Cards */
        .user-card {{
            background: {t['card_bg']};
            border: 1px solid {t['border']};
            border-radius: 12px;
            padding: 1.5rem;
            margin: 0.75rem 0;
            transition: all 0.2s ease;
        }}
        
        .user-card:hover {{
            border-color: {t['accent']};
            transform: translateX(5px);
        }}
        
        .user-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }}
        
        .user-name {{
            font-size: 1.2rem;
            font-weight: 600;
            color: {t['text']};
        }}
        
        .badge {{
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .badge-admin {{
            background: {t['accent']}20;
            color: {t['accent']};
            border: 1px solid {t['accent']};
        }}
        
        .badge-user {{
            background: {t['success']}20;
            color: {t['success']};
            border: 1px solid {t['success']};
        }}
        
        .badge-active {{
            background: {t['success']}20;
            color: {t['success']};
        }}
        
        .badge-blocked {{
            background: {t['error']}20;
            color: {t['error']};
        }}
        
        /* Buttons */
        .stButton > button {{
            background: {t['surface_light']};
            color: {t['text']} !important;
            border: 1px solid {t['border']};
            border-radius: 8px;
            padding: 0.6rem 1.2rem;
            font-weight: 500;
            transition: all 0.2s ease;
        }}
        
        .stButton > button:hover {{
            background: {t['accent']};
            border-color: {t['accent']};
            transform: translateY(-2px);
        }}
        
        .btn-success button {{
            background: {t['success']} !important;
            border-color: {t['success']} !important;
        }}
        
        .btn-danger button {{
            background: {t['error']} !important;
            border-color: {t['error']} !important;
        }}
        
        .btn-warning button {{
            background: {t['warning']} !important;
            border-color: {t['warning']} !important;
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0;
            background: transparent;
            border-bottom: 1px solid {t['border']};
        }}
        
        .stTabs [data-baseweb="tab"] {{
            border-radius: 8px 8px 0 0;
            color: {t['text_secondary']} !important;
            font-weight: 500;
            padding: 0.75rem 1.5rem;
            border: none;
            background: transparent;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: {t['accent']} !important;
            color: white !important;
        }}
        
        /* Tables */
        .dataframe {{
            background: {t['card_bg']} !important;
            color: {t['text']} !important;
        }}
        
        .dataframe th {{
            background: {t['surface']} !important;
            color: {t['text']} !important;
        }}
        
        .dataframe td {{
            background: {t['card_bg']} !important;
            color: {t['text']} !important;
            border-color: {t['border']} !important;
        }}
        
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background: {t['surface']} !important;
            border-right: 1px solid {t['border']};
        }}
        
        /* Progress bars */
        .stProgress > div > div > div > div {{
            background: linear-gradient(90deg, {t['accent']}, {t['success']});
        }}
        
        /* Hide Streamlit branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {{
            width: 6px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: {t['bg']};
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {t['border']};
            border-radius: 3px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: {t['accent']};
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# ---------------------- DATEN-FUNKTIONEN ----------------------
def load_user_data(username: str):
    """Lädt die Daten eines Benutzers"""
    user_file = os.path.join(ANSWERS_DIR, f"{username}.json")
    if not os.path.exists(user_file):
        return {"username": username, "runs": []}
    
    try:
        with open(user_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"username": username, "runs": []}

def get_leaderboard():
    """Erstellt eine Bestenliste basierend auf Runs"""
    if not os.path.exists(ANSWERS_DIR):
        return []
    
    leaderboard = []
    
    for filename in os.listdir(ANSWERS_DIR):
        if not filename.endswith(".json"):
            continue
        
        username = filename[:-5]
        user_data = load_user_data(username)
        
        runs = user_data.get("runs", [])
        if not runs:
            continue
        
        # Bestes Ergebnis pro Nutzer
        best_run = max(runs, key=lambda x: x.get("percentage", 0))
        
        leaderboard.append({
            "username": username,
            "score": best_run.get("percentage", 0),
            "correct": best_run.get("correct", 0),
            "total": best_run.get("total", 0),
            "time": best_run.get("time_seconds", 0),
            "quiz_name": best_run.get("quiz_name", "Unbekannt"),
            "timestamp": best_run.get("timestamp", ""),
            "attempts": len(runs)
        })
    
    leaderboard.sort(key=lambda x: (-x["score"], x["time"]))
    return leaderboard

def get_user_stats():
    """Gibt Statistiken über alle Benutzer zurück"""
    users = auth_manager.load_users()
    total_users = len(users)
    active_users = sum(1 for u in users.values() if u.active)
    admin_users = sum(1 for u in users.values() if u.role == UserRole.ADMIN)
    
    # Quiz-Statistiken
    total_attempts = 0
    if os.path.exists(ANSWERS_DIR):
        for filename in os.listdir(ANSWERS_DIR):
            if filename.endswith(".json"):
                user_data = load_user_data(filename[:-5])
                total_attempts += len(user_data.get("runs", []))
    
    return {
        "total": total_users,
        "active": active_users,
        "admins": admin_users,
        "blocked": total_users - active_users,
        "total_attempts": total_attempts
    }

def format_time(seconds: float):
    """Formatiert Sekunden in MM:SS Format"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

# ---------------------- BENUTZERVERWALTUNG ----------------------
def show_user_management(current_admin):
    """Benutzerverwaltung mit modernem Design"""
    t = get_theme()
    
    st.markdown("<div class='admin-header'>", unsafe_allow_html=True)
    st.markdown("<div class='admin-title'>👥 Benutzerverwaltung</div>", unsafe_allow_html=True)
    st.markdown("<div class='admin-subtitle'>Verwalten Sie Benutzerkonten und Berechtigungen</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Statistiken
    stats = get_user_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''
        <div class="stats-card">
            <div class="stats-label">Gesamt Benutzer</div>
            <div class="stats-value">{stats['total']}</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="stats-card">
            <div class="stats-label">Aktiv</div>
            <div class="stats-value">{stats['active']}</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="stats-card">
            <div class="stats-label">Admins</div>
            <div class="stats-value">{stats['admins']}</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'''
        <div class="stats-card">
            <div class="stats-label">Quiz Versuche</div>
            <div class="stats-value">{stats['total_attempts']}</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Neuen Benutzer hinzufügen
    with st.expander("➕ Neuen Benutzer erstellen", expanded=True):
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        
        with col1:
            new_username = st.text_input("👤 Benutzername", placeholder="Benutzername eingeben")
        
        with col2:
            new_password = st.text_input("🔑 Passwort", value="4-26-2011", type="password")
        
        with col3:
            new_role = st.selectbox("🎭 Rolle", ["User", "Admin"])
        
        with col4:
            st.write("")
            st.write("")
            if st.button("✅ Erstellen", use_container_width=True):
                if new_username and new_password:
                    users = auth_manager.load_users()
                    if new_username in users:
                        st.error("❌ Benutzer existiert bereits!")
                    else:
                        is_valid, error_msg = auth_manager.is_valid_username(new_username)
                        if not is_valid:
                            st.error(f"❌ {error_msg}")
                        else:
                            password_hash, salt = auth_manager.hash_password(new_password)
                            from pages.auth import User
                            
                            users[new_username] = User(
                                username=new_username,
                                password_hash=password_hash,
                                role=UserRole.ADMIN if new_role == "Admin" else UserRole.USER,
                                active=True,
                                created_at=datetime.now(),
                                using_default=True,
                                salt=salt
                            )
                            auth_manager.save_users(users)
                            st.success(f"✅ Benutzer '{new_username}' erfolgreich erstellt")
                            st.rerun()
                else:
                    st.error("❌ Bitte Benutzername und Passwort eingeben")
    
    # Benutzerliste
    st.markdown("### 📋 Benutzerliste")
    
    users = auth_manager.load_users()
    
    # Suchfunktion
    search = st.text_input("🔍 Benutzer suchen", placeholder="Benutzername eingeben...")
    
    # Filter
    col1, col2, col3 = st.columns(3)
    with col1:
        role_filter = st.selectbox("Rolle", ["Alle", "Admin", "User"])
    with col2:
        status_filter = st.selectbox("Status", ["Alle", "Aktiv", "Blockiert"])
    with col3:
        st.write("")
        if st.button("🔄 Aktualisieren"):
            st.rerun()
    
    # Gefilterte Benutzer
    filtered_users = []
    for username, user in users.items():
        if username == current_admin:
            continue
        
        if search and search.lower() not in username.lower():
            continue
        
        if role_filter != "Alle":
            if role_filter == "Admin" and user.role != UserRole.ADMIN:
                continue
            if role_filter == "User" and user.role == UserRole.ADMIN:
                continue
        
        if status_filter != "Alle":
            if status_filter == "Aktiv" and not user.active:
                continue
            if status_filter == "Blockiert" and user.active:
                continue
        
        filtered_users.append((username, user))
    
    if not filtered_users:
        st.info("ℹ️ Keine Benutzer gefunden")
        return
    
    for username, user in filtered_users:
        role_badge = "badge-admin" if user.role == UserRole.ADMIN else "badge-user"
        role_text = "Admin" if user.role == UserRole.ADMIN else "User"
        status_badge = "badge-active" if user.active else "badge-blocked"
        status_text = "Aktiv" if user.active else "Blockiert"
        
        st.markdown(f'''
        <div class="user-card">
            <div class="user-header">
                <div class="user-name">👤 {username}</div>
                <div style="display: flex; gap: 0.5rem;">
                    <span class="badge {role_badge}">{role_text}</span>
                    <span class="badge {status_badge}">{status_text}</span>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Aktionen
        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
        
        with col1:
            if user.active:
                st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
                if st.button("🚫 Blockieren", key=f"block_{username}", use_container_width=True):
                    user.active = False
                    auth_manager.save_users(users)
                    st.success(f"✅ '{username}' wurde blockiert")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="btn-success">', unsafe_allow_html=True)
                if st.button("✅ Aktivieren", key=f"activate_{username}", use_container_width=True):
                    user.active = True
                    auth_manager.save_users(users)
                    st.success(f"✅ '{username}' wurde aktiviert")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            if user.role == UserRole.ADMIN:
                if st.button("👤 Zu User", key=f"remove_admin_{username}", use_container_width=True):
                    user.role = UserRole.USER
                    auth_manager.save_users(users)
                    st.success(f"✅ '{username}' ist jetzt User")
                    st.rerun()
            else:
                if st.button("👑 Zu Admin", key=f"make_admin_{username}", use_container_width=True):
                    user.role = UserRole.ADMIN
                    auth_manager.save_users(users)
                    st.success(f"✅ '{username}' ist jetzt Admin")
                    st.rerun()
        
        with col3:
            if st.button("🗑️ Löschen", key=f"delete_{username}", use_container_width=True):
                if username != current_admin:
                    del users[username]
                    auth_manager.save_users(users)
                    st.success(f"✅ '{username}' wurde gelöscht")
                    st.rerun()
                else:
                    st.error("❌ Sie können sich nicht selbst löschen")
        
        with col4:
            # Benutzerstatistiken anzeigen
            user_data = load_user_data(username)
            runs = user_data.get("runs", [])
            if runs:
                best_score = max(run.get("percentage", 0) for run in runs)
                st.info(f"📊 Bestes Ergebnis: {best_score:.1f}% ({len(runs)} Versuche)")
            else:
                st.info("📊 Noch keine Quiz-Versuche")
        
        st.markdown("---")

# ---------------------- BESTENLISTE ----------------------
def show_leaderboard_tab():
    """Bestenliste im Admin-Panel"""
    t = get_theme()
    
    st.markdown("<div class='admin-header'>", unsafe_allow_html=True)
    st.markdown("<div class='admin-title'>🏆 Bestenliste</div>", unsafe_allow_html=True)
    st.markdown("<div class='admin-subtitle'>Übersicht der besten Ergebnisse</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    leaderboard = get_leaderboard()
    
    if not leaderboard:
        st.info("ℹ️ Noch keine Quiz-Ergebnisse vorhanden")
        return
    
    # Top 3 hervorheben
    if len(leaderboard) >= 3:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if len(leaderboard) > 0:
                user = leaderboard[0]
                st.markdown(f'''
                <div style="background: linear-gradient(135deg, {t['warning']}20, {t['accent']}20); 
                            border: 2px solid {t['warning']}; border-radius: 16px; padding: 2rem; text-align: center;">
                    <div style="font-size: 3rem;">🥇</div>
                    <div style="font-size: 1.5rem; font-weight: 700; margin: 1rem 0;">{user['username']}</div>
                    <div style="font-size: 2rem; font-weight: 700; color: {t['warning']};">{user['score']:.1f}%</div>
                    <div style="color: {t['text_secondary']}; margin-top: 0.5rem;">
                        {user['correct']}/{user['total']} • {format_time(user['time'])}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
        
        with col2:
            if len(leaderboard) > 1:
                user = leaderboard[1]
                st.markdown(f'''
                <div style="background: linear-gradient(135deg, {t['text_secondary']}20, {t['surface_light']}); 
                            border: 2px solid {t['text_secondary']}; border-radius: 16px; padding: 2rem; text-align: center;">
                    <div style="font-size: 3rem;">🥈</div>
                    <div style="font-size: 1.5rem; font-weight: 700; margin: 1rem 0;">{user['username']}</div>
                    <div style="font-size: 2rem; font-weight: 700; color: {t['text_secondary']};">{user['score']:.1f}%</div>
                    <div style="color: {t['text_secondary']}; margin-top: 0.5rem;">
                        {user['correct']}/{user['total']} • {format_time(user['time'])}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
        
        with col3:
            if len(leaderboard) > 2:
                user = leaderboard[2]
                st.markdown(f'''
                <div style="background: linear-gradient(135deg, {t['warning']}15, {t['surface_light']}); 
                            border: 2px solid {t['warning']}80; border-radius: 16px; padding: 2rem; text-align: center;">
                    <div style="font-size: 3rem;">🥉</div>
                    <div style="font-size: 1.5rem; font-weight: 700; margin: 1rem 0;">{user['username']}</div>
                    <div style="font-size: 2rem; font-weight: 700; color: {t['warning']}80;">{user['score']:.1f}%</div>
                    <div style="color: {t['text_secondary']}; margin-top: 0.5rem;">
                        {user['correct']}/{user['total']} • {format_time(user['time'])}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
    
    # Detaillierte Tabelle
    st.markdown("### 📊 Detaillierte Übersicht")
    
    # Daten für Tabelle vorbereiten
    table_data = []
    for i, entry in enumerate(leaderboard, 1):
        table_data.append({
            "Rang": i,
            "Benutzer": entry["username"],
            "Punkte": f"{entry['correct']}/{entry['total']}",
            "Prozent": f"{entry['score']:.1f}%",
            "Zeit": format_time(entry["time"]),
            "Quiz": entry["quiz_name"],
            "Versuche": entry["attempts"]
        })
    
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Export-Button
    if st.button("📥 Als CSV exportieren"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 CSV herunterladen",
            data=csv,
            file_name="bestenliste.csv",
            mime="text/csv"
        )

# ---------------------- QUIZ-STATISTIKEN ----------------------
def show_quiz_statistics():
    """Detaillierte Quiz-Statistiken"""
    t = get_theme()
    
    st.markdown("<div class='admin-header'>", unsafe_allow_html=True)
    st.markdown("<div class='admin-title'>📈 Quiz-Statistiken</div>", unsafe_allow_html=True)
    st.markdown("<div class='admin-subtitle'>Detaillierte Analysen und Metriken</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    if not os.path.exists(ANSWERS_DIR):
        st.info("ℹ️ Noch keine Quiz-Daten vorhanden")
        return
    
    # Alle Runs sammeln
    all_runs = []
    for filename in os.listdir(ANSWERS_DIR):
        if filename.endswith(".json"):
            user_data = load_user_data(filename[:-5])
            all_runs.extend(user_data.get("runs", []))
    
    if not all_runs:
        st.info("ℹ️ Noch keine Quiz-Versuche vorhanden")
        return
    
    # Statistiken berechnen
    total_runs = len(all_runs)
    avg_score = sum(run.get("percentage", 0) for run in all_runs) / total_runs
    avg_time = sum(run.get("time_seconds", 0) for run in all_runs) / total_runs
    total_questions = sum(run.get("total", 0) for run in all_runs)
    total_correct = sum(run.get("correct", 0) for run in all_runs)
    
    # Quiz-Verteilung
    quiz_distribution = {}
    for run in all_runs:
        quiz_name = run.get("quiz_name", "Unbekannt")
        quiz_distribution[quiz_name] = quiz_distribution.get(quiz_name, 0) + 1
    
    # Statistiken anzeigen
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''
        <div class="stats-card">
            <div class="stats-label">Gesamt Versuche</div>
            <div class="stats-value">{total_runs}</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="stats-card">
            <div class="stats-label">Ø Ergebnis</div>
            <div class="stats-value">{avg_score:.1f}%</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="stats-card">
            <div class="stats-label">Ø Zeit</div>
            <div class="stats-value" style="font-size: 1.8rem;">{format_time(avg_time)}</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'''
        <div class="stats-card">
            <div class="stats-label">Richtige Antworten</div>
            <div class="stats-value">{total_correct}</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Quiz-Verteilung
    st.markdown("### 📊 Quiz-Verteilung")
    
    quiz_data = []
    for quiz_name, count in quiz_distribution.items():
        quiz_runs = [r for r in all_runs if r.get("quiz_name") == quiz_name]
        avg_quiz_score = sum(r.get("percentage", 0) for r in quiz_runs) / len(quiz_runs) if quiz_runs else 0
        quiz_data.append({
            "Quiz": quiz_name,
            "Versuche": count,
            "Ø Ergebnis": f"{avg_quiz_score:.1f}%"
        })
    
    quiz_df = pd.DataFrame(quiz_data)
    st.dataframe(quiz_df, use_container_width=True, hide_index=True)
    
    # Letzte Aktivitäten
    st.markdown("### 📅 Letzte Aktivitäten")
    
    # Sortiere nach Zeitstempel
    recent_runs = sorted(all_runs, key=lambda x: x.get("timestamp", ""), reverse=True)[:10]
    
    for run in recent_runs:
        timestamp = run.get("timestamp", "")[:19]
        username = "Unbekannt"
        # Username aus Dateiname ermitteln
        for filename in os.listdir(ANSWERS_DIR):
            if filename.endswith(".json"):
                user_data = load_user_data(filename[:-5])
                if run in user_data.get("runs", []):
                    username = filename[:-5]
                    break
        
        st.markdown(f"""
        **{username}** - {run.get('quiz_name', 'Unbekannt')}  
        ⭐ {run.get('percentage', 0):.1f}% ({run.get('correct', 0)}/{run.get('total', 0)})  
        ⏱️ {format_time(run.get('time_seconds', 0))} • 📅 {timestamp}
        """)
        st.markdown("---")

# ---------------------- SIDEBAR ----------------------
def show_sidebar():
    """Sidebar mit Navigation"""
    with st.sidebar:
        t = get_theme()
        
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h1 style='color: #3b82f6; margin-bottom: 0.5rem;'>⚙️</h1>
            <h2 style='color: white; margin: 0;'>Admin Panel</h2>
            <p style='color: #a0a0a0; margin: 0;'>Control Center</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.get("logged_in", False):
            st.markdown(f"""
            <div style='background: {t['card_bg']}; border: 1px solid {t['border']}; 
                        border-radius: 12px; padding: 1rem; margin-bottom: 1rem;'>
                <div style='font-weight: 600; color: {t['text']};'>👤 {st.session_state.username}</div>
                <div style='color: {t['accent']}; font-size: 0.8rem; margin-top: 0.25rem;'>
                    Administrator
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### 🧭 Navigation")
        
        if st.button("🏠 Zurück zur Hauptseite", use_container_width=True):
            st.switch_page("main.py")
        
        st.markdown("---")
        
        # System-Info
        st.markdown("### ℹ️ System-Info")
        stats = get_user_stats()
        st.markdown(f"""
        - **Benutzer:** {stats['total']}
        - **Aktiv:** {stats['active']}
        - **Quiz-Versuche:** {stats['total_attempts']}
        """)
        
        st.markdown("---")
        
        if st.button("🚪 Abmelden", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("main.py")

# ---------------------- HAUPTPROGRAMM ----------------------
def main():
    apply_admin_theme()
    
    # Prüfen ob eingeloggt und Admin
    if not st.session_state.get("logged_in", False):
        st.error("🔐 Sie sind nicht eingeloggt!")
        if st.button("➡️ Zur Anmeldung"):
            st.switch_page("main.py")
        return
    
    if st.session_state.get("role") != UserRole.ADMIN:
        st.error("⛔ Sie haben keine Admin-Berechtigung!")
        if st.button("⬅️ Zurück"):
            st.switch_page("main.py")
        return
    
    show_sidebar()
    
    current_admin = st.session_state.username
    
    # Tabs für verschiedene Bereiche
    tab1, tab2, tab3 = st.tabs(["👥 Benutzer", "🏆 Bestenliste", "📈 Statistiken"])
    
    with tab1:
        show_user_management(current_admin)
    
    with tab2:
        show_leaderboard_tab()
    
    with tab3:
        show_quiz_statistics()

if __name__ == "__main__":
    main()