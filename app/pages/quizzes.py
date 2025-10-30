import streamlit as st
import random
import time
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import pandas as pd

# Import der Auth-Funktionen
import sys
sys.path.append('.')
from pages.auth import AuthManager

# Quiz Daten
HINDUISMUS_QUIZ = {
    "title": "Kleidung und Tiere im Hinduismus",
    "questions": [
        {
            "question": "Welche Bedeutung hat Kleidung im Hinduismus?",
            "options": [
                "Sie steht für Respekt gegenüber Gott und Tradition",
                "Sie ist nur für religiöse Führer wichtig",
                "Sie hat keine religiöse Bedeutung",
                "Sie muss immer weiß sein"
            ],
            "answer": "Sie steht für Respekt gegenüber Gott und Tradition"
        },
        {
            "question": "Wann spielt Kleidung im Hinduismus eine besonders wichtige Rolle?",
            "options": [
                "Bei Festen und in Tempeln",
                "Nur bei Hochzeiten",
                "Nur beim Gebet zu Hause",
                "Nie, Kleidung ist unwichtig"
            ],
            "answer": "Bei Festen und in Tempeln"
        },
        {
            "question": "Gibt es im Hinduismus feste Kleidungsvorschriften?",
            "options": [
                "Nein, es gibt keine festen Vorschriften",
                "Ja, alle müssen Weiß tragen",
                "Ja, nur Männer tragen traditionelle Kleidung",
                "Ja, Kleidung ist streng vorgeschrieben"
            ],
            "answer": "Nein, es gibt keine festen Vorschriften"
        },
        {
            "question": "Was ist ein Sari?",
            "options": [
                "Ein ca. 6m langer Stoffstreifen, mehrfach um den Körper gewickelt",
                "Ein weites Hemd für Männer",
                "Eine Kombination aus Hose und Oberteil",
                "Ein langes Jackett mit Stehkragen"
            ],
            "answer": "Ein ca. 6m langer Stoffstreifen, mehrfach um den Körper gewickelt"
        },
        {
            "question": "Was kann ein Sari über die Trägerin verraten?",
            "options": [
                "Die Herkunft der Frau",
                "Ihr Alter",
                "Ihren Familienstand",
                "Ihre Religion"
            ],
            "answer": "Die Herkunft der Frau"
        },
        {
            "question": "Was gehört oft zu einem Nasenpiercing im Hinduismus?",
            "options": [
                "Eine Kette, die mit einem Ohrring verbunden ist",
                "Ein Armband",
                "Ein Stirnband",
                "Ein Ring am Finger"
            ],
            "answer": "Eine Kette, die mit einem Ohrring verbunden ist"
        },
        {
            "question": "Was ist ein Kurta?",
            "options": [
                "Ein weites, langes Hemd für Männer ohne Kragen",
                "Ein Tuch für den Kopf",
                "Ein Rock für Frauen",
                "Eine kurze Jacke"
            ],
            "answer": "Ein weites, langes Hemd für Männer ohne Kragen"
        },
        {
            "question": "Wie lang ist ein typischer Kurta?",
            "options": [
                "Er reicht bis zum Knie",
                "Er reicht bis zur Hüfte",
                "Er reicht bis zum Boden",
                "Er endet an der Taille"
            ],
            "answer": "Er reicht bis zum Knie"
        },
        {
            "question": "Was ist ein Salwar Kameez?",
            "options": [
                "Eine Kombination aus Hose und langem Oberteil",
                "Ein Stoffstreifen für Frauen",
                "Ein Hemd für Männer",
                "Eine Jacke mit Kragen"
            ],
            "answer": "Eine Kombination aus Hose und langem Oberteil"
        },
        {
            "question": "Was ist ein Dhoti?",
            "options": [
                "Ein langes Stück Stoff, in der Taille zusammengeknotet",
                "Ein Sari für Männer",
                "Eine Kombination aus Hose und Jacke",
                "Ein Stirntuch"
            ],
            "answer": "Ein langes Stück Stoff, in der Taille zusammengeknotet"
        },
        {
            "question": "Was ist ein Sherwani?",
            "options": [
                "Ein langes Jackett mit Stehkragen, das über dem Dhoti getragen wird",
                "Ein leichter Sommermantel",
                "Ein traditioneller Hut",
                "Ein religiöser Schal"
            ],
            "answer": "Ein langes Jackett mit Stehkragen, das über dem Dhoti getragen wird"
        },
        {
            "question": "Welche Rolle spielen Tiere im Hinduismus?",
            "options": [
                "Sie gelten als heilig und werden verehrt",
                "Sie werden geopfert",
                "Sie sind bedeutungslos",
                "Sie dienen nur als Arbeitstiere"
            ],
            "answer": "Sie gelten als heilig und werden verehrt"
        },
        {
            "question": "Warum werden Tiere im Hinduismus verehrt?",
            "options": [
                "Weil sie symbolische und religiöse Bedeutung haben",
                "Weil sie selten sind",
                "Weil sie gefährlich sind",
                "Weil sie schön aussehen"
            ],
            "answer": "Weil sie symbolische und religiöse Bedeutung haben"
        },
        {
            "question": "Was wird im Hinduismus NICHT mit Tieren gemacht?",
            "options": [
                "Sie werden getötet oder gegessen",
                "Sie werden verehrt",
                "Sie gelten als heilig",
                "Sie haben religiöse Bedeutung"
            ],
            "answer": "Sie werden getötet oder gegessen"
        },
        {
            "question": "Welche fünf Gaben liefert die heilige Kuh?",
            "options": [
                "Ghee, Lassi, Mist, Pflanzendünger, Urin",
                "Milch, Butter, Käse, Joghurt, Sahne",
                "Honig, Öl, Milch, Wasser, Salz",
                "Fleisch, Leder, Knochen, Fell, Milch"
            ],
            "answer": "Ghee, Lassi, Mist, Pflanzendünger, Urin"
        },
        {
            "question": "Für welchen Gott steht der Elefant?",
            "options": [
                "Ganesha - Symbol für Glück, Weisheit und Neubeginn",
                "Shiva - Symbol für Kraft und Ewigkeit",
                "Vishnu - Symbol für Schutz",
                "Brahma - Symbol für Schöpfung"
            ],
            "answer": "Ganesha - Symbol für Glück, Weisheit und Neubeginn"
        },
        {
            "question": "Für welchen Gott steht die Schlange?",
            "options": [
                "Shiva - Symbol für Kraft und Ewigkeit",
                "Ganesha - Symbol für Glück und Neubeginn",
                "Vishnu - Symbol für Schutz",
                "Seraswati - Symbol für Schönheit"
            ],
            "answer": "Shiva - Symbol für Kraft und Ewigkeit"
        },
        {
            "question": "Für welchen Gott steht der Pfau?",
            "options": [
                "Seraswati - Symbol für Stolz und Schönheit",
                "Ganesha - Symbol für Glück und Neubeginn",
                "Shiva - Symbol für Kraft",
                "Vishnu - Symbol für Schutz"
            ],
            "answer": "Seraswati - Symbol für Stolz und Schönheit"
        }
    ]
}

# Theme
THEME = {
    "name": "Purple Dream",
    "bg": "linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)",
    "surface": "rgba(255,255,255,0.05)",
    "border": "rgba(255,255,255,0.1)",
    "text": "#ffffff",
    "text_secondary": "rgba(255,255,255,0.7)",
    "accent": "#667eea",
    "accent_hover": "#764ba2",
    "card_gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
}

# Page config
st.set_page_config(
    page_title="Hinduismus Quiz",
    page_icon="🕉️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Auth Manager initialisieren
@st.cache_resource
def get_auth_manager():
    return AuthManager()

auth_manager = get_auth_manager()

# Session State Initialisierung
def initialize_session_state():
    if 'quiz_data' not in st.session_state:
        st.session_state.quiz_data = {
            'current_question': 0,
            'score': 0,
            'answers': [],
            'start_time': None,
            'question_start_time': None,
            'shuffled_options': []
        }
    
    if 'page' not in st.session_state:
        st.session_state.page = 'start'
    
    if 'username' not in st.session_state:
        query_params = st.query_params
        if 'user' in query_params:
            st.session_state.username = query_params['user']
        else:
            st.session_state.username = None

def save_result(username: str, score: int, total: int, time_taken: float, answers: List[Dict]):
    data_dir = Path("./data/answers")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    result = {
        "username": username,
        "score": score,
        "total": total,
        "percentage": round((score / total) * 100, 2),
        "time_taken": round(time_taken, 2),
        "avg_time_per_question": round(time_taken / total, 2),
        "timestamp": datetime.now().isoformat(),
        "answers": answers
    }
    
    filename = data_dir / f"{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

def load_all_results() -> List[Dict]:
    data_dir = Path("./data/answers")
    if not data_dir.exists():
        return []
    
    results = []
    for file in data_dir.glob("*.json"):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                results.append(json.load(f))
        except:
            continue
    return results

def get_leaderboard_data() -> pd.DataFrame:
    results = load_all_results()
    if not results:
        return pd.DataFrame()
    
    df = pd.DataFrame(results)
    leaderboard = df.loc[df.groupby('username')['score'].idxmax()]
    leaderboard = leaderboard.sort_values(['score', 'time_taken'], ascending=[False, True])
    return leaderboard[['username', 'score', 'percentage', 'time_taken', 'avg_time_per_question']]

def apply_theme():
    st.markdown(f"""
        <style>
        .stApp {{
            background: {THEME['bg']};
        }}
        
        .main-title {{
            font-size: 3rem;
            font-weight: 800;
            text-align: center;
            color: {THEME['text']};
            margin-bottom: 2rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .question-card {{
            background: {THEME['surface']};
            border: 2px solid {THEME['border']};
            border-radius: 20px;
            padding: 2.5rem;
            margin: 2rem 0;
            backdrop-filter: blur(10px);
        }}
        
        .question-text {{
            font-size: 1.8rem;
            font-weight: 600;
            color: {THEME['text']};
            margin-bottom: 2rem;
            text-align: center;
        }}
        
        .stats-card {{
            background: {THEME['surface']};
            border: 2px solid {THEME['border']};
            border-radius: 15px;
            padding: 1.5rem;
            text-align: center;
            backdrop-filter: blur(10px);
        }}
        
        .stat-value {{
            font-size: 2.5rem;
            font-weight: 800;
            color: {THEME['accent']};
        }}
        
        .stat-label {{
            font-size: 1rem;
            color: {THEME['text_secondary']};
            margin-top: 0.5rem;
        }}
        
        .stButton > button {{
            border-radius: 15px;
            border: 2px solid {THEME['border']};
            background: {THEME['surface']};
            color: {THEME['text']};
            transition: all 0.3s ease;
            font-weight: 600;
        }}
        
        .stButton > button:hover {{
            background: {THEME['card_gradient']};
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }}
        
        .result-card {{
            background: {THEME['card_gradient']};
            border-radius: 20px;
            padding: 3rem;
            text-align: center;
            margin: 2rem 0;
            box-shadow: 0 20px 60px rgba(0,0,0,0.4);
        }}
        
        .result-score {{
            font-size: 5rem;
            font-weight: 900;
            color: {THEME['text']};
        }}
        </style>
    """, unsafe_allow_html=True)

def show_unauthorized_page():
    st.markdown('<h1 class="main-title">🔒 Nicht autorisiert</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div class="question-card">
                <h2 style="text-align: center; color: white; margin-bottom: 2rem;">
                    Bitte melde dich zuerst an
                </h2>
                <p style="text-align: center; color: rgba(255,255,255,0.7); font-size: 1.2rem;">
                    Du musst dich auf der Hauptseite anmelden, um das Quiz spielen zu können.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Zur Hauptseite", key="go_main_btn", use_container_width=True):
            st.switch_page("main.py")

def show_start_page():
    st.markdown('<h1 class="main-title">🕉️ Hinduismus Quiz</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="question-card">', unsafe_allow_html=True)
        
        st.info(f"Angemeldet als: **{st.session_state.username}**")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("Quiz starten", key="start_btn", use_container_width=True):
            st.session_state.quiz_data = {
                'current_question': 0,
                'score': 0,
                'answers': [],
                'start_time': time.time(),
                'question_start_time': None,
                'shuffled_options': []
            }
            st.session_state.page = 'quiz'
            st.rerun()
        
        if st.button("Leaderboard ansehen", key="leaderboard_btn", use_container_width=True):
            st.session_state.page = 'leaderboard'
            st.rerun()
        
        if st.button("Zurück zur Hauptseite", key="back_main_btn", use_container_width=True):
            st.switch_page("main.py")

def show_quiz_page():
    questions = HINDUISMUS_QUIZ['questions']
    current_q = st.session_state.quiz_data['current_question']
    
    if current_q >= len(questions):
        st.session_state.page = 'result'
        st.rerun()
        return
    
    question = questions[current_q]
    
    if st.session_state.quiz_data['question_start_time'] is None:
        st.session_state.quiz_data['question_start_time'] = time.time()
    
    if not st.session_state.quiz_data['shuffled_options'] or len(st.session_state.quiz_data['shuffled_options']) != len(question['options']):
        st.session_state.quiz_data['shuffled_options'] = question['options'].copy()
        random.shuffle(st.session_state.quiz_data['shuffled_options'])
    
    progress = (current_q + 1) / len(questions)
    st.progress(progress)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div class="stats-card">
                <div class="stat-value">{current_q + 1}/{len(questions)}</div>
                <div class="stat-label">Frage</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="stats-card">
                <div class="stat-value">{st.session_state.quiz_data['score']}</div>
                <div class="stat-label">Punkte</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        elapsed = int(time.time() - st.session_state.quiz_data['start_time'])
        st.markdown(f"""
            <div class="stats-card">
                <div class="stat-value">{elapsed}s</div>
                <div class="stat-label">Zeit</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="question-card">
            <div class="question-text">{question['question']}</div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    options = st.session_state.quiz_data['shuffled_options']
    
    for idx, option in enumerate(options):
        col = col1 if idx % 2 == 0 else col2
        with col:
            if st.button(option, key=f"answer_{idx}", use_container_width=True):
                question_time = time.time() - st.session_state.quiz_data['question_start_time']
                is_correct = option == question['answer']
                
                if is_correct:
                    st.session_state.quiz_data['score'] += 1
                
                st.session_state.quiz_data['answers'].append({
                    "question": question['question'],
                    "selected": option,
                    "correct": question['answer'],
                    "is_correct": is_correct,
                    "time": round(question_time, 2)
                })
                
                st.session_state.quiz_data['current_question'] += 1
                st.session_state.quiz_data['question_start_time'] = None
                st.session_state.quiz_data['shuffled_options'] = []
                st.rerun()

def show_result_page():
    total_time = time.time() - st.session_state.quiz_data['start_time']
    total_questions = len(HINDUISMUS_QUIZ['questions'])
    percentage = (st.session_state.quiz_data['score'] / total_questions) * 100
    
    save_result(
        st.session_state.username,
        st.session_state.quiz_data['score'],
        total_questions,
        total_time,
        st.session_state.quiz_data['answers']
    )
    
    st.markdown('<h1 class="main-title">Quiz abgeschlossen! 🎉</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
            <div class="result-card">
                <div class="result-score">{st.session_state.quiz_data['score']}/{total_questions}</div>
                <div class="stat-label" style="font-size: 1.5rem; margin-top: 1rem;">
                    {percentage:.1f}% richtig
                </div>
                <div class="stat-label" style="font-size: 1.2rem; margin-top: 1rem;">
                    ⏱️ Gesamtzeit: {total_time:.1f}s
                </div>
                <div class="stat-label" style="font-size: 1.2rem;">
                    📊 Durchschnitt: {total_time/total_questions:.1f}s pro Frage
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("Nochmal spielen", key="retry_btn", use_container_width=True):
                st.session_state.quiz_data = {
                    'current_question': 0,
                    'score': 0,
                    'answers': [],
                    'start_time': time.time(),
                    'question_start_time': None,
                    'shuffled_options': []
                }
                st.session_state.page = 'quiz'
                st.rerun()
        
        with col2:
            if st.button("Leaderboard ansehen", key="result_leaderboard_btn", use_container_width=True):
                st.session_state.page = 'leaderboard'
                st.rerun()
        
        with col3:
            if st.button("Zurück zur Hauptseite", key="back_home_btn", use_container_width=True):
                st.switch_page("main.py")

def show_leaderboard_page():
    st.markdown('<h1 class="main-title">🏆 Leaderboard</h1>', unsafe_allow_html=True)
    
    leaderboard = get_leaderboard_data()
    
    if leaderboard.empty:
        st.info("Noch keine Ergebnisse vorhanden. Sei der Erste!")
    else:
        for idx, row in leaderboard.head(3).iterrows():
            medal = ["🥇", "🥈", "🥉"][idx] if idx < 3 else "🏅"
            st.markdown(f"""
                <div class="stats-card" style="margin: 1rem 0; padding: 2rem;">
                    <h2 style="font-size: 2rem; margin-bottom: 1rem;">{medal} {row['username']}</h2>
                    <div style="display: flex; justify-content: space-around; flex-wrap: wrap;">
                        <div>
                            <div class="stat-value">{row['score']}</div>
                            <div class="stat-label">Punkte</div>
                        </div>
                        <div>
                            <div class="stat-value">{row['percentage']:.1f}%</div>
                            <div class="stat-label">Richtig</div>
                        </div>
                        <div>
                            <div class="stat-value">{row['time_taken']:.1f}s</div>
                            <div class="stat-label">Gesamtzeit</div>
                        </div>
                        <div>
                            <div class="stat-value">{row['avg_time_per_question']:.1f}s</div>
                            <div class="stat-label">Ø pro Frage</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        if len(leaderboard) > 3:
            st.markdown("### Weitere Spieler")
            for idx, row in leaderboard.iloc[3:].iterrows():
                st.markdown(f"""
                    <div class="stats-card" style="margin: 0.5rem 0;">
                        <strong>{row['username']}</strong> - 
                        {row['score']} Punkte ({row['percentage']:.1f}%) - 
                        {row['time_taken']:.1f}s
                    </div>
                """, unsafe_allow_html=True)
    
    if st.button("Zurück zum Quiz", key="back_quiz_btn", use_container_width=True):
        st.session_state.page = 'start'
        st.rerun()

def main():
    initialize_session_state()
    
    if not st.session_state.username:
        show_unauthorized_page()
        return
    
    status = auth_manager.check_user_status(st.session_state.username)
    if status["should_logout"]:
        st.error(f"🔒 {status['message']}")
        time.sleep(2)
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("main.py")
        return
    
    apply_theme()
    
    if st.session_state.page == 'start':
        show_start_page()
    elif st.session_state.page == 'quiz':
        show_quiz_page()
    elif st.session_state.page == 'result':
        show_result_page()
    elif st.session_state.page == 'leaderboard':
        show_leaderboard_page()

if __name__ == "__main__":
    main()