import json
import os
import hashlib
import re
from typing import Dict, List, Tuple

USERS_FILE = "./data/users.json"
BAD_WORDS_FILE = "./data/bad_words.txt"
ANSWERS_DIR = "./data/answers"
DEFAULT_PASSWORD = "4-26-2011"

# ---------------------- UTILS ----------------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def load_bad_words() -> List[str]:
    if not os.path.exists(BAD_WORDS_FILE):
        os.makedirs(os.path.dirname(BAD_WORDS_FILE), exist_ok=True)
        with open(BAD_WORDS_FILE, "w", encoding="utf-8") as f:
            f.write("arsch\nidiot\ndummy\ndepp\nhurensohn\nnutte\nbitch\nfick\nfuck\n")
    with open(BAD_WORDS_FILE, "r", encoding="utf-8") as f:
        return [word.strip().lower() for word in f.readlines()]

def is_valid_username(username: str) -> bool:
    """
    Überprüft, ob ein Benutzername gültig ist.
    
    Regeln:
    - Länge zwischen 4 und 20 Zeichen
    - Nur Buchstaben, Zahlen, Unterstrich und Bindestrich
    - Keine Schimpfwörter oder anstößige Begriffe
    
    Args:
        username: Der zu prüfende Benutzername
    
    Returns:
        bool: True wenn der Benutzername gültig ist, False sonst
    """
    # Prüfe Länge
    if not username or len(username) < 4 or len(username) > 20:
        return False
        
    # Prüfe erlaubte Zeichen (Buchstaben, Zahlen, Unterstrich, Bindestrich)
    if not all(c.isalnum() or c in '_-' for c in username):
        return False
    
    # Prüfe auf Schimpfwörter
    username_lower = username.lower()
    bad_words = load_bad_words()
    
    # Direkter Vergleich
    if username_lower in bad_words:
        return False
        
    # Teilwort-Vergleich
    for word in bad_words:
        if word.strip() and word.strip() in username_lower:
            return False
            
    return True

def is_valid_password(password: str) -> bool:
    return len(password) >= 6

# ---------------------- USER MANAGEMENT ----------------------
def is_user_active(username: str) -> bool:
    """
    Überprüft, ob ein Benutzer aktiv ist.
    
    Args:
        username: Der zu überprüfende Benutzername
    
    Returns:
        bool: True wenn der Benutzer aktiv ist, False sonst
    """
    users = load_users()
    if username not in users:
        return False
    return users[username].get("active", True)

def load_users() -> Dict:
    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
    # Admin anlegen, falls keiner existiert
    if not any(u.get("is_admin", False) for u in users.values()):
        users["admin"] = {
            "password": hash_password("24Lama6"),
            "is_admin": True,
            "active": True,
            "using_default": False
        }
        save_users(users)
    return users

def save_users(users: Dict) -> None:
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

def authenticate_user(username: str, password: str) -> Tuple[bool, str, bool]:
    """
    Authentifiziert einen Benutzer oder erstellt einen neuen, wenn das Default-Passwort verwendet wird.
    
    Args:
        username: Der Benutzername
        password: Das Passwort
        
    Returns:
        Tuple[bool, str, bool]: (Erfolg, Nachricht, Passwort-Änderung erforderlich)
    """
    users = load_users()

    # Wenn der Benutzer noch nicht existiert
    if username not in users:
        if not is_valid_username(username):
            return False, "Ungültiger Benutzername! (4-20 Zeichen, nur Buchstaben, Zahlen, _ und -)", False
            
        # Neuen Benutzer nur mit Default-Passwort erlauben
        if password == DEFAULT_PASSWORD:
            users[username] = {
                "password": hash_password(password),
                "is_admin": False,
                "active": True,
                "using_default": True  # Markiere, dass Default-Passwort verwendet wird
            }
            save_users(users)
            return True, "Neuer Benutzer erstellt! Bitte ändern Sie Ihr Passwort.", True
        else:
            return False, f"Für neue Benutzer bitte das Standard-Passwort verwenden!", False

    # Prüfe existierenden Benutzer
    user = users[username]

    if not user["active"]:
        return False, "Dieser Account wurde deaktiviert!", False

    if user["password"] == hash_password(password):
        return True, "", user.get("using_default", False)
    elif password == DEFAULT_PASSWORD and not user.get("using_default", False):
        # Erlaube Login mit Default-Passwort und markiere für Änderung
        user["password"] = hash_password(password)
        user["using_default"] = True
        save_users(users)
        return True, "Bitte ändern Sie Ihr Passwort.", True

    return False, "Falsches Passwort!", False

def get_active_users() -> List[str]:
    users = load_users()
    return [u for u, data in users.items() if data["active"]]

def deactivate_user(admin_username: str, username: str) -> Tuple[bool, str]:
    users = load_users()
    if admin_username not in users or not users[admin_username].get("is_admin", False):
        return False, "Nur Admins können Benutzer deaktivieren"
    if username not in users:
        return False, f"Benutzer {username} nicht gefunden"
    if users[username].get("is_admin", False):
        return False, "Admin kann nicht deaktiviert werden"
    if not users[username]["active"]:
        return False, "Benutzer bereits deaktiviert"
    users[username]["active"] = False
    save_users(users)
    try:
        with open(BAD_WORDS_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n{username.lower()}")
    except Exception as e:
        return False, f"Fehler beim Aktualisieren der Blacklist: {str(e)}"
    return True, "Benutzer deaktiviert"

def change_password(username: str, old_password: str, new_password: str) -> Tuple[bool, str]:
    if not is_valid_password(new_password):
        return False, "Neues Passwort muss mindestens 6 Zeichen haben"
    users = load_users()
    if username not in users:
        return False, "Benutzer nicht gefunden"
    user = users[username]
    if not user["active"]:
        return False, "Account deaktiviert"
    if user["password"] != hash_password(old_password):
        return False, "Altes Passwort falsch"
    users[username]["password"] = hash_password(new_password)
    users[username]["using_default"] = False
    save_users(users)
    return True, "Passwort geändert"

# ---------------------- ANSWERS ----------------------
def load_answers() -> list:
    os.makedirs(ANSWERS_DIR, exist_ok=True)
    answers = []
    for f_name in os.listdir(ANSWERS_DIR):
        if f_name.endswith(".json"):
            with open(os.path.join(ANSWERS_DIR, f_name), "r", encoding="utf-8") as f:
                answers.append(json.load(f))
    return answers

def save_answer(answer: dict):
    os.makedirs(ANSWERS_DIR, exist_ok=True)
    username = answer.get("username", "unknown")
    with open(os.path.join(ANSWERS_DIR, f"{username}.json"), "w", encoding="utf-8") as f:
        json.dump(answer, f, indent=2)
