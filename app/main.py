import streamlit as st
import json
import os
import random
from datetime import datetime
from user_management import (
    authenticate_user,
    get_active_users,
    deactivate_user,
    change_password,
    load_answers,
    save_answer
)


# Pfad zu den gespeicherten Antworten
ANSWERS_FILE = "./data/answers"

# Initialisiere Session State Variablen
if "authentifiziert" not in st.session_state:
    st.session_state["authentifiziert"] = False
if "passwort" not in st.session_state:
    st.session_state["passwort"] = ""
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False
if "show_answer" not in st.session_state:
    st.session_state["show_answer"] = False
if "needs_password_change" not in st.session_state:
    st.session_state["needs_password_change"] = False
if "new_password" not in st.session_state:
    st.session_state["new_password"] = ""
if "confirm_password" not in st.session_state:
    st.session_state["confirm_password"] = ""
if "show_quiz" not in st.session_state:
    st.session_state["show_quiz"] = False

def check_password():
    success, message, needs_pw_change = authenticate_user(
        st.session_state["username"].strip(),
        st.session_state["passwort"]
    )
    
    if success:
        st.session_state["authentifiziert"] = True
        st.session_state["is_admin"] = (st.session_state["username"] == ADMIN_USERNAME)
        st.session_state["needs_password_change"] = needs_pw_change
        
        # Wenn Admin-Login erfolgreich war, speichere das Admin-Passwort
        if st.session_state["is_admin"]:
            st.session_state["admin_password"] = st.session_state["passwort"]
        
        if needs_pw_change:
            st.warning("Sie verwenden das Standard-Passwort. Bitte ändern Sie es in den Einstellungen.")
        if message:
            st.success(message)
        else:
            st.success(f"Erfolgreich angemeldet als {st.session_state['username']}")
    else:
        st.error(message)

def save_answer(entry: dict):
    """Speichert eine Antwort in ANSWERS_FILE."""
    os.makedirs(os.path.dirname(ANSWERS_FILE), exist_ok=True)
    
    # Lade existierende Antworten
    answers = []
    if os.path.exists(ANSWERS_FILE):
        with open(ANSWERS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    answers.append(json.loads(line.strip()))
                except:
                    continue
    
    # Füge neue Antwort hinzu
    answers.append(entry)
    
    # Speichere alle Antworten
    with open(ANSWERS_FILE, "w", encoding="utf-8") as f:
        for answer in answers:
            f.write(json.dumps(answer, ensure_ascii=False) + "\n")

def load_answers():
    """Lädt alle gespeicherten Antworten (Liste von dicts)."""
    if not os.path.exists(ANSWERS_FILE):
        return []
    entries = []
    with open(ANSWERS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except Exception:
                continue
    return entries

def show_login_page():
    st.markdown("""
        <div style='display:flex;flex-direction:column;align-items:center;justify-content:center;height:60vh;'>
            <h1 style='font-size:2.6rem;margin-bottom:1.2rem;color:#2d3436;'>Willkommen zum Quiz</h1>
            <p style='font-size:1.2rem;color:#636e72;'>Bitte melde dich an, um fortzufahren.</p>
        </div>
    """, unsafe_allow_html=True)
    st.text_input("Benutzername", key="username")
    st.text_input("Passwort", type="password", key="passwort", on_change=check_password)

def show_main_content():
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(120deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        .quiz-container {
            background: #fff;
            padding: 28px 24px;
            border-radius: 18px;
            margin: 24px auto;
            color: #222;
            box-shadow: 0 8px 32px rgba(44,62,80,0.10);
            border: 1px solid #dfe6e9;
            max-width: 600px;
        }
        .quiz-container.highlight {
            box-shadow: 0 16px 40px rgba(44,62,80,0.18);
            border: 1.5px solid #636e72;
            background: linear-gradient(180deg, #f8f9fa 98%, #f1f2f6 95%);
        }
        .correct-answer {
            color: #00b894;
            font-weight: bold;
            font-size: 1.1rem;
        }
        .incorrect-answer {
            color: #d63031;
            font-weight: bold;
            font-size: 1.1rem;
        }
        .question-title {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 0.5em;
        }
        .answer-radio label {
            font-size: 1.08rem;
        }
        </style>
    """, unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;margin-top:1.5em;'>Quiz-Plattform</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;color:#636e72;'>Angemeldet als: {st.session_state['username']}</p>", unsafe_allow_html=True)

    # Sidebar: Quiz-Auswahl, Farben, und Admin-Ansicht
    st.sidebar.markdown("<h2 style='margin-bottom:0.5em;'>Einstellungen</h2>", unsafe_allow_html=True)
    quiz_choice = st.sidebar.selectbox("Quiz auswählen:", ["Kleidung", "Heilige Tiere", "Kombiniert"])
    
    # Hintergrundfarben
    st.sidebar.markdown("### Design")
    bg_color_primary = st.sidebar.color_picker("Hintergrundfarbe 1", "#f5f7fa")
    bg_color_secondary = st.sidebar.color_picker("Hintergrundfarbe 2", "#c3cfe2")
    
    # Benutzereinstellungen
    st.sidebar.markdown("### Benutzer")
    
    # Passwort-Änderung
    if st.session_state["needs_password_change"]:
        st.sidebar.warning("⚠️ Bitte ändern Sie Ihr Standard-Passwort")
    st.sidebar.text_input("Neues Passwort", type="password", key="new_password")
    st.sidebar.text_input("Passwort bestätigen", type="password", key="confirm_password")
    if st.sidebar.button("Passwort ändern"):
        if st.session_state["new_password"] != st.session_state["confirm_password"]:
            st.sidebar.error("Passwörter stimmen nicht überein")
        else:
            success, msg = change_password(
                st.session_state["username"],
                st.session_state["passwort"],
                st.session_state["new_password"]
            )
            if success:
                st.session_state["passwort"] = st.session_state["new_password"]
                st.session_state["needs_password_change"] = False
                st.session_state["new_password"] = ""
                st.session_state["confirm_password"] = ""
                st.sidebar.success(msg)
            else:
                st.sidebar.error(msg)
    
    st.sidebar.markdown("---")
    show_saved = st.sidebar.checkbox("Gespeicherte Antworten anzeigen", value=False)
    if st.sidebar.button("Abmelden"):
        st.session_state["authentifiziert"] = False
        st.session_state["passwort"] = ""
        st.session_state["username"] = ""
        for k in list(st.session_state.keys()):
            if isinstance(k, str) and (k.endswith("_submitted") or k.endswith("_score") or "__" in k):
                try:
                    del st.session_state[k]
                except Exception:
                    pass
        st.rerun()
    
    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(135deg, {bg_color_primary} 0%, {bg_color_secondary} 100%);
        }}
        </style>
    """, unsafe_allow_html=True)

    # Define quizzes with randomized options
    def randomize_options(question):
        """Mischt die Antwortoptionen eines Quiz-Elements."""
        options = question["optionen"].copy()
        correct = question["richtig"]
        random.shuffle(options)
        return {
            "frage": question["frage"],
            "optionen": options,
            "richtig": correct
        }

    quizzes = {
        "Kleidung": {
            "id": "kleidung",
            "questions": {
                "kleidung1": randomize_options({
                    "frage": "Welches Kleidungsstück ist bei hinduistischen Frauen weit verbreitet?",
                    "optionen": ["Sari", "Kimono", "Dirndl", "Kaftan"],
                    "richtig": "Sari"
                }),
                "kleidung2": randomize_options({
                    "frage": "Welche Farbe wird traditionell bei hinduistischen Hochzeiten getragen?",
                    "optionen": ["Schwarz", "Weiß", "Rot", "Blau"],
                    "richtig": "Rot"
                })
            }
        },
        "Heilige Tiere": {
            "id": "tiere",
            "questions": {
                "tier1": {"frage": "Welches Tier wird als Reittier (Vahana) von Lord Shiva betrachtet?", "optionen": ["Elefant", "Stier Nandi", "Pfau", "Löwe"], "richtig": "Stier Nandi"},
                "tier2": {"frage": "Welches Tier wird mit Lord Ganesha in Verbindung gebracht?", "optionen": ["Maus", "Schlange", "Affe", "Tiger"], "richtig": "Maus"},
                "tier3": {"frage": "Welches Tier gilt als heilig und wird als 'Mutter' verehrt?", "optionen": ["Schaf", "Kuh", "Ziege", "Pferd"], "richtig": "Kuh"}
            }
        },
        "Kombiniert": {
            "id": "kombiniert",
            "questions": {}
        }
    }

    # Kombiniere Fragen für den Kombiniert-Quiz
    quizzes["Kombiniert"]["questions"] = {**quizzes["Kleidung"]["questions"], **quizzes["Heilige Tiere"]["questions"]}

    selected_quiz = quizzes[quiz_choice]
    questions = selected_quiz["questions"]

    st.markdown("<h3 style='text-align:center;'>Teste dein Wissen</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#636e72;'>Beantworte die Fragen und klicke auf 'Weiter'</p>", unsafe_allow_html=True)

    quiz_key_prefix = selected_quiz["id"]
    # Ensure session state containers exist for this quiz
    if f"{quiz_key_prefix}_submitted" not in st.session_state:
        st.session_state[f"{quiz_key_prefix}_submitted"] = False
    if f"{quiz_key_prefix}_score" not in st.session_state:
        st.session_state[f"{quiz_key_prefix}_score"] = 0

    # Stufenweises Quiz ohne st.form (Buttons dürfen nicht in einer Form verwendet werden)
    q_ids = list(questions.keys())
    step_key = f"{quiz_key_prefix}_step"
    if step_key not in st.session_state:
        st.session_state[step_key] = 0

    current_index = st.session_state[step_key]
    if current_index < 0:
        current_index = 0
    if current_index >= len(q_ids):
        current_index = len(q_ids) - 1

    # Zeige aktuelle Frage
    current_qid = q_ids[current_index]
    q_data = questions[current_qid]
    full_key = f"{quiz_key_prefix}__{current_qid}"
    st.markdown(f'<div class="quiz-container highlight">', unsafe_allow_html=True)
    st.markdown(f"<div class='question-title'>Frage {current_index+1} von {len(q_ids)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:1.15rem;margin-bottom:0.7em;'><b>{q_data['frage']}</b></div>", unsafe_allow_html=True)
    user_answer = st.radio("Antwort auswählen:", q_data['optionen'], key=full_key)
    
    # Zeige Ergebnis nur nach dem Klicken auf "Weiter"
    if st.session_state.get("show_answer"):
        is_correct = user_answer == q_data['richtig']
        if is_correct:
            st.success("✓ Richtig!")
        else:
            st.error(f"✗ Falsch! Die richtige Antwort ist: {q_data['richtig']}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    # Top-right area: progress & Weiter-Button
    left_col, right_col = st.columns([3, 1])
    with right_col:
        answered = sum(1 for q in q_ids if st.session_state.get(f"{quiz_key_prefix}__{q}") is not None)
        score_so_far = sum(1 for q in q_ids if st.session_state.get(f"{quiz_key_prefix}__{q}") == questions[q]['richtig'])
        percent_so_far = int(score_so_far / max(1, len(q_ids)) * 100)
        st.markdown(f"<div style='text-align:center;margin-bottom:0.5em;'><b>Fortschritt</b></div>", unsafe_allow_html=True)
        st.progress(percent_so_far)
        st.markdown(f"<div style='text-align:center;font-size:1.1rem;color:#636e72;'>Richtig: <b style='color:#00b894'>{score_so_far}</b> / Falsch: <b style='color:#d63031'>{answered-score_so_far}</b></div>", unsafe_allow_html=True)
        if st.button("Weiter ▶", key=f"weiter_{quiz_key_prefix}"):
            # erlaube weitergehen nur, wenn eine Antwort vorhanden
            if st.session_state.get(full_key) is None:
                st.warning("Bitte wähle eine Antwort, bevor du weitergehst.")
            else:
                # save partial answers on Weiter
                partial_answers = {q: st.session_state.get(f"{quiz_key_prefix}__{q}") for q in q_ids if st.session_state.get(f"{quiz_key_prefix}__{q}") is not None}
                partial_entry = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "quiz": quiz_key_prefix,
                    "questions_count": len(q_ids),
                    "answered": len(partial_answers),
                    "partial": True,
                    "answers": partial_answers
                }
                try:
                    save_answer(partial_entry)
                except Exception:
                    pass

                if st.session_state[step_key] < len(q_ids) - 1:
                    st.session_state[step_key] += 1
                else:
                    # last question: prüfen, ob alle Fragen beantwortet sind
                    all_answered = all(st.session_state.get(f"{quiz_key_prefix}__{q}") is not None for q in q_ids)
                    if not all_answered:
                        st.warning("Bitte beantworte alle Fragen, bevor das Quiz abgeschlossen wird.")
                    else:
                        # auto-evaluate and save final result
                        score = 0
                        answers = {}
                        for q_id in q_ids:
                            fk = f"{quiz_key_prefix}__{q_id}"
                            ua = st.session_state.get(fk)
                            answers[q_id] = ua
                            qd = questions[q_id]
                            if ua == qd['richtig']:
                                score += 1

                        st.session_state[f"{quiz_key_prefix}_submitted"] = True
                        st.session_state[f"{quiz_key_prefix}_score"] = score
                        percent = int(score / max(1, len(q_ids)) * 100)
                        st.success(f"Quiz abgeschlossen: {percent}% ({score}/{len(q_ids)})")
                        final_entry = {
                            "timestamp": datetime.utcnow().isoformat() + "Z",
                            "quiz": quiz_key_prefix,
                            "questions_count": len(q_ids),
                            "score": score,
                            "percent": percent,
                            "partial": False,
                            "answers": answers
                        }
                        # Füge Benutzername zu den Antworten hinzu
                    final_entry["username"] = st.session_state["username"]
                    try:
                        save_answer(final_entry)
                    except Exception:
                        pass
                    # Reset show_answer state
                    st.session_state["show_answer"] = False

    # Wenn bereits eingereicht wurde, zeige Details
    if st.session_state.get(f"{quiz_key_prefix}_submitted"):
        st.markdown("<h3 style='text-align:center;margin-top:2em;'>📊 Deine Ergebnisse</h3>", unsafe_allow_html=True)
        score = st.session_state.get(f"{quiz_key_prefix}_score", 0)
        st.markdown(f"<div style='text-align:center;font-size:1.2rem;margin-bottom:1em;'>Du hast <b style='color:#00b894'>{score}</b> von <b>{len(questions)}</b> Fragen richtig beantwortet.</div>", unsafe_allow_html=True)
        for q_id, q_data in questions.items():
            full_key = f"{quiz_key_prefix}__{q_id}"
            user_answer = st.session_state.get(full_key)
            is_correct = user_answer == q_data['richtig']
            st.markdown(f'<div class="quiz-container">', unsafe_allow_html=True)
            st.markdown(f"<div class='question-title'>{q_data['frage']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='margin-bottom:0.5em;'>Deine Antwort: <b>{user_answer if user_answer else 'Keine Antwort'}</b></div>", unsafe_allow_html=True)
            if user_answer is not None:
                color = "#00b894" if is_correct else "#d63031"
                icon = "✅" if is_correct else "❌"
                st.markdown(f"<div style='background:#eee;border-radius:8px;padding:4px;margin-top:6px;'><div style='width:100%;background:{color};height:14px;border-radius:6px;'></div></div>", unsafe_allow_html=True)
                if is_correct:
                    st.markdown(f'<p class="correct-answer">{icon} Richtig!</p>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<p class="incorrect-answer">{icon} Falsch! Die richtige Antwort ist: <b>{q_data["richtig"]}</b></p>', unsafe_allow_html=True)
            else:
                st.info("Noch nicht beantwortet")
            st.markdown('</div>', unsafe_allow_html=True)

    # Gespeicherte Antworten und Highscores
    if show_saved:
        st.sidebar.markdown("---")
        entries = load_answers()
        
        if st.session_state["is_admin"]:
            st.sidebar.markdown("### Alle Antworten")
            if not entries:
                st.sidebar.write("Keine Einträge gefunden.")
            else:
                for e in entries[::-1]:
                    st.sidebar.markdown(f"**{e.get('username', '-')}** ({e.get('quiz','-')})")
                    st.sidebar.write(f"Score: {e.get('score',0)} / {e.get('questions_count',0)}")
                    st.sidebar.write(f"Antworten: {e.get('answers', {})}")
        
        # Highscore-Tabelle
        st.markdown("### Highscores")
        if entries:
            scores = {}
            for e in entries:
                if not e.get('partial', True):  # Nur vollständige Quizze
                    username = e.get('username', 'Unbekannt')
                    quiz = e.get('quiz', '-')
                    score = e.get('score', 0)
                    if (username, quiz) not in scores or scores[(username, quiz)] < score:
                        scores[(username, quiz)] = score
            
            # Erstelle Tabelle
            if scores:
                data = []
                for (username, quiz), score in scores.items():
                    data.append({"Benutzer": username, "Quiz": quiz, "Punkte": score})
                st.table(data)

    # Entfernt - Abmelde-Button ist jetzt in der Sidebar

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
            if col2.button("❌", key=f"remove_{user}", help="Benutzer entfernen"):
                with st.spinner(f"Entferne Benutzer {user}..."):
                    admin_pw = st.session_state.get("admin_password", "")
                    success, msg = deactivate_user(admin_pw, user)
                    if success:
                        st.success(f"Benutzer {user} wurde erfolgreich entfernt und geblacklistet.")
                        st.rerun()
                    else:
                        st.error(f"Fehler: {msg}")

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

    # Sidebar und Quiz-Layout
    st.sidebar.markdown("<h2 style='margin-bottom:0.5em;'>Einstellungen</h2>", unsafe_allow_html=True)
    quiz_choice = st.sidebar.selectbox("Quiz auswählen:", ["Kleidung", "Heilige Tiere", "Kombiniert"])
    
    # Hintergrundfarben
    st.sidebar.markdown("### Design")
    bg_color_primary = st.sidebar.color_picker("Hintergrundfarbe 1", "#f5f7fa")
    bg_color_secondary = st.sidebar.color_picker("Hintergrundfarbe 2", "#c3cfe2")
    
    # Benutzereinstellungen
    st.sidebar.markdown("### Benutzer")
    
    # Passwort-Änderung
    if st.session_state["needs_password_change"]:
        st.sidebar.warning("⚠️ Bitte ändern Sie Ihr Standard-Passwort")
    st.sidebar.text_input("Neues Passwort", type="password", key="new_password")
    st.sidebar.text_input("Passwort bestätigen", type="password", key="confirm_password")
    if st.sidebar.button("Passwort ändern"):
        if st.session_state["new_password"] != st.session_state["confirm_password"]:
            st.sidebar.error("Passwörter stimmen nicht überein")
        else:
            success, msg = change_password(
                st.session_state["username"],
                st.session_state["passwort"],
                st.session_state["new_password"]
            )
            if success:
                st.session_state["passwort"] = st.session_state["new_password"]
                st.session_state["needs_password_change"] = False
                st.session_state["new_password"] = ""
                st.session_state["confirm_password"] = ""
                st.sidebar.success(msg)
            else:
                st.sidebar.error(msg)
    
    st.sidebar.markdown("---")
    show_saved = st.sidebar.checkbox("Gespeicherte Antworten anzeigen", value=False)
    if st.sidebar.button("Abmelden"):
        st.session_state["authentifiziert"] = False
        st.session_state["passwort"] = ""
        st.session_state["username"] = ""
        st.session_state["show_quiz"] = False
        for k in list(st.session_state.keys()):
            if isinstance(k, str) and (k.endswith("_submitted") or k.endswith("_score") or "__" in k):
                try:
                    del st.session_state[k]
                except Exception:
                    pass
        st.rerun()
    
    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(135deg, {bg_color_primary} 0%, {bg_color_secondary} 100%);
        }}
        </style>
    """, unsafe_allow_html=True)

    # Quizfragen definieren
    def randomize_options(question):
        """Mischt die Antwortoptionen eines Quiz-Elements."""
        options = question["optionen"].copy()
        correct = question["richtig"]
        random.shuffle(options)
        return {
            "frage": question["frage"],
            "optionen": options,
            "richtig": correct
        }

    quizzes = {
        "Kleidung": {
            "id": "kleidung",
            "questions": {
                "kleidung1": randomize_options({
                    "frage": "Welches Kleidungsstück ist bei hinduistischen Frauen weit verbreitet?",
                    "optionen": ["Sari", "Kimono", "Dirndl", "Kaftan"],
                    "richtig": "Sari"
                }),
                "kleidung2": randomize_options({
                    "frage": "Welche Farbe wird traditionell bei hinduistischen Hochzeiten getragen?",
                    "optionen": ["Schwarz", "Weiß", "Rot", "Blau"],
                    "richtig": "Rot"
                })
            }
        },
        "Heilige Tiere": {
            "id": "tiere",
            "questions": {
                "tier1": randomize_options({
                    "frage": "Welches Tier wird als Reittier (Vahana) von Lord Shiva betrachtet?",
                    "optionen": ["Elefant", "Stier Nandi", "Pfau", "Löwe"],
                    "richtig": "Stier Nandi"
                }),
                "tier2": randomize_options({
                    "frage": "Welches Tier wird mit Lord Ganesha in Verbindung gebracht?",
                    "optionen": ["Maus", "Schlange", "Affe", "Tiger"],
                    "richtig": "Maus"
                }),
                "tier3": randomize_options({
                    "frage": "Welches Tier gilt als heilig und wird als 'Mutter' verehrt?",
                    "optionen": ["Schaf", "Kuh", "Ziege", "Pferd"],
                    "richtig": "Kuh"
                })
            }
        }
    }
    
    # Kombiniere Fragen für den Kombiniert-Quiz
    quizzes["Kombiniert"] = {
        "id": "kombiniert",
        "questions": {
            **quizzes["Kleidung"]["questions"],
            **quizzes["Heilige Tiere"]["questions"]
        }
    }

    selected_quiz = quizzes[quiz_choice]
    questions = selected_quiz["questions"]

    quiz_key_prefix = selected_quiz["id"]
    # Ensure session state containers exist for this quiz
    if f"{quiz_key_prefix}_submitted" not in st.session_state:
        st.session_state[f"{quiz_key_prefix}_submitted"] = False
    if f"{quiz_key_prefix}_score" not in st.session_state:
        st.session_state[f"{quiz_key_prefix}_score"] = 0

    # Stufenweises Quiz
    q_ids = list(questions.keys())
    step_key = f"{quiz_key_prefix}_step"
    if step_key not in st.session_state:
        st.session_state[step_key] = 0

    current_index = st.session_state[step_key]
    if current_index < 0:
        current_index = 0
    if current_index >= len(q_ids):
        current_index = len(q_ids) - 1

    # Zeige aktuelle Frage
    current_qid = q_ids[current_index]
    q_data = questions[current_qid]
    full_key = f"{quiz_key_prefix}__{current_qid}"
    st.markdown(f'<div class="quiz-container highlight">', unsafe_allow_html=True)
    st.markdown(f"<div class='question-title'>Frage {current_index+1} von {len(q_ids)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:1.15rem;margin-bottom:0.7em;'><b>{q_data['frage']}</b></div>", unsafe_allow_html=True)
    st.radio("Antwort auswählen:", q_data['optionen'], key=full_key)
    
    # Zeige Ergebnis nur nach dem Klicken auf "Weiter"
    if st.session_state.get("show_answer"):
        is_correct = st.session_state[full_key] == q_data['richtig']
        if is_correct:
            st.success("✓ Richtig!")
        else:
            st.error(f"✗ Falsch! Die richtige Antwort ist: {q_data['richtig']}")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Top-right area: progress & Weiter-Button
    left_col, right_col = st.columns([3, 1])
    with right_col:
        # calculate answered and current score so far
        answered = sum(1 for q in q_ids if st.session_state.get(f"{quiz_key_prefix}__{q}") is not None)
        score_so_far = sum(1 for q in q_ids if st.session_state.get(f"{quiz_key_prefix}__{q}") == questions[q]['richtig'])
        percent_so_far = int(score_so_far / max(1, len(q_ids)) * 100)
        st.markdown(f"<div style='text-align:center;margin-bottom:0.5em;'><b>Fortschritt</b></div>", unsafe_allow_html=True)
        st.progress(percent_so_far)
        st.markdown(f"<div style='text-align:center;font-size:1.1rem;color:#636e72;'>Richtig: <b style='color:#00b894'>{score_so_far}</b> / Falsch: <b style='color:#d63031'>{answered-score_so_far}</b></div>", unsafe_allow_html=True)
        
        # Weiter-Button
        if st.button("Weiter ▶", key=f"weiter_{quiz_key_prefix}"):
            if st.session_state.get(full_key) is None:
                st.warning("Bitte wähle eine Antwort, bevor du weitergehst.")
            else:
                st.session_state["show_answer"] = True
                # Speichere partielle Antworten
                partial_answers = {
                    q: st.session_state.get(f"{quiz_key_prefix}__{q}")
                    for q in q_ids
                    if st.session_state.get(f"{quiz_key_prefix}__{q}") is not None
                }
                partial_entry = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "quiz": quiz_key_prefix,
                    "questions_count": len(q_ids),
                    "answered": len(partial_answers),
                    "partial": True,
                    "username": st.session_state["username"],
                    "answers": partial_answers
                }
                try:
                    save_answer(partial_entry)
                except Exception:
                    pass

                if st.session_state[step_key] < len(q_ids) - 1:
                    st.session_state[step_key] += 1
                else:
                    # Letzte Frage: prüfe, ob alle beantwortet wurden
                    all_answered = all(
                        st.session_state.get(f"{quiz_key_prefix}__{q}") is not None
                        for q in q_ids
                    )
                    if not all_answered:
                        st.warning("Bitte beantworte alle Fragen, bevor das Quiz abgeschlossen wird.")
                    else:
                        # Auto-evaluate und speichere Endergebnis
                        score = 0
                        answers = {}
                        for q_id in q_ids:
                            fk = f"{quiz_key_prefix}__{q_id}"
                            ua = st.session_state.get(fk)
                            answers[q_id] = ua
                            qd = questions[q_id]
                            if ua == qd['richtig']:
                                score += 1

                        st.session_state[f"{quiz_key_prefix}_submitted"] = True
                        st.session_state[f"{quiz_key_prefix}_score"] = score
                        percent = int(score / max(1, len(q_ids)) * 100)
                        st.success(f"Quiz abgeschlossen: {percent}% ({score}/{len(q_ids)})")
                        final_entry = {
                            "timestamp": datetime.utcnow().isoformat() + "Z",
                            "quiz": quiz_key_prefix,
                            "questions_count": len(q_ids),
                            "score": score,
                            "percent": percent,
                            "partial": False,
                            "username": st.session_state["username"],
                            "answers": answers
                        }
                        try:
                            save_answer(final_entry)
                        except Exception:
                            pass
                        st.session_state["show_answer"] = False

    # Wenn bereits eingereicht wurde, zeige Details
    if st.session_state.get(f"{quiz_key_prefix}_submitted"):
        st.markdown("<h3 style='text-align:center;margin-top:2em;'>Deine Ergebnisse</h3>", unsafe_allow_html=True)
        score = st.session_state.get(f"{quiz_key_prefix}_score", 0)
        st.markdown(f"<div style='text-align:center;font-size:1.2rem;margin-bottom:1em;'>Du hast <b style='color:#00b894'>{score}</b> von <b>{len(questions)}</b> Fragen richtig beantwortet.</div>", unsafe_allow_html=True)
        
        # Zeige Highscores
        st.markdown("### Highscores")
        entries = load_answers()
        if entries:
            scores = {}
            for entry in entries:
                if not entry.get('partial', True):  # Nur vollständige Quizze
                    username = entry.get('username', 'Unbekannt')
                    quiz = entry.get('quiz', '-')
                    score = entry.get('score', 0)
                    if (username, quiz) not in scores or scores[(username, quiz)] < score:
                        scores[(username, quiz)] = score
            
            if scores:
                data = []
                for (username, quiz), score in scores.items():
                    data.append({"Benutzer": username, "Quiz": quiz, "Punkte": score})
                st.table(data)

    # Gespeicherte Antworten im Sidebar
    if show_saved:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Gespeicherte Antworten")
        entries = load_answers()
        if not entries:
            st.sidebar.write("Keine Einträge gefunden.")
        else:
            for e in entries[-10:][::-1]:  # Zeige nur die letzten 10 Einträge
                if e.get('username') == st.session_state["username"]:  # Zeige nur eigene Einträge
                    st.sidebar.markdown(f"**{e.get('quiz','-')}** — {e.get('timestamp','-')}")
                    st.sidebar.write(f"Score: {e.get('score',0)} / {e.get('questions_count',0)} ({e.get('percent',0)}%)")

def show_main_content():
    if st.session_state["is_admin"] and not st.session_state["show_quiz"]:
        show_admin_content()
        if st.button("Zum Quiz wechseln"):
            st.session_state["show_quiz"] = True
            st.rerun()
    else:
        show_quiz_content()

def main():
    if not st.session_state["authentifiziert"]:
        show_login_page()
        return
    # Überprüfe, ob der User gebannt ist (active: false in .data/users.json)
    user_file = "./data/users.json"
    username = st.session_state.get("username", "")
    if username:
        try:
            with open(user_file, "r", encoding="utf-8") as f:
                users = json.load(f)
            user_data = users.get(username)
            if user_data and not user_data.get("active", True):
                st.error("Du wurdest vom System gebannt und wirst jetzt ausgeloggt.")
                st.session_state["authentifiziert"] = False
                st.session_state["passwort"] = ""
                st.session_state["username"] = ""
                st.session_state["is_admin"] = False
                st.session_state["show_quiz"] = False
                st.session_state["needs_password_change"] = False
                st.session_state["new_password"] = ""
                st.session_state["confirm_password"] = ""
                st.experimental_rerun()
                return
        except Exception:
            pass
    if st.session_state.get("needs_password_change", False):
        # Zeige Pflicht-Fenster zur Passwortänderung
        st.markdown("""
            <div style='display:flex;flex-direction:column;align-items:center;justify-content:center;height:60vh;'>
                <h2 style='font-size:2.2rem;margin-bottom:1.2rem;color:#d63031;'>Passwort ändern erforderlich</h2>
                <p style='font-size:1.1rem;color:#636e72;'>Sie verwenden noch das Standard-Passwort.<br>Bitte vergeben Sie ein neues Passwort (mind. 6 Zeichen), um fortzufahren.</p>
            </div>
        """, unsafe_allow_html=True)
        st.text_input("Neues Passwort", type="password", key="new_password")
        st.text_input("Passwort bestätigen", type="password", key="confirm_password")
        if st.button("Passwort jetzt ändern"):
            if st.session_state["new_password"] != st.session_state["confirm_password"]:
                st.error("Passwörter stimmen nicht überein")
            elif len(st.session_state["new_password"]) < 6:
                st.error("Das neue Passwort muss mindestens 6 Zeichen lang sein.")
            else:
                success, msg = change_password(
                    st.session_state["username"],
                    st.session_state["passwort"],
                    st.session_state["new_password"]
                )
                if success:
                    st.session_state["passwort"] = st.session_state["new_password"]
                    st.session_state["needs_password_change"] = False
                    st.session_state["new_password"] = ""
                    st.session_state["confirm_password"] = ""
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        return
    show_main_content()

if __name__ == "__main__":
    main()
