def show_admin_content():
    st.markdown("<h1 style='text-align:center;margin-top:1.5em;'>Admin-Bereich</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;color:#636e72;'>Administrator: {st.session_state['username']}</p>", unsafe_allow_html=True)

    # Benutzerverwaltung
    st.markdown("### Benutzerverwaltung")
    active_users = get_active_users()
    
    for user in active_users:
        col1, col2 = st.columns([3, 1])
        col1.write(user)
        if user != ADMIN_USERNAME:
            if col2.button("Entfernen", key=f"remove_{user}"):
                if deactivate_user(st.session_state["passwort"], user):
                    st.success(f"Benutzer {user} wurde entfernt")
                    st.rerun()
                else:
                    st.error("Fehler beim Entfernen des Benutzers")

    # Quiz-Statistiken
    st.markdown("### Quiz-Statistiken")
    entries = load_answers()
    if entries:
        df_data = []
        for entry in entries:
            if not entry.get('partial', True):  # Nur vollständige Quizze
                df_data.append({
                    "Benutzer": entry.get('username', 'Unbekannt'),
                    "Quiz": entry.get('quiz', '-'),
                    "Punkte": entry.get('score', 0),
                    "Prozent": entry.get('percent', 0),
                    "Datum": entry.get('timestamp', '-')
                })
        if df_data:
            st.dataframe(df_data)
    else:
        st.info("Noch keine Quiz-Ergebnisse vorhanden")

def show_quiz_content():
    st.markdown("<h1 style='text-align:center;margin-top:1.5em;'>Quiz-Plattform</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;color:#636e72;'>Angemeldet als: {st.session_state['username']}</p>", unsafe_allow_html=True)
    
    # Für Admin: Button zum Zurückkehren zum Admin-Bereich
    if st.session_state["is_admin"] and st.session_state["show_quiz"]:
        if st.button("Zurück zum Admin-Bereich"):
            st.session_state["show_quiz"] = False
            st.rerun()
            return