import streamlit as st
from user_management import load_users, save_users, hash_password, load_answers

def show_admin_panel():
    st.title("Admin Dashboard")
    
    # Sicherstellen, dass ein Admin eingeloggt ist
    if ("username" not in st.session_state or 
        not st.session_state.username or 
        st.session_state.username.strip() == ""):
        st.warning("Nicht eingeloggt!")
        return
    
    # Prüfen ob der aktuelle User auch wirklich Admin ist
    current_admin = st.session_state.username
    users = load_users()
    
    if current_admin not in users:
        st.error(f"Benutzer '{current_admin}' existiert nicht!")
        return
    
    if not users[current_admin].get("is_admin", False):
        st.error("Keine Admin-Berechtigung!")
        return
    
    # State für aktualisierte User-Liste - immer fresh laden
    st.session_state.users = users
    
    st.markdown("## Benutzerverwaltung")
    
    # Neuen Benutzer hinzufügen
    with st.form("add_user_form"):
        col_new = st.columns([3, 3, 1])
        with col_new[0]:
            new_user = st.text_input("Neuer Benutzername")
        with col_new[1]:
            default_pw = st.text_input("Standardpasswort", value="4-26-2011", type="password")
        with col_new[2]:
            submitted = st.form_submit_button("Benutzer hinzufügen")
            
        if submitted and new_user:
            if new_user in users:
                st.error("Benutzer existiert bereits!")
            else:
                users[new_user] = {
                    "password": hash_password(default_pw),
                    "active": True,
                    "is_admin": False,
                    "using_default": True
                }
                save_users(users)
                st.success(f"{new_user} wurde hinzugefügt!")
                st.rerun()  # Seite neu laden um neue Daten zu zeigen
    
    st.markdown("---")
    st.markdown("### Bestehende Benutzer")
    
    # User-Actions mit eindeutigen Keys und Session-State-Behandlung
    for username, info in users.items():
        if username == current_admin:
            continue  # Admin selbst überspringen
            
        cols = st.columns([2, 1, 1, 1, 1])
        cols[0].markdown(f"**{username}**")
        cols[1].markdown("✅" if info.get("active", True) else "❌")
        cols[2].markdown("👑" if info.get("is_admin", False) else "")
        
        # Action Buttons mit Forms um Page-Reload zu vermeiden
        if not info.get("is_admin", False):
            with cols[3]:
                if info.get("active", True):
                    if st.button("Blockieren", key=f"block_{username}", use_container_width=True):
                        users[username]["active"] = False
                        save_users(users)
                        st.success(f"{username} wurde geblockt!")
                        st.rerun()
                else:
                    if st.button("Entblocken", key=f"unblock_{username}", use_container_width=True):
                        users[username]["active"] = True
                        save_users(users)
                        st.success(f"{username} wurde entblockt!")
                        st.rerun()
            
            with cols[4]:
                if st.button("Admin geben", key=f"make_admin_{username}", use_container_width=True):
                    users[username]["is_admin"] = True
                    save_users(users)
                    st.success(f"{username} ist jetzt Admin!")
                    st.rerun()
        else:
            # Wenn User bereits Admin ist
            with cols[3]:
                st.write("—")
            with cols[4]:
                if st.button("Admin entfernen", key=f"remove_admin_{username}", use_container_width=True):
                    users[username]["is_admin"] = False
                    save_users(users)
                    st.success(f"{username} ist kein Admin mehr!")
                    st.rerun()
    
    st.markdown("---")
    st.markdown("## Bestenliste")
    
    # Bestenliste laden und anzeigen
    answers = load_answers()
    if not answers:
        st.info("Noch keine Ergebnisse vorhanden.")
        return
    
    user_stats = {}
    for entry in answers:
        username = entry.get("username")
        if username not in user_stats:
            user_stats[username] = {"total": 0, "correct": 0}
        user_stats[username]["total"] += 1
        if entry.get("correct", False):
            user_stats[username]["correct"] += 1
    
    leaderboard = []
    for user, stats in user_stats.items():
        total = stats["total"]
        correct = stats["correct"]
        percent = (correct/total)*100 if total > 0 else 0
        leaderboard.append((user, correct, total, percent))
    
    leaderboard.sort(key=lambda x: x[3], reverse=True)
    
    # Bessere Darstellung der Bestenliste
    if leaderboard:
        st.dataframe([{
            "Rang": i+1,
            "Benutzer": u[0],
            "Richtige Antworten": f"{u[1]} / {u[2]}",
            "Erfolgsquote": f"{u[3]:.1f}%"
        } for i, u in enumerate(leaderboard)], use_container_width=True)