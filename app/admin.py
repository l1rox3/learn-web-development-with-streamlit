import streamlit as st
from app.auth import load_users, save_users, hash_password, load_answers


def show_admin_panel():
    st.title("🛠 Admin Dashboard")

    # Reload-Button
    if st.button("🔄 Daten aktualisieren"):
        st.rerun()

    # Prüfen ob Admin eingeloggt
    if "username" not in st.session_state or not st.session_state.username.strip():
        st.warning("Nicht eingeloggt!")
        return

    current_admin = st.session_state.username
    users = load_users()
    if current_admin not in users:
        st.error(f"Benutzer '{current_admin}' existiert nicht!")
        return
    if not users[current_admin].get("is_admin", False):
        st.error("Keine Admin-Berechtigung!")
        return

    # Session-State aktualisieren
    st.session_state.users = users

    st.markdown("## 👥 Benutzerverwaltung")

    # Neuen Benutzer hinzufügen
    with st.expander("Neuen Benutzer hinzufügen"):
        col_new = st.columns([3, 3, 1])
        with col_new[0]:
            new_user = st.text_input("Benutzername")
        with col_new[1]:
            default_pw = st.text_input("Standardpasswort", value="4-26-2011", type="password")
        with col_new[2]:
            if st.button("➕ Hinzufügen"):
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
                    st.rerun()


    st.markdown("---")
    st.markdown("### Bestehende Benutzer")

    # User-Liste anzeigen
    for username, info in users.items():
        if username == current_admin:
            continue  # Admin selbst überspringen

        cols = st.columns([2, 1, 1, 1, 1])
        cols[0].markdown(f"**{username}**")
        cols[1].markdown("✅" if info.get("active", True) else "❌", unsafe_allow_html=True)
        cols[2].markdown("👑" if info.get("is_admin", False) else "")

        # Block / Unblock
        with cols[3]:
            if info.get("active", True):
                if st.button("Blockieren", key=f"block_{username}"):
                    users[username]["active"] = False
                    save_users(users)
                    st.success(f"{username} wurde geblockt!")
                    st.rerun()

            else:
                if st.button("Entblocken", key=f"unblock_{username}"):
                    users[username]["active"] = True
                    save_users(users)
                    st.success(f"{username} wurde entblockt!")
                    st.rerun()


        # Admin setzen / entfernen
        with cols[4]:
            if info.get("is_admin", False):
                if st.button("Admin entfernen", key=f"remove_admin_{username}"):
                    users[username]["is_admin"] = False
                    save_users(users)
                    st.success(f"{username} ist kein Admin mehr!")
                    st.rerun()

            else:
                if st.button("Admin geben", key=f"make_admin_{username}"):
                    users[username]["is_admin"] = True
                    save_users(users)
                    st.success(f"{username} ist jetzt Admin!")
                    st.rerun()


    st.markdown("---")
    st.markdown("## 🏆 Bestenliste")

    answers = load_answers()
    if not answers:
        st.info("Noch keine Ergebnisse vorhanden.")
        return

    # Statistik vorbereiten
    user_stats = {}
    for entry in answers:
        uname = entry.get("username")
        if uname not in user_stats:
            user_stats[uname] = {"total": 0, "correct": 0}
        user_stats[uname]["total"] += 1
        if entry.get("correct", False):
            user_stats[uname]["correct"] += 1

    leaderboard = []
    for user, stats in user_stats.items():
        total = stats["total"]
        correct = stats["correct"]
        percent = (correct/total)*100 if total > 0 else 0
        leaderboard.append((user, correct, total, percent))

    leaderboard.sort(key=lambda x: x[3], reverse=True)

    # Schöne Darstellung
    if leaderboard:
        table_data = []
        for i, (user, correct, total, percent) in enumerate(leaderboard):
            table_data.append({
                "Rang": i+1,
                "Benutzer": user,
                "Richtige Antworten": f"{correct}/{total}",
                "Erfolgsquote": f"{percent:.1f}%"
            })
        st.table(table_data)
