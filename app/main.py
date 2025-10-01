import streamlit as st
import json
import os
from datetime import datetime
from app.pages.auth import authenticate_user, load_users, AuthManager, UserRole, LoginResult

# ---------------------- KONFIGURATION ----------------------
st.set_page_config(
    page_title="Quiz-Anwendung",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------- GLOBALE VARIABLEN ----------------------
QUESTIONS_FILE = "./data/questions.json"
ANSWERS_DIR = "./data/answers"
SETTINGS_FILE = "./data/settings.json"

auth_manager = AuthManager()

# ---------------------- HELPER FUNKTIONEN ----------------------
def load_settings():
    """Lädt Benutzereinstellungen"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "dark_mode": False,
        "background_color": "#FFFFFF",
        "primary_color": "#1E88E5"
    }

def save_settings(settings):
    """Speichert Benutzereinstellungen"""
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)

def apply_custom_css(settings):
    """Wendet benutzerdefiniertes CSS an"""
    dark_mode = settings.get("dark_mode", False)
    bg_color = settings.get("background_color", "#FFFFFF")
    primary_color = settings.get("primary_color", "#1E88E5")
    
    # Bestimme Button-Farbe basierend auf Modus
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
        /* Haupthintergrund */
        .stApp {{
            background-color: {bg_color};
        }}
        
        /* Textfarbe */
        .stApp, .stMarkdown, p, h1, h2, h3, h4, h5, h6, label {{
            color: {text_color} !important;
        }}
        
        /* Buttons */
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
        
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {card_bg};
        }}
        
        /* Input Felder */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {{
            background-color: {card_bg};
            color: {text_color};
            border: 1px solid {primary_color};
            border-radius: 6px;
        }}
        
        /* Radio Buttons */
        .stRadio > div {{
            background-color: {card_bg};
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid {primary_color};
        }}
        
        /* Success/Error/Info Boxes */
        .stSuccess, .stError, .stWarning, .stInfo {{
            border-radius: 8px;
            padding: 1rem;
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background-color: {card_bg};
            color: {text_color};
            border-radius: 8px 8px 0 0;
            padding: 0.5rem 1rem;
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: {primary_color} !important;
            color: white !important;
        }}
        
        /* Container mit Rahmen */
        .question-container {{
            background-color: {card_bg};
            border: 2px solid {primary_color};
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
        }}
        
        /* Überschriften */
        h1, h2, h3 {{
            color: {primary_color} !important;
            font-weight: 600;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def load_questions():
    """Lädt Fragen aus JSON-Datei"""
    if os.path.exists(QUESTIONS_FILE):
        try:
            with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return []

def save_answer(username, answers):
    """Speichert Antworten eines Benutzers"""
    os.makedirs(ANSWERS_DIR, exist_ok=True)
    answer_data = {
        "username": username,
        "answers": answers,
        "timestamp": datetime.now().isoformat(),
        "completed": True
    }
    
    filepath = os.path.join(ANSWERS_DIR, f"{username}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(answer_data, f, indent=2, ensure_ascii=False)

def load_user_answers(username):
    """Lädt gespeicherte Antworten eines Benutzers"""
    filepath = os.path.join(ANSWERS_DIR, f"{username}.json")
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return None

def check_admin_access():
    """Prüft ob Admin-Seite verfügbar ist"""
    admin_file = "./pages/admin.py"
    return os.path.exists(admin_file)

# ---------------------- SEITENINHALT ----------------------
def show_settings_page():
    """Einstellungsseite"""
    st.title("Einstellungen")
    
    settings = load_settings()
    
    st.subheader("Darstellung")
    
    col1, col2 = st.columns(2)
    
    with col1:
        dark_mode = st.checkbox(
            "Dark Mode",
            value=settings.get("dark_mode", False)
        )
        
        background_color = st.color_picker(
            "Hintergrundfarbe",
            value=settings.get("background_color", "#FFFFFF")
        )
    
    with col2:
        primary_color = st.color_picker(
            "Primärfarbe (Akzente)",
            value=settings.get("primary_color", "#1E88E5")
        )
    
    st.markdown("---")
    
    if st.button("Einstellungen speichern"):
        new_settings = {
            "dark_mode": dark_mode,
            "background_color": background_color,
            "primary_color": primary_color
        }
        save_settings(new_settings)
        st.success("Einstellungen gespeichert! Seite wird neu geladen...")
        st.rerun()
    
    if st.button("Auf Standard zurücksetzen"):
        default_settings = {
            "dark_mode": False,
            "background_color": "#FFFFFF",
            "primary_color": "#1E88E5"
        }
        save_settings(default_settings)
        st.success("Einstellungen zurückgesetzt! Seite wird neu geladen...")
        st.rerun()

def show_quiz_page():
    """Quiz-Seite"""
    st.title("Quiz")
    
    questions = load_questions()
    
    if not questions:
        st.warning("Keine Fragen verfügbar. Bitte kontaktieren Sie den Administrator.")
        return
    
    # Prüfe ob Benutzer bereits geantwortet hat
    saved_answers = load_user_answers(st.session_state.username)
    
    if saved_answers and saved_answers.get("completed"):
        st.info("Sie haben das Quiz bereits ausgefüllt.")
        
        if st.button("Antworten anzeigen"):
            st.subheader("Ihre Antworten")
            for i, (question, answer) in enumerate(zip(questions, saved_answers.get("answers", [])), 1):
                st.markdown(f"**Frage {i}:** {question['question']}")
                st.write(f"Antwort: {answer}")
                st.markdown("---")
        
        if st.button("Quiz erneut ausfüllen"):
            # Lösche alte Antworten
            filepath = os.path.join(ANSWERS_DIR, f"{st.session_state.username}.json")
            if os.path.exists(filepath):
                os.remove(filepath)
            st.rerun()
        
        return
    
    # Quiz-Formular
    st.write(f"Beantworten Sie die folgenden {len(questions)} Fragen:")
    
    with st.form("quiz_form"):
        answers = []
        
        for i, question in enumerate(questions, 1):
            st.markdown(f"### Frage {i} von {len(questions)}")
            st.markdown(f"**{question['question']}**")
            
            q_type = question.get("type", "text")
            
            if q_type == "multiple_choice":
                answer = st.radio(
                    "Wählen Sie eine Antwort:",
                    options=question.get("options", []),
                    key=f"q_{i}"
                )
            elif q_type == "text":
                answer = st.text_area(
                    "Ihre Antwort:",
                    key=f"q_{i}",
                    height=100
                )
            elif q_type == "number":
                answer = st.number_input(
                    "Ihre Antwort:",
                    key=f"q_{i}"
                )
            else:
                answer = st.text_input(
                    "Ihre Antwort:",
                    key=f"q_{i}"
                )
            
            answers.append(answer)
            st.markdown("---")
        
        submitted = st.form_submit_button("Quiz absenden")
        
        if submitted:
            # Prüfe ob alle Fragen beantwortet wurden
            if all(answers):
                save_answer(st.session_state.username, answers)
                st.success("Quiz erfolgreich abgeschickt!")
                st.balloons()
                st.rerun()
            else:
                st.error("Bitte beantworten Sie alle Fragen!")

def show_login_page():
    """Login-Seite"""
    st.title("Anmeldung")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Bitte melden Sie sich an")
        
        username = st.text_input("Benutzername")
        password = st.text_input("Passwort", type="password")
        
        if st.button("Anmelden", use_container_width=True):
            if username and password:
                result, message, role = auth_manager.authenticate_user(username, password)
                
                if result == LoginResult.SUCCESS:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = role
                    st.success(message)
                    st.rerun()
                
                elif result == LoginResult.PASSWORD_CHANGE_REQUIRED:
                    st.session_state.username = username
                    st.session_state.role = role
                    st.session_state.password_change_required = True
                    st.warning(message)
                    st.rerun()
                
                elif result == LoginResult.INVALID_USERNAME:
                    st.error(message)
                
                elif result == LoginResult.ACCOUNT_LOCKED:
                    st.error(message)
                
                elif result == LoginResult.ACCOUNT_DISABLED:
                    st.error(message)
                
                else:
                    st.error(message)
            else:
                st.warning("Bitte füllen Sie alle Felder aus!")
        
        st.markdown("---")
        st.info(f"**Neuer Benutzer?** Verwenden Sie das Standard-Passwort: `4-26-2011`")
        st.caption("Ihr Benutzername muss zwischen 4-20 Zeichen lang sein und darf nur Buchstaben, Zahlen, _ und - enthalten.")

def show_password_change_page():
    """Passwort-Änderungs-Seite"""
    st.title("Passwort ändern")
    
    st.warning("Sie müssen Ihr Passwort ändern, um fortzufahren.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        old_password = st.text_input("Altes Passwort", type="password")
        new_password = st.text_input("Neues Passwort", type="password")
        confirm_password = st.text_input("Neues Passwort bestätigen", type="password")
        
        if st.button("Passwort ändern", use_container_width=True):
            if not all([old_password, new_password, confirm_password]):
                st.error("Bitte füllen Sie alle Felder aus!")
            elif new_password != confirm_password:
                st.error("Die Passwörter stimmen nicht überein!")
            elif new_password == "4-26-2011":
                st.error("Bitte wählen Sie ein anderes Passwort als das Standard-Passwort!")
            else:
                success, message = auth_manager.change_password(
                    st.session_state.username,
                    old_password,
                    new_password
                )
                
                if success:
                    st.success(message)
                    st.session_state.password_change_required = False
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error(message)
        
        st.markdown("---")
        st.info("Das neue Passwort muss mindestens 6 Zeichen lang sein.")

def show_home_page():
    """Startseite"""
    st.title("Willkommen")
    
    st.markdown(f"### Hallo, {st.session_state.username}!")
    
    # Benutzerinformationen
    users = auth_manager.load_users()
    if st.session_state.username in users:
        user = users[st.session_state.username]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Rolle:** {user.role.value.title()}")
            st.info(f"**Account erstellt:** {user.created_at.strftime('%d.%m.%Y')}")
        
        with col2:
            if user.last_login:
                st.info(f"**Letzter Login:** {user.last_login.strftime('%d.%m.%Y %H:%M')}")
            st.info(f"**Status:** Aktiv")
    
    st.markdown("---")
    
    # Schnellzugriff
    st.subheader("Schnellzugriff")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Zum Quiz", use_container_width=True):
            st.session_state.page = "Quiz"
            st.rerun()
    
    with col2:
        if st.button("Einstellungen", use_container_width=True):
            st.session_state.page = "Einstellungen"
            st.rerun()
    
    with col3:
        # Prüfe ob Admin-Seite existiert
        if st.session_state.role == UserRole.ADMIN:
            if check_admin_access():
                if st.button("Admin-Panel", use_container_width=True):
                    # Navigiere zur Admin-Seite
                    st.switch_page("pages/admin.py")
            else:
                st.button("Admin-Panel (nicht verfügbar)", disabled=True, use_container_width=True)
                st.caption("Die Admin-Seite wurde nicht gefunden.")
    
    st.markdown("---")
    
    # Quiz-Status
    saved_answers = load_user_answers(st.session_state.username)
    if saved_answers and saved_answers.get("completed"):
        st.success("Sie haben das Quiz bereits ausgefüllt!")
        if st.button("Antworten ansehen"):
            st.session_state.page = "Quiz"
            st.rerun()
    else:
        st.warning("Sie haben das Quiz noch nicht ausgefüllt.")
        if st.button("Quiz starten"):
            st.session_state.page = "Quiz"
            st.rerun()

# ---------------------- HAUPTPROGRAMM ----------------------
def main():
    # Session State initialisieren
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "role" not in st.session_state:
        st.session_state.role = None
    if "password_change_required" not in st.session_state:
        st.session_state.password_change_required = False
    if "page" not in st.session_state:
        st.session_state.page = "Home"
    
    # Einstellungen laden und CSS anwenden
    settings = load_settings()
    apply_custom_css(settings)
    
    # Nicht eingeloggt
    if not st.session_state.logged_in:
        if st.session_state.password_change_required:
            show_password_change_page()
        else:
            show_login_page()
        return
    
    # Sidebar Navigation
    with st.sidebar:
        st.title("Navigation")
        
        st.markdown(f"**Angemeldet als:** {st.session_state.username}")
        st.markdown(f"**Rolle:** {st.session_state.role.value.title()}")
        
        st.markdown("---")
        
        # Navigation
        pages = ["Home", "Quiz", "Einstellungen"]
        
        for page in pages:
            if st.button(page, use_container_width=True, key=f"nav_{page}"):
                st.session_state.page = page
                st.rerun()
        
        # Admin-Panel Button in Sidebar
        if st.session_state.role == UserRole.ADMIN:
            st.markdown("---")
            if check_admin_access():
                if st.button("Admin-Panel", use_container_width=True, key="nav_admin"):
                    st.switch_page("pages/admin.py")
            else:
                st.button("Admin-Panel (nicht verfügbar)", disabled=True, use_container_width=True)
        
        st.markdown("---")
        
        if st.button("Abmelden", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.role = None
            st.session_state.password_change_required = False
            st.rerun()
    
    # Hauptinhalt
    if st.session_state.page == "Home":
        show_home_page()
    elif st.session_state.page == "Quiz":
        show_quiz_page()
    elif st.session_state.page == "Einstellungen":
        show_settings_page()

if __name__ == "__main__":
    main()