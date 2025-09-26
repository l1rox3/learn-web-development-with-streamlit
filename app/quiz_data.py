# app/quiz_data.py

QUIZZES = {
    "Kleidung": {
        "id": "kleidung",
        "questions": {
            "kleidung1": {
                "frage": "Welches Kleidungsstück ist bei hinduistischen Frauen weit verbreitet?",
                "optionen": ["Sari", "Kimono", "Dirndl", "Kaftan"],
                "richtig": "Sari"
            },
            "kleidung2": {
                "frage": "Welche Farbe wird traditionell bei hinduistischen Hochzeiten getragen?",
                "optionen": ["Schwarz", "Weiß", "Rot", "Blau"],
                "richtig": "Rot"
            }
        }
    },
    "Heilige Tiere": {
        "id": "tiere",
        "questions": {
            "tier1": {
                "frage": "Welches Tier wird als Reittier (Vahana) von Lord Shiva betrachtet?",
                "optionen": ["Elefant", "Stier Nandi", "Pfau", "Löwe"],
                "richtig": "Stier Nandi"
            },
            "tier2": {
                "frage": "Welches Tier wird mit Lord Ganesha in Verbindung gebracht?",
                "optionen": ["Maus", "Schlange", "Affe", "Tiger"],
                "richtig": "Maus"
            },
            "tier3": {
                "frage": "Welches Tier gilt als heilig und wird als 'Mutter' verehrt?",
                "optionen": ["Schaf", "Kuh", "Ziege", "Pferd"],
                "richtig": "Kuh"
            }
        }
    }
}

# Kombiniere Fragen für den Kombiniert-Quiz
QUIZZES["Kombiniert"] = {
    "id": "kombiniert",
    "questions": {
        **QUIZZES["Kleidung"]["questions"],
        **QUIZZES["Heilige Tiere"]["questions"]
    }
}