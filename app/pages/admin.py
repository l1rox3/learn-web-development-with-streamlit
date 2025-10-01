import streamlit as st
import sys
import os

# Füge Parent-Directory zum Path hinzu für Imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.auth import AuthManager, UserRole, load_answers

# ---------------------- KONFIGURATION ----------------------
st.set_page_config(
    page_title="Admin-Panel",
    page_icon="⚙️",
    layout="wide"
)

auth_manager = AuthManager()

# ---------------------- SETTINGS LADEN ----------------------
def load_settings():
    """Lädt Benutzereinstellungen für CSS"""
    settings_file = "./data/settings.json"
    if os.path.exists(settings_file):
        try:
            import json
            with open(settings_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "dark_mode": False,
        "background_color": "#FFFFFF",
        "primary_color": "#1E88E5"
    }

def apply_custom_css(settings):
    """Wendet benutzerdefiniertes CSS an"""
    dark_mode = settings.get("dark_mode", False)
    bg_color = settings.get("background_color", "#FFFFFF")
    primary_color = settings.get("primary_color", "#1E88E5")
    
    if dark_mode:
        button_bg = "#000000"
        button_text = "#FFFFFF"
        text_color = "#FFFFFF"
        card_bg = "#1E1E1E"
    else:
        button_bg = "#FFFFFF"
        button_text = "#000000"
        text_color = "#000000"
        card_bg = "#F5F5F5"
    
    css = f"""
    <style>
        .stApp {{
            background-color: {bg_color};
        }}
        
        .stApp, .stMarkdown, p, h1, h2, h3, h4, h5, h6, label {{
            color: {text_color} !important;
        }}
        
        .stButton > button {{
            background-color: {button_bg} !important;
            color: {button_text} !important;
            border: 2px solid {primary_color} !important;
            border-radius: 8px;
            padding: 0.5rem 2rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        
        .stButton > button:hover {{
            background-color: {primary_color} !important;
            color: white !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        
        [data-testid="stSidebar"] {{
            background-color: {card_bg};
        }}
        
        .stTextInput > div > div > input {{
            background-color: {card_bg};
            color: {text_color};
            border: 1px solid {primary_color};
            border-radius: 6px;
        }}
        
        h1, h2, h3 {{
            color: {primary_color} !important;
            font-weight: 600;
        }}
        
        .user-row {{
            background-color: {card_bg};
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 0.5rem;
            border: 1px solid {primary_color};
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# ---------------------- ADMIN-PANEL ----------------------
def show_admin_panel():
    """Hauptfunktion für Admin-Panel"""
    
    # Einstellungen laden und CSS anwenden
    settings = load_settings()
    apply_custom_css(settings)
    
    st.title("Admin-Panel")
    
    # Prüfen ob eingeloggt und Admin
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("Sie sind nicht eingeloggt!")
        if st.button("Zur Anmeldung"):
            st.switch_page("main.py")
        return
    
    if "role" not in st.session_state or st.session_state.role != UserRole.ADMIN:
        st.error("Sie haben keine Admin-Berechtigung!")
        if st.button("Zurück zur Startseite"):
            st.switch_page("main.py")
        return
    
    current_admin = st.session_state.username
    
    # Reload-Button
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("Aktualisieren"):
            st.rerun()
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["Benutzerverwaltung", "Bestenliste", "Antworten"])
    
    with tab1:
        show_user_management(current_admin)
    
    with tab2:
        show_leaderboard()
    
    with tab3:
        show_all_answers()

def show_user_management(current_admin):
    """Benutzerverwaltung"""
    st.subheader("Benutzerverwaltung")
    
    users = auth_manager.load_users()
    
    # Neuen Benutzer hinzufügen
    with st.expander("Neuen Benutzer hinzufügen"):
        col1, col2, col3 = st.columns([3, 3, 1])
        
        with col1:
            new_username = st.text_input("Benutzername", key="new_user")
        
        with col2:
            new_password = st.text_input("Passwort", value="4-26-2011", type="password", key="new_pass")
        
        with col3:
            st.write("")  # Spacing
            st.write("")  # Spacing
            if st.button("Hinzufügen", use_container_width=True):
                if new_username in users:
                    st.error("Benutzer existiert bereits!")
                else:
                    is_valid, error_msg = auth_manager.is_valid_username(new_username)
                    if not is_valid:
                        st.error(error_msg)
                    else:
                        password_hash, salt = auth_manager.hash_password(new_password)
                        from app.pages.auth import User
                        from datetime import datetime
                        
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
                        st.success(f"Benutzer '{new_username}' wurde hinzugefügt!")
                        st.rerun()
    
    st.markdown("---")
    
    # Bestehende Benutzer
    st.markdown("### Bestehende Benutzer")
    
    # Header
    cols = st.columns([3, 1, 1, 2, 2])
    cols[0].markdown("**Benutzername**")
    cols[1].markdown("**Status**")
    cols[2].markdown("**Rolle**")
    cols[3].markdown("**Aktionen**")
    cols[4].markdown("**Admin-Rechte**")
    
    st.markdown("---")
    
    # User-Liste
    for username, user in users.items():
        if username == current_admin:
            continue  # Admin selbst überspringen
        
        cols = st.columns([3, 1, 1, 2, 2])
        
        # Benutzername
        cols[0].markdown(f"**{username}**")
        
        # Status
        if user.active:
            cols[1].markdown("✅ Aktiv")
        else:
            cols[1].markdown("❌ Gesperrt")
        
        # Rolle
        if user.role == UserRole.ADMIN:
            cols[2].markdown("👑 Admin")
        else:
            cols[3].markdown("👤 User")
        
        # Block / Unblock
        with cols[3]:
            if user.active:
                if st.button("Blockieren", key=f"block_{username}", use_container_width=True):
                    user.active = False
                    auth_manager.save_users(users)
                    st.success(f"'{username}' wurde blockiert!")
                    st.rerun()
            else:
                if st.button("Entblocken", key=f"unblock_{username}", use_container_width=True):
                    user.active = True
                    auth_manager.save_users(users)
                    st.success(f"'{username}' wurde entblockt!")
                    st.rerun()
        
        # Admin-Rechte
        with cols[4]:
            if user.role == UserRole.ADMIN:
                if st.button("Admin entfernen", key=f"remove_admin_{username}", use_container_width=True):
                    user.role = UserRole.USER
                    auth_manager.save_users(users)
                    st.success(f"'{username}' ist kein Admin mehr!")
                    st.rerun()
            else:
                if st.button("Admin geben", key=f"make_admin_{username}", use_container_width=True):
                    user.role = UserRole.ADMIN
                    auth_manager.save_users(users)
                    st.success(f"'{username}' ist jetzt Admin!")
                    st.rerun()
        
        st.markdown("---")

def show_leaderboard():
    """Bestenliste anzeigen"""
    st.subheader("Bestenliste")
    
    answers = load_answers()
    
    if not answers:
        st.info("Noch keine Ergebnisse vorhanden.")
        return
    
    # Statistik vorbereiten
    user_stats = {}
    for entry in answers:
        username = entry.get("username")
        if not username:
            continue
        
        if username not in user_stats:
            user_stats[username] = {
                "completed": 0,
                "timestamp": entry.get("timestamp", "")
            }
        
        user_stats[username]["completed"] += 1
        if entry.get("timestamp"):
            user_stats[username]["timestamp"] = entry.get("timestamp")
    
    # Sortieren nach Anzahl abgeschlossener Quiz
    leaderboard = []
    for username, stats in user_stats.items():
        leaderboard.append({
            "Rang": 0,
            "Benutzer": username,
            "Abgeschlossene Quiz": stats["completed"],
            "Letzter Eintrag": stats["timestamp"][:10] if stats["timestamp"] else "Unbekannt"
        })
    
    # Nach Anzahl sortieren
    leaderboard.sort(key=lambda x: x["Abgeschlossene Quiz"], reverse=True)
    
    # Ränge zuweisen
    for i, entry in enumerate(leaderboard, 1):
        entry["Rang"] = i
    
    # Tabelle anzeigen
    if leaderboard:
        st.table(leaderboard)
    else:
        st.info("Keine Daten vorhanden.")

def show_all_answers():
    """Alle Antworten anzeigen"""
    st.subheader("Alle Antworten")
    
    answers = load_answers()
    
    if not answers:
        st.info("Noch keine Antworten vorhanden.")
        return
    
    # Nach Benutzer filtern
    usernames = list(set([a.get("username", "Unbekannt") for a in answers]))
    selected_user = st.selectbox("Benutzer auswählen:", ["Alle"] + sorted(usernames))
    
    # Filtern
    if selected_user != "Alle":
        filtered_answers = [a for a in answers if a.get("username") == selected_user]
    else:
        filtered_answers = answers
    
    # Anzeigen
    for entry in filtered_answers:
        username = entry.get("username", "Unbekannt")
        timestamp = entry.get("timestamp", "Unbekannt")
        user_answers = entry.get("answers", [])
        
        with st.expander(f"{username} - {timestamp[:19] if timestamp != 'Unbekannt' else 'Unbekannt'}"):
            if user_answers:
                for i, answer in enumerate(user_answers, 1):
                    st.markdown(f"**Frage {i}:** {answer}")
            else:
                st.info("Keine Antworten vorhanden.")

# ---------------------- SIDEBAR ----------------------
with st.sidebar:
    st.title("Navigation")
    
    if "logged_in" in st.session_state and st.session_state.logged_in:
        st.markdown(f"**Angemeldet als:** {st.session_state.username}")
        st.markdown(f"**Rolle:** Admin")
        
        st.markdown("---")
        
        if st.button("Zurück zur Startseite", use_container_width=True):
            st.switch_page("main.py")
        
        st.markdown("---")
        
        if st.button("Abmelden", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.role = None
            st.switch_page("main.py")

# ---------------------- HAUPTPROGRAMM ----------------------
if __name__ == "__main__":
    show_admin_panel()