import json
import os
import hashlib
import re
import secrets
import subprocess
import sys
from typing import Tuple, Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

# ---------------------- KONSTANTEN ----------------------
USERS_FILE = "./data/users.json"
BAD_WORDS_FILE = "./data/bad_words.txt"
ANSWERS_DIR = "./data/answers"
DEFAULT_PASSWORD = "4-26-2011"

# ---------------------- ENUMS ----------------------
class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"

class LoginResult(Enum):
    SUCCESS = "success"
    INVALID_CREDENTIALS = "invalid_credentials"
    ACCOUNT_DISABLED = "account_disabled"
    PASSWORD_CHANGE_REQUIRED = "password_change_required"
    ACCOUNT_LOCKED = "account_locked"
    INVALID_USERNAME = "invalid_username"

# ---------------------- DATACLASSES ----------------------
@dataclass
class User:
    username: str
    password_hash: str
    role: UserRole
    active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    using_default: bool = False
    failed_attempts: int = 0
    locked_until: Optional[datetime] = None
    email: Optional[str] = None
    salt: str = ""

# ---------------------- AUTH MANAGER ----------------------
class AuthManager:
    """Schlankes Login-System mit Passwort-Hashing, Account-Lockout etc."""

    def __init__(self):
        self.session_timeout = timedelta(hours=24)
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=30)
        self._ensure_directories()

    def _ensure_directories(self):
        """Erstellt notwendige Verzeichnisse"""
        for directory in [os.path.dirname(USERS_FILE), ANSWERS_DIR]:
            if directory:
                os.makedirs(directory, exist_ok=True)

    # ---------------------- Passwort ----------------------
    def hash_password(self, password: str, salt: str = None) -> Tuple[str, str]:
        """Erstellt sicheren Hash mit Salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256', password.encode(), salt.encode(), 100_000
        )
        return password_hash.hex(), salt

    def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """Verifiziert Passwort gegen gespeicherten Hash"""
        if not salt:
            # Alte Hashes ohne Salt (Migration)
            old_hash = hashlib.sha256(password.encode()).hexdigest()
            return old_hash == stored_hash
        password_hash, _ = self.hash_password(password, salt)
        return password_hash == stored_hash

    # ---------------------- Benutzername & Passwort Validierung ----------------------
    def load_bad_words(self) -> List[str]:
        """Lädt die Liste verbotener Wörter aus bad_words.txt"""
        if not os.path.exists(BAD_WORDS_FILE):
            # Erstelle Standard bad_words.txt falls nicht vorhanden
            default_words = "arsch\nidiot\ndummy\ndepp\nhurensohn\nnutte\nbitch\nfick\nfuck\n"
            with open(BAD_WORDS_FILE, "w", encoding="utf-8") as f:
                f.write(default_words)
        
        try:
            with open(BAD_WORDS_FILE, "r", encoding="utf-8") as f:
                return [word.strip().lower() for word in f.readlines() if word.strip()]
        except Exception:
            return []

    def is_valid_username(self, username: str) -> Tuple[bool, str]:
        """
        Überprüft ob Benutzername gültig ist.
        Prüft: Länge, Zeichen, verbotene Wörter aus bad_words.txt
        """
        if not username:
            return False, "Benutzername darf nicht leer sein"
        
        if len(username) < 4:
            return False, "Benutzername muss mindestens 4 Zeichen haben"
        
        if len(username) > 20:
            return False, "Benutzername darf maximal 20 Zeichen haben"
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, "Benutzername darf nur Buchstaben, Zahlen, _ und - enthalten"
        
        # WICHTIG: Überprüfung auf verbotene Wörter
        username_lower = username.lower()
        bad_words = self.load_bad_words()
        
        for word in bad_words:
            if word in username_lower:
                return False, f"Benutzername enthält nicht erlaubte Begriffe"
        
        return True, ""

    def is_valid_password(self, password: str) -> Tuple[bool, str]:
        """Überprüft ob Passwort gültig ist"""
        if password == DEFAULT_PASSWORD:
            return True, ""
        
        if len(password) < 6:
            return False, "Passwort muss mindestens 6 Zeichen haben"
        
        return True, ""

    # ---------------------- User Management ----------------------
    def load_users(self) -> Dict[str, User]:
        """Lädt alle Benutzer aus users.json"""
        users = {}
        
        if os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                for username, user_data in data.items():
                    users[username] = User(
                        username=username,
                        password_hash=user_data.get("password", ""),
                        role=UserRole.ADMIN if user_data.get("is_admin", False) else UserRole.USER,
                        active=user_data.get("active", True),
                        created_at=datetime.fromisoformat(user_data.get("created_at", datetime.now().isoformat())),
                        last_login=datetime.fromisoformat(user_data["last_login"]) if user_data.get("last_login") else None,
                        using_default=user_data.get("using_default", False),
                        failed_attempts=user_data.get("failed_attempts", 0),
                        locked_until=datetime.fromisoformat(user_data["locked_until"]) if user_data.get("locked_until") else None,
                        email=user_data.get("email"),
                        salt=user_data.get("salt", "")
                    )
            except Exception as e:
                print(f"Fehler beim Laden der Benutzer: {e}")
                users = {}
        
        # Admin-Fallback: Erstelle Admin-Account falls keiner existiert
        if not any(user.role == UserRole.ADMIN for user in users.values()):
            admin_hash, admin_salt = self.hash_password("24Lama6")
            users["admin"] = User(
                username="admin",
                password_hash=admin_hash,
                role=UserRole.ADMIN,
                active=True,
                created_at=datetime.now(),
                salt=admin_salt
            )
            self.save_users(users)
        
        return users

    def save_users(self, users: Dict[str, User]):
        """Speichert alle Benutzer in users.json"""
        data = {}
        
        for username, user in users.items():
            data[username] = {
                "password": user.password_hash,
                "is_admin": user.role == UserRole.ADMIN,
                "active": user.active,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "using_default": user.using_default,
                "failed_attempts": user.failed_attempts,
                "locked_until": user.locked_until.isoformat() if user.locked_until else None,
                "email": user.email,
                "salt": user.salt
            }
        
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ---------------------- Account Lock ----------------------
    def is_account_locked(self, user: User) -> bool:
        """Prüft ob Account gesperrt ist"""
        if user.locked_until and datetime.now() < user.locked_until:
            return True
        elif user.locked_until and datetime.now() >= user.locked_until:
            # Sperre ist abgelaufen - zurücksetzen
            user.failed_attempts = 0
            user.locked_until = None
        return False

    def lock_account(self, user: User):
        """Erhöht Fehlversuche und sperrt Account bei zu vielen Versuchen"""
        user.failed_attempts += 1
        if user.failed_attempts >= self.max_failed_attempts:
            user.locked_until = datetime.now() + self.lockout_duration

    # ---------------------- Auth ----------------------
    def authenticate_user(self, username: str, password: str) -> Tuple[LoginResult, str, Optional[UserRole]]:
        """
        Authentifiziert einen Benutzer.
        Erstellt neue Benutzer automatisch mit Standard-Passwort.
        Überprüft verbotene Wörter bei neuen Benutzern.
        """
        users = self.load_users()

        # ========== NEUER BENUTZER ==========
        if username not in users:
            # SCHRITT 1: Benutzername validieren (inkl. bad_words Check!)
            is_valid, error_msg = self.is_valid_username(username)
            if not is_valid:
                return LoginResult.INVALID_USERNAME, error_msg, None
            
            # SCHRITT 2: Nur mit Standard-Passwort können neue Benutzer angelegt werden
            if password == DEFAULT_PASSWORD:
                # Passwort hashen mit Salt
                password_hash, salt = self.hash_password(password)
                
                # Neuen Benutzer erstellen
                new_user = User(
                    username=username,
                    password_hash=password_hash,
                    role=UserRole.USER,
                    active=True,
                    created_at=datetime.now(),
                    using_default=True,
                    salt=salt
                )
                
                # Benutzer zum Dictionary hinzufügen
                users[username] = new_user
                
                # WICHTIG: Speichern in users.json
                self.save_users(users)
                
                return LoginResult.PASSWORD_CHANGE_REQUIRED, "Neuer Benutzer erstellt! Bitte ändern Sie Ihr Passwort.", UserRole.USER
            else:
                return LoginResult.INVALID_CREDENTIALS, "Für neue Benutzer bitte das Standard-Passwort verwenden!", None

        # ========== EXISTIERENDER BENUTZER ==========
        user = users[username]
        
        # Account deaktiviert?
        if not user.active:
            return LoginResult.ACCOUNT_DISABLED, "Dieser Account wurde deaktiviert!", None
        
        # Account gesperrt?
        if self.is_account_locked(user):
            remaining_time = user.locked_until - datetime.now()
            minutes = int(remaining_time.total_seconds() / 60)
            return LoginResult.ACCOUNT_LOCKED, f"Account ist für {minutes} Minuten gesperrt!", None

        # Passwort überprüfen
        password_valid = self.verify_password(password, user.password_hash, user.salt)
        
        # Migration alter Hashes ohne Salt
        if not password_valid and not user.salt:
            old_hash = hashlib.sha256(password.encode()).hexdigest()
            if user.password_hash == old_hash:
                password_valid = True
                # Migriere zu neuem Hash mit Salt
                new_hash, new_salt = self.hash_password(password)
                user.password_hash = new_hash
                user.salt = new_salt

        # Default Passwort Handling für existierende User
        if not password_valid and password == DEFAULT_PASSWORD and not user.using_default:
            password_hash, salt = self.hash_password(password)
            user.password_hash = password_hash
            user.salt = salt
            user.using_default = True
            password_valid = True

        # ========== LOGIN ERFOLGREICH ==========
        if password_valid:
            user.last_login = datetime.now()
            user.failed_attempts = 0
            user.locked_until = None
            self.save_users(users)
            
            if user.using_default:
                return LoginResult.PASSWORD_CHANGE_REQUIRED, "Bitte ändern Sie Ihr Passwort.", user.role
            else:
                msg = f"Willkommen zurück, {username}!"
                if user.role == UserRole.ADMIN:
                    msg = f"Willkommen im Admin-Panel, {username}!"
                return LoginResult.SUCCESS, msg, user.role
        
        # ========== LOGIN FEHLGESCHLAGEN ==========
        else:
            self.lock_account(user)
            self.save_users(users)
            return LoginResult.INVALID_CREDENTIALS, "Ungültige Anmeldedaten!", None

    # ---------------------- Passwort ändern ----------------------
    def change_password(self, username: str, old_password: str, new_password: str) -> Tuple[bool, str]:
        """Ändert das Passwort eines Benutzers"""
        # Neues Passwort validieren
        is_valid, err = self.is_valid_password(new_password)
        if not is_valid:
            return False, err
        
        users = self.load_users()
        
        if username not in users:
            return False, "Benutzer nicht gefunden"
        
        user = users[username]
        
        if not user.active:
            return False, "Account deaktiviert"
        
        # Altes Passwort prüfen (außer bei Default-Passwort)
        if not user.using_default:
            if not self.verify_password(old_password, user.password_hash, user.salt):
                return False, "Altes Passwort falsch"
        
        # Neues Passwort setzen
        new_hash, new_salt = self.hash_password(new_password)
        user.password_hash = new_hash
        user.salt = new_salt
        user.using_default = False
        
        users[username] = user
        self.save_users(users)
        
        return True, "Passwort erfolgreich geändert"

# ---------------------- ANSWERS ----------------------
def load_answers() -> list:
    """Lädt alle gespeicherten Antworten"""
    os.makedirs(ANSWERS_DIR, exist_ok=True)
    answers = []
    
    try:
        for f_name in os.listdir(ANSWERS_DIR):
            if f_name.endswith(".json"):
                with open(os.path.join(ANSWERS_DIR, f_name), "r", encoding="utf-8") as f:
                    answers.append(json.load(f))
    except Exception as e:
        print(f"Fehler beim Laden der Antworten: {e}")
    
    return answers

def save_answer(answer: dict):
    """Speichert eine Antwort"""
    os.makedirs(ANSWERS_DIR, exist_ok=True)
    username = answer.get("username", "unknown")
    
    try:
        with open(os.path.join(ANSWERS_DIR, f"{username}.json"), "w", encoding="utf-8") as f:
            json.dump(answer, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Fehler beim Speichern der Antwort: {e}")

# ---------------------- LEGACY WRAPPER ----------------------
# Für Kompatibilität mit altem Code
_auth_manager = AuthManager()

def load_users() -> dict:
    """Legacy-Funktion: Lädt Benutzer als Dictionary"""
    users = _auth_manager.load_users()
    legacy_users = {}
    
    for username, user in users.items():
        legacy_users[username] = {
            "password": user.password_hash,
            "is_admin": user.role == UserRole.ADMIN,
            "active": user.active,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "using_default": user.using_default,
            "failed_attempts": user.failed_attempts,
            "locked_until": user.locked_until.isoformat() if user.locked_until else None,
            "email": user.email,
            "salt": user.salt
        }
    
    return legacy_users

def save_users(users: dict):
    """Legacy-Funktion: Speichert Benutzer aus Dictionary"""
    new_users = {}
    
    for username, user_data in users.items():
        new_users[username] = User(
            username=username,
            password_hash=user_data.get("password", ""),
            role=UserRole.ADMIN if user_data.get("is_admin", False) else UserRole.USER,
            active=user_data.get("active", True),
            created_at=datetime.fromisoformat(user_data.get("created_at", datetime.now().isoformat())),
            last_login=datetime.fromisoformat(user_data["last_login"]) if user_data.get("last_login") else None,
            using_default=user_data.get("using_default", False),
            failed_attempts=user_data.get("failed_attempts", 0),
            locked_until=datetime.fromisoformat(user_data["locked_until"]) if user_data.get("locked_until") else None,
            email=user_data.get("email"),
            salt=user_data.get("salt", "")
        )
    
    _auth_manager.save_users(new_users)

def authenticate_user(username: str, password: str) -> tuple:
    """Legacy-Funktion: Authentifiziert Benutzer"""
    result, message, role = _auth_manager.authenticate_user(username, password)
    
    # WICHTIG: Bei INVALID_USERNAME soll success=False sein
    if result == LoginResult.INVALID_USERNAME:
        return False, message, False
    
    success = result in [LoginResult.SUCCESS, LoginResult.PASSWORD_CHANGE_REQUIRED]
    password_change_required = result == LoginResult.PASSWORD_CHANGE_REQUIRED
    return success, message, password_change_required

def hash_password(password: str) -> tuple:
    """Legacy-Funktion: Hasht Passwort"""
    return _auth_manager.hash_password(password)