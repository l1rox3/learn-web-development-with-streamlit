import streamlit as st
from streamlit_autorefresh import st_autorefresh

# Auto-Refresh alle 3 Sekunden (3000 ms)
count = st_autorefresh(interval=3000, limit=None, key="refresh")

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
                success, msg = deactivate_user(st.session_state["passwort"], user)
                if success:
                    st.success(f"Benutzer {user} wurde entfernt")
                    st.experimental_rerun()  # Seite sofort neu laden
                else:
                    st.error(msg)

    # Quiz-Statistiken & Bearbeitung
    st.markdown("### Quiz-Statistiken")
    entries = load_answers()
    if entries:
        for entry in entries:
            st.markdown(f"**Benutzer:** {entry.get('username', 'Unbekannt')} | Quiz: {entry.get('quiz', '-')}")
            
            # Werte editierbar machen
            score = st.number_input(f"Punkte ({entry.get('username')})", value=entry.get('score', 0), step=1, key=f"score_{entry.get('username')}")
            percent = st.number_input(f"Prozent ({entry.get('username')})", value=entry.get('percent', 0), step=1, key=f"percent_{entry.get('username')}")
            timestamp = st.text_input(f"Datum ({entry.get('username')})", value=entry.get('timestamp', '-'), key=f"timestamp_{entry.get('username')}")

            if st.button(f"Änderungen speichern ({entry.get('username')})", key=f"save_{entry.get('username')}"):
                entry['score'] = score
                entry['percent'] = percent
                entry['timestamp'] = timestamp
                save_answer(entry)
                st.success(f"Änderungen für {entry.get('username')} gespeichert!")
    else:
        st.info("Noch keine Quiz-Ergebnisse vorhanden")
    
    # Alle Ergebnisse löschen
    if st.button("Alle Ergebnisse löschen"):
        for f_name in os.listdir(ANSWERS_DIR):
            if f_name.endswith(".json"):
                os.remove(os.path.join(ANSWERS_DIR, f_name))
        st.success("Alle Ergebnisse wurden gelöscht")
        st.experimental_rerun()
