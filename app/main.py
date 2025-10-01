import streamlit as st
import os
import json
from pages.auth import AuthManager, UserRole, DEFAULT_PASSWORD

# ---------------------- KONFIGURATION ----------------------
st.set_page_config(
    page_title="Quiz-Anwendung",
    page_icon="📝",
    layout="wide"
)

auth_manager = AuthManager()

# ---------------------- SETTINGS ----------------------
def load_settings():
    settings_file = "./data/settings.json"
    if os.path.exists(settings_file):
        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                settings = json.load(f)
                # Leere Datei-Prüfung
                if not settings:
                    return get_default_settings()
                return settings
        except:
            pass
    return get_default_settings()

def get_default_settings():
    """Standard-Einstellungen basierend auf System-Theme"""
    # Versuche System-Theme zu erkennen (Streamlit verwendet helles Theme standardmäßig)
    return {
        "dark_mode": False,
        "background_color": "#FFFFFF",
        "sidebar_color": "#F5F5F5",
        "primary_color": "#1E88E5"
    }

def apply_custom_css(settings):
    dark_mode = settings.get("dark_mode", False)
    bg_color = settings.get("background_color", "#FFFFFF")
    sidebar_color = settings.get("sidebar_color", "#F5F5F5")
    primary_color = settings.get("primary_color", "#1E88E5")

    if dark_mode:
        text_color, card_bg, input_bg = "#FFFFFF", "#1E1E1E", "#2A2A2A"
        button_bg, button_text = "#000000", "#FFFFFF"
    else:
        text_color, card_bg, input_bg = "#000000", "#F5F5F5", "#FFFFFF"
        button_bg, button_text = "#FFFFFF", "#000000"

    css = f"""
    <style>
        .stApp {{ background-color: {bg_color}; }}
        .stApp, .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, span {{
            color: {text_color} !important;
        }}
        .stButton > button {{
            background-color: {button_bg} !important;
            color: {button_text} !important;
            border: 2px solid {primary_color} !important;
            border-radius: 8px;
            padding: 0.5rem 2rem;
        }}
        .stButton > button:hover {{
            background-color: {primary_color} !important;
            color: white !important;
        }}
        [data-testid="stSidebar"] {{ background-color: {sidebar_color} !important; }}
        [data-testid="stSidebar"] * {{ color: {text_color} !important; }}
        h1, h2, h3 {{ color: {primary_color} !important; }}
        .welcome-card {{
            background-color: {card_bg};
            padding: 2rem;
            border-radius: 12px;
            border: 2px solid {primary_color};
            margin: 1rem 0;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# ---------------------- PASSWORD CHANGE ----------------------
def show_password_change():
    st.subheader("Passwort ändern")
    st.warning("Sie verwenden noch das Standard-Passwort. Bitte ändern Sie es aus Sicherheitsgründen.")

    old_pw = st.text_input("Aktuelles Passwort", type="password")
    new_pw = st.text_input("Neues Passwort", type="password")
    confirm_pw = st.text_input("Neues Passwort bestätigen", type="password")

    if st.button("Passwort ändern"):
        if not old_pw or not new_pw or not confirm_pw:
            st.warning("Bitte alle Felder ausfüllen!")
        elif new_pw != confirm_pw:
            st.error("Neue Passwörter stimmen nicht überein!")
        else:
            success, msg = auth_manager.change_password(st.session_state.username, old_pw, new_pw)
            if success:
                st.success(msg)
                st.session_state.using_default = False
                st.rerun()
            else:
                st.error(msg)

    if st.button("Später ändern"):
        st.session_state.skip_password_change = True
        st.rerun()

# ---------------------- LOGIN / REGISTRATION ----------------------
def show_login():
    settings = load_settings()
    apply_custom_css(settings)

    st.title("📝 Quiz-App Login")
    st.markdown("---")

    tab1, tab2 = st.tabs(["Anmelden", "Registrieren"])

    with tab1:
        username = st.text_input("Benutzername", key="login_user")
        password = st.text_input("Passwort", type="password", key="login_pass")
        if st.button("Anmelden"):
            if username and password:
                success, message, using_default = auth_manager.authenticate_user(username, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.using_default = using_default
                    st.session_state.role = auth_manager.load_users()[username].role
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("Bitte alle Felder ausfüllen!")

    with tab2:
        new_username = st.text_input("Neuer Benutzername", key="reg_user")
        new_password = st.text_input("Passwort", type="password", key="reg_pass")
        confirm_password = st.text_input("Passwort bestätigen", type="password", key="reg_confirm")
        if st.button("Registrieren"):
            if not new_username or not new_password or not confirm_password:
                st.warning("Bitte alle Felder ausfüllen!")
            elif new_password != confirm_password:
                st.error("Passwörter stimmen nicht überein!")
            else:
                if new_password != DEFAULT_PASSWORD:
                    st.info(f"Für neue Benutzer bitte das Standard-Passwort ({DEFAULT_PASSWORD}) verwenden!")
                else:
                    success, message, using_default = auth_manager.authenticate_user(new_username, new_password)
                    if success:
                        st.success("🎉 Registrierung erfolgreich! Bitte anmelden.")
                    else:
                        st.error(message)

# ---------------------- DASHBOARD ----------------------
def show_dashboard():
    settings = load_settings()
    apply_custom_css(settings)

    if st.session_state.get("using_default", False) and not st.session_state.get("skip_password_change", False):
        show_password_change()
        return

    st.title(f"Willkommen, {st.session_state.username}!")

    if st.session_state.role == UserRole.ADMIN:
        st.info("🔑 Sie sind als Administrator angemeldet.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="welcome-card"><h3>Quiz starten</h3></div>', unsafe_allow_html=True)
        if st.button("Zum Quiz", use_container_width=True):
            st.switch_page("pages/quizzes.py")

    with col2:
        if st.session_state.role == UserRole.ADMIN:
            st.markdown('<div class="welcome-card"><h3>Admin-Panel</h3></div>', unsafe_allow_html=True)
            if st.button("Zum Admin-Panel", use_container_width=True):
                st.switch_page("pages/admin.py")
        else:
            st.markdown('<div class="welcome-card"><h3>Meine Ergebnisse</h3></div>', unsafe_allow_html=True)
            if st.button("Zu meinen Ergebnissen", use_container_width=True):
                st.info("🚧 Ergebnisse-Seite wird implementiert...")

# ---------------------- SIDEBAR ----------------------
def show_sidebar():
    with st.sidebar:
        st.title("Navigation")
        if st.session_state.get("logged_in", False):
            st.markdown(f"👤 **{st.session_state.username}**")
            st.markdown(f"Rolle: **{st.session_state.role.value}**")
            st.markdown("---")
            
            # Navigation Links
            if st.button("🏠 Dashboard", use_container_width=True):
                st.switch_page("main.py")
            
            if st.button("📝 Quiz", use_container_width=True):
                st.switch_page("pages/quizzes.py")
            
            if st.session_state.role == UserRole.ADMIN:
                if st.button("⚙️ Admin-Panel", use_container_width=True):
                    st.switch_page("pages/admin.py")
            
            st.markdown("---")
            
            if st.button("Abmelden"):
                st.session_state.clear()
                st.rerun()
        else:
            st.info("Bitte anmelden")

# ---------------------- MAIN ----------------------
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.skip_password_change = False

    show_sidebar()

    if st.session_state.logged_in:
        show_dashboard()
    else:
        show_login()

if __name__ == "__main__":
    main()