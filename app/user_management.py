import json
import os
import hashlib
import re
from typing import Dict, List, Optional

USERS_FILE = "./data/users.json"
BAD_WORDS_FILE = "./data/bad_words.txt"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "24Lama6"
DEFAULT_PASSWORD = "4-26-2011"

def hash_password(password: str) -> str:
    """Erstellt einen sicheren Hash des Passworts."""
    return hashlib.sha256(password.encode()).hexdigest()

def load_bad_words() -> List[str]:
    """Lädt die Liste der verbotenen Wörter."""
    if not os.path.exists(BAD_WORDS_FILE):
        with open(BAD_WORDS_FILE, "w") as f:
            f.write("arsch\nidiot\ndummy\ndepp\nhurensohn\nnutte\nbitch\nfick\nfuck\n")  # Beispiel-Liste
    with open(BAD_WORDS_FILE, "r", encoding="utf-8") as f:
        return [word.strip().lower() for word in f.readlines()]

def is_valid_username(username: str) -> bool:
    """Überprüft, ob der Benutzername gültig ist."""
    if not (4 <= len(username) <= 20):
        return False
    
    if not re.match("^[a-zA-Z0-9_-]+$", username):
        return False
        
    bad_words = load_bad_words()
    username_lower = username.lower()
    # Direkter Treffer
    if username_lower in bad_words:
        return False
    # Fuzzy-Match: Erlaube beliebige Zeichen zwischen den Buchstaben
    for word in bad_words:
        # Erzeuge Regex wie h.*u.*r.*e.*n.*s.*o.*h.*n
        pattern = ".*".join(map(re.escape, word))
        if re.search(pattern, username_lower):
            return False
    return True

def is_valid_password(password: str) -> bool:
    """Überprüft, ob das Passwort den Anforderungen entspricht."""
    if len(password) < 6:
        return False
    return True

def load_users() -> Dict:
    """Lädt die Benutzerdaten aus der JSON-Datei."""
    users = {}
    
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
    
    # Stelle sicher, dass der Admin-Account immer existiert
    if ADMIN_USERNAME not in users:
        users[ADMIN_USERNAME] = {
            "password": hash_password(ADMIN_PASSWORD),
            "is_admin": True,
            "active": True,
            "using_default": False
        }
        save_users(users)
    
    return users

def save_users(users: Dict) -> None:
    """Speichert die Benutzerdaten in der JSON-Datei."""
    dir_name = os.path.dirname(USERS_FILE)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

def authenticate_user(username: str, password: str) -> tuple[bool, str, bool]:
    """Authentifiziert einen Benutzer.
    Returns:
        tuple: (success, message, needs_password_change)
    """
    users = load_users()
    
    # Spezialfall: Admin-Login
    if username == ADMIN_USERNAME:
        if password == ADMIN_PASSWORD:
            return True, "", False
        return False, "Falsches Admin-Passwort.", False
    
    if username not in users:
        # Neuer Benutzer
        if not is_valid_username(username):
            return False, "Ungültiger Benutzername. Nur Buchstaben, Zahlen, - und _ erlaubt (4-20 Zeichen).", False
        
        if not is_valid_password(password):
            return False, "Passwort muss mindestens 6 Zeichen lang sein.", False
            
        users[username] = {
            "password": hash_password(password),
            "is_admin": False,
            "active": True,
            "using_default": False
        }
        save_users(users)
        return True, "Neuer Benutzer erstellt!", False
    
    # Existierender Benutzer
    user = users[username]
    if not user["active"]:
        return False, "Dieser Account wurde deaktiviert.", False
        
    if user["password"] == hash_password(password):
        return True, "", user.get("using_default", False)
    elif password == DEFAULT_PASSWORD:
        users[username]["password"] = hash_password(password)
        users[username]["using_default"] = True
        save_users(users)
        return True, "", True
    
    return False, "Falsches Passwort.", False

def get_active_users() -> List[str]:
    """Gibt eine Liste aller aktiven Benutzer zurück."""
    users = load_users()
    return [username for username, data in users.items() if data["active"]]

def deactivate_user(admin_password: str, username: str) -> tuple[bool, str]:
    """Deaktiviert einen Benutzer und fügt ihn zur Blacklist hinzu (nur für Admin)."""
    users = load_users()
    
    # Überprüfe, ob das Admin-Passwort stimmt
    if not admin_password:
        return False, "Admin-Passwort ist leer"
        
    if admin_password != ADMIN_PASSWORD:
        return False, "Falsches Admin-Passwort"
        
    if username not in users:
        return False, f"Benutzer {username} nicht gefunden"
        
    if users[username]["is_admin"]:
        return False, "Admin-Benutzer kann nicht deaktiviert werden"
        
    if not users[username]["active"]:
        return False, f"Benutzer {username} ist bereits deaktiviert"
    
    # Benutzer deaktivieren
    users[username]["active"] = False
    save_users(users)
    
    # Füge Benutzername zur Blacklist hinzu
    try:
        with open(BAD_WORDS_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n{username.lower()}")
    except Exception as e:
        return False, f"Fehler beim Aktualisieren der Blacklist: {str(e)}"
    
    return True, "Benutzer erfolgreich deaktiviert"

def change_password(username: str, old_password: str, new_password: str) -> tuple[bool, str]:
    """Ändert das Passwort eines Benutzers."""
    if not is_valid_password(new_password):
        return False, "Neues Passwort muss mindestens 6 Zeichen lang sein."
        
    users = load_users()
    if username not in users:
        return False, "Benutzer nicht gefunden."
        
    user = users[username]
    if not user["active"]:
        return False, "Dieser Account wurde deaktiviert."
        
    if user["password"] != hash_password(old_password):
        return False, "Altes Passwort ist falsch."
        
    users[username]["password"] = hash_password(new_password)
    users[username]["using_default"] = False
    save_users(users)
    return True, "Passwort erfolgreich geändert."