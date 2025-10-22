import streamlit as st
from auth import AuthManager

# ---------------------- SESSION VALIDATOR ----------------------
def check_session_validity(auth_manager: AuthManager):
    """
    Überprüft bei JEDEM Seitenaufruf ob der Benutzer noch aktiv ist.
    Muss am Anfang jeder Seite aufgerufen werden (außer Login-Seite).
    
    Returns:
        True = Session gültig, weiter machen
        False = Session ungültig, wurde bereits ausgeloggt
    """
    # Wenn nicht eingeloggt, nichts zu prüfen
    if not st.session_state.get("authenticated", False):
        return False
    
    username = st.session_state.get("username")
    if not username:
        return False
    
    # Status prüfen
    status = auth_manager.check_user_status(username)
    
    # Wenn ungültig -> Logout und Fehlermeldung
    if status["should_logout"]:
        # Session-Daten löschen
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.role = None
        
        # Fehlermeldung anzeigen
        st.error(f"🚫 Du wurdest ausgeloggt: {status['message']}")
        st.info("Bitte melde dich erneut an.")
        st.stop()  # Verhindert weitere Ausführung
        return False
    
    # Status hat sich geändert? (z.B. von User zu Admin befördert)
    if status["role"] != st.session_state.get("role"):
        st.session_state.role = status["role"]
        st.info(f"ℹ️ Deine Rolle wurde aktualisiert: {status['role']}")
        st.rerun()
    
    return True


# ---------------------- BEISPIEL MAIN.PY ----------------------
def main():
    st.set_page_config(page_title="Quiz App", page_icon="📝", layout="wide")
    
    # Auth Manager initialisieren
    if "auth_manager" not in st.session_state:
        st.session_state.auth_manager = AuthManager()
    
    auth_manager = st.session_state.auth_manager
    
    # Initialize Session State
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "role" not in st.session_state:
        st.session_state.role = None
    
    # ========== LOGIN SEITE ==========
    if not st.session_state.authenticated:
        st.title("🔐 Login")
        
        with st.form("login_form"):
            username = st.text_input("Benutzername", key="login_username")
            password = st.text_input("Passwort", type="password", key="login_password")
            submit = st.form_submit_button("Anmelden")
            
            if submit:
                if username and password:
                    result = auth_manager.login(username, password)
                    
                    if result["success"]:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.role = result["role"].value
                        st.success(result["message"])
                        st.rerun()
                    else:
                        st.error(result["message"])
                else:
                    st.warning("Bitte Benutzername und Passwort eingeben")
        
        return
    
    # ========== GESCHÜTZTE BEREICHE ==========
    # ⚠️ WICHTIG: Session-Check bei JEDEM Seitenaufruf!
    if not check_session_validity(auth_manager):
        return  # Wurde bereits ausgeloggt
    
    # Ab hier ist der Benutzer garantiert aktiv und berechtigt
    st.sidebar.title(f"👤 {st.session_state.username}")
    st.sidebar.write(f"**Rolle:** {st.session_state.role}")
    
    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.role = None
        st.rerun()
    
    # ========== NAVIGATION ==========
    page = st.sidebar.radio(
        "Navigation",
        ["Quiz", "Profil", "Admin"] if st.session_state.role == "admin" else ["Quiz", "Profil"]
    )
    
    # ========== SEITEN ==========
    if page == "Quiz":
        show_quiz_page(auth_manager)
    elif page == "Profil":
        show_profile_page(auth_manager)
    elif page == "Admin":
        show_admin_page(auth_manager)


# ---------------------- BEISPIEL SEITEN ----------------------
def show_quiz_page(auth_manager):
    """Beispiel Quiz-Seite"""
    # Session nochmal checken (optional, aber empfohlen bei langen Seiten)
    if not check_session_validity(auth_manager):
        return
    
    st.title("📝 Quiz")
    st.write("Hier kommt dein Quiz...")


def show_profile_page(auth_manager):
    """Beispiel Profil-Seite"""
    if not check_session_validity(auth_manager):
        return
    
    st.title("👤 Profil")
    
    user = auth_manager.users.get(st.session_state.username)
    if user:
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Benutzername", user.username)
            st.metric("Rolle", user.role.value)
            st.metric("Status", "✅ Aktiv" if user.active else "❌ Deaktiviert")
        
        with col2:
            st.metric("Erstellt", user.created_at.strftime("%d.%m.%Y %H:%M"))
            if user.last_login:
                st.metric("Letzter Login", user.last_login.strftime("%d.%m.%Y %H:%M"))
    
    # Passwort ändern
    st.subheader("🔒 Passwort ändern")
    with st.form("change_password"):
        old_pw = st.text_input("Altes Passwort", type="password")
        new_pw = st.text_input("Neues Passwort", type="password")
        new_pw2 = st.text_input("Neues Passwort wiederholen", type="password")
        
        if st.form_submit_button("Passwort ändern"):
            if new_pw != new_pw2:
                st.error("Neue Passwörter stimmen nicht überein")
            else:
                success, msg = auth_manager.change_password(
                    st.session_state.username, old_pw, new_pw
                )
                if success:
                    st.success(msg)
                else:
                    st.error(msg)


def show_admin_page(auth_manager):
    """Beispiel Admin-Seite"""
    if not check_session_validity(auth_manager):
        return
    
    # Zusätzlicher Admin-Check
    if st.session_state.role != "admin":
        st.error("⛔ Keine Berechtigung")
        return
    
    st.title("⚙️ Admin-Panel")
    
    # Benutzerliste
    st.subheader("👥 Benutzerverwaltung")
    
    users = auth_manager.get_all_users()
    
    for username, user in users.items():
        with st.expander(f"{'👑' if user.role.value == 'admin' else '👤'} {username}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Rolle:** {user.role.value}")
                st.write(f"**Status:** {'✅ Aktiv' if user.active else '❌ Deaktiviert'}")
                if user.is_locked():
                    remaining = user.get_lockout_remaining()
                    if remaining:
                        minutes = int(remaining.total_seconds() / 60)
                        st.write(f"🔒 **Gesperrt:** {minutes} Min.")
            
            with col2:
                if st.button(f"{'Deaktivieren' if user.active else 'Aktivieren'}", 
                           key=f"toggle_{username}"):
                    success, msg = auth_manager.toggle_user_active(username)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                
                if user.is_locked():
                    if st.button("🔓 Entsperren", key=f"unlock_{username}"):
                        success, msg = auth_manager.unlock_user(username)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
            
            with col3:
                if user.role.value == "user":
                    if st.button("↗️ Zu Admin", key=f"promote_{username}"):
                        success, msg = auth_manager.promote_to_admin(username)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                else:
                    if st.button("↘️ Zu User", key=f"demote_{username}"):
                        success, msg = auth_manager.demote_from_admin(username)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                
                if st.button("🗑️ Löschen", key=f"delete_{username}"):
                    if username == st.session_state.username:
                        st.error("Du kannst dich nicht selbst löschen!")
                    else:
                        success, msg = auth_manager.delete_user(username)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)


if __name__ == "__main__":
    main()