import json
import os
import hashlib
import re
import secrets
import subprocess
import sys
import secrets, hashlib
from typing import Tuple
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


# Pfade und Konstanten
USERS_FILE = "./data/users.json"
BAD_WORDS_FILE = "./data/bad_words.txt"
ANSWERS_DIR = "./data/answers"
SESSIONS_FILE = "./data/sessions.json"
DEFAULT_PASSWORD = "4-26-2011"

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

class AuthManager:
    """Schlankes Login-System für direkte Ausführung"""
    
    def __init__(self):
        self.session_timeout = timedelta(hours=24)
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=30)
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Stellt sicher, dass alle benötigten Verzeichnisse existieren"""
        for directory in [os.path.dirname(USERS_FILE), 
                         os.path.dirname(SESSIONS_FILE), 
                         ANSWERS_DIR]:
            if directory:
                os.makedirs(directory, exist_ok=True)
    
    # ---------------------- UTILS ----------------------
    def hash_password(self, password: str, salt: str = None) -> Tuple[str, str]:
    """Erstellt einen sicheren Hash mit Salt"""
    if salt is None:
        salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        'sha256', password.encode(), salt.encode(), 100_000
    )
    return password_hash.hex(), salt


    def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """Verifiziert ein Passwort gegen den gespeicherten Hash"""
        if not salt:
            # Fallback für alte Hash-Methode
            old_hash = hashlib.sha256(password.encode()).hexdigest()
            return old_hash == stored_hash
        
        password_hash, _ = self.hash_password(password, salt)
        return password_hash == stored_hash

    def load_bad_words(self) -> List[str]:
        """Lädt die Liste der verbotenen Wörter"""
        if not os.path.exists(BAD_WORDS_FILE):
            default_words = "arsch\nidiot\ndummy\ndepp\nhurensohn\nnutte\nbitch\nfick\nfuck\n"
            with open(BAD_WORDS_FILE, "w", encoding="utf-8") as f:
                f.write(default_words)
        
        try:
            with open(BAD_WORDS_FILE, "r", encoding="utf-8") as f:
                return [word.strip().lower() for word in f.readlines() if word.strip()]
        except Exception:
            return []

    def is_valid_username(self, username: str) -> Tuple[bool, str]:
        """Erweiterte Benutzername-Validierung"""
        if not username:
            return False, "Benutzername darf nicht leer sein"
            
        if len(username) < 4:
            return False, "Benutzername muss mindestens 4 Zeichen haben"
            
        if len(username) > 20:
            return False, "Benutzername darf maximal 20 Zeichen haben"
            
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, "Benutzername darf nur Buchstaben, Zahlen, _ und - enthalten"
        
        # Prüfe auf verbotene Wörter
        username_lower = username.lower()
        bad_words = self.load_bad_words()
        
        for word in bad_words:
            if word and word in username_lower:
                return False, "Benutzername enthält nicht erlaubte Begriffe"
                
        return True, ""

    def is_valid_password(self, password: str) -> Tuple[bool, str]:
        """Passwort-Validierung"""
        if password == DEFAULT_PASSWORD:
            return True, ""  # Default-Passwort ist temporär erlaubt
            
        if len(password) < 6:
            return False, "Passwort muss mindestens 6 zeichen haben"
            
        return True, ""

    # ---------------------- USER MANAGEMENT ----------------------
    def load_users(self) -> Dict[str, User]:
        """Lädt Benutzer aus der JSON-Datei"""
        users = {}
        
        if os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                for username, user_data in data.items():
                    try:
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
                    except (ValueError, KeyError):
                        continue
                        
            except (json.JSONDecodeError, FileNotFoundError):
                users = {}
        
        # Admin anlegen, falls keiner existiert
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

    def save_users(self, users: Dict[str, User]) -> None:
        """Speichert Benutzer in die JSON-Datei"""
        try:
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
        except Exception as e:
            print(f"Fehler beim Speichern der Benutzer: {e}")

    def is_account_locked(self, user: User) -> bool:
        """Prüft, ob ein Account gesperrt ist"""
        if user.locked_until and datetime.now() < user.locked_until:
            return True
        elif user.locked_until and datetime.now() >= user.locked_until:
            # Sperre ist abgelaufen, zurücksetzen
            user.failed_attempts = 0
            user.locked_until = None
        return False

    def lock_account(self, user: User) -> None:
        """Sperrt einen Account nach zu vielen fehlgeschlagenen Versuchen"""
        user.failed_attempts += 1
        if user.failed_attempts >= self.max_failed_attempts:
            user.locked_until = datetime.now() + self.lockout_duration

    def authenticate_user(self, username: str, password: str) -> Tuple[LoginResult, str, Optional[UserRole]]:
        """Benutzer-Authentifizierung"""
        users = self.load_users()

        # Neuer Benutzer
        if username not in users:
            is_valid, error_msg = self.is_valid_username(username)
            if not is_valid:
                return LoginResult.INVALID_USERNAME, error_msg, None
                
            if password == DEFAULT_PASSWORD:
                password_hash, salt = self.hash_password(password)
                users[username] = User(
                    username=username,
                    password_hash=password_hash,
                    role=UserRole.USER,
                    active=True,
                    created_at=datetime.now(),
                    using_default=True,
                    salt=salt
                )
                self.save_users(users)
                return LoginResult.PASSWORD_CHANGE_REQUIRED, "Neuer Benutzer erstellt! Bitte ändern Sie Ihr Passwort.", UserRole.USER
            else:
                return LoginResult.INVALID_CREDENTIALS, "Für neue Benutzer bitte das Standard-Passwort verwenden!", None

        user = users[username]

        # Account-Status prüfen
        if not user.active:
            return LoginResult.ACCOUNT_DISABLED, "Dieser Account wurde deaktiviert!", None

        if self.is_account_locked(user):
            remaining_time = user.locked_until - datetime.now()
            minutes = int(remaining_time.total_seconds() / 60)
            return LoginResult.ACCOUNT_LOCKED, f"Account ist für {minutes} Minuten gesperrt!", None

        # Passwort prüfen
        password_valid = self.verify_password(password, user.password_hash, user.salt)
        
        # Migration für alte Hashes ohne Salt
        if not password_valid and not user.salt:
            old_hash = hashlib.sha256(password.encode()).hexdigest()
            if user.password_hash == old_hash:
                password_valid = True
                # Migriere zu neuer Hash-Methode
                new_hash, new_salt = self.hash_password(password)
                user.password_hash = new_hash
                user.salt = new_salt

        # Default-Passwort-Behandlung
        if not password_valid and password == DEFAULT_PASSWORD and not user.using_default:
            password_hash, salt = self.hash_password(password)
            user.password_hash = password_hash
            user.using_default = True
            user.salt = salt
            password_valid = True

        if password_valid:
            # Erfolgreiche Anmeldung
            user.last_login = datetime.now()
            user.failed_attempts = 0
            user.locked_until = None
            self.save_users(users)
            
            if user.using_default:
                return LoginResult.PASSWORD_CHANGE_REQUIRED, "Bitte ändern Sie Ihr Passwort.", user.role
            else:
                message = f"Willkommen zurück, {username}!"
                if user.role == UserRole.ADMIN:
                    message = f"Willkommen im Admin-Panel, {username}!"
                return LoginResult.SUCCESS, message, user.role
        else:
            # Fehlgeschlagene Anmeldung
            self.lock_account(user)
            self.save_users(users)
            return LoginResult.INVALID_CREDENTIALS, "Ungültige Anmeldedaten!", None

    def change_password(self, username: str, old_password: str, new_password: str) -> Tuple[bool, str]:
        """Ändert das Passwort eines Benutzers"""
        is_valid, error_msg = self.is_valid_password(new_password)
        if not is_valid:
            return False, error_msg
            
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
        user.using_default = False
        user.salt = new_salt
        
        users[username] = user
        self.save_users(users)
        
        return True, "Passwort erfolgreich geändert"

# ---------------------- COMMAND LINE LOGIN ----------------------
def console_login():
    """Einfache Konsolen-basierte Anmeldung"""
    auth = AuthManager()
    
    print("=" * 50)
    print("🔐 LOGIN SYSTEM")
    print("=" * 50)
    print(f"💡 Neue Benutzer verwenden: {DEFAULT_PASSWORD}")
    print("-" * 50)
    
    max_attempts = 3
    attempts = 0
    
    while attempts < max_attempts:
        try:
            username = input("Benutzername: ").strip()
            if not username:
                print("❌ Benutzername darf nicht leer sein!")
                continue
                
            # Passwort sicher eingeben
            import getpass
            password = getpass.getpass("Passwort: ")
            
            if not password:
                print("❌ Passwort darf nicht leer sein!")
                continue
            
            print("\n🔍 Anmeldung wird überprüft...")
            
            result, message, role = auth.authenticate_user(username, password)
            
            print(f"\n{message}")
            
            if result == LoginResult.SUCCESS:
                print("✅ Anmeldung erfolgreich!")
                
                if role == UserRole.ADMIN:
                    print("\n🛠️ Admin-Rechte erkannt - Starte Admin-Panel...")
                    try:
                        # Führe admin.py aus
                        subprocess.run([sys.executable, "admin.py"], check=True)
                    except FileNotFoundError:
                        print("❌ admin.py nicht gefunden!")
                        print("💡 Stelle sicher, dass admin.py im selben Verzeichnis liegt.")
                    except subprocess.CalledProcessError as e:
                        print(f"❌ Fehler beim Starten von admin.py: {e}")
                    except KeyboardInterrupt:
                        print("\n👋 Admin-Panel beendet.")
                else:
                    print("\n👤 Standard-Benutzer angemeldet.")
                    print("💡 Keine Admin-Rechte - Admin-Panel nicht verfügbar.")
                
                break
                
            elif result == LoginResult.PASSWORD_CHANGE_REQUIRED:
                print("🔑 Passwort-Änderung erforderlich!")
                
                while True:
                    try:
                        if username in auth.load_users() and auth.load_users()[username].using_default:
                            old_password = DEFAULT_PASSWORD
                            print(f"Aktuelles Passwort: {DEFAULT_PASSWORD} (Standard)")
                        else:
                            old_password = getpass.getpass("Aktuelles Passwort: ")
                        
                        new_password = getpass.getpass("Neues Passwort (min. 8 Zeichen): ")
                        confirm_password = getpass.getpass("Neues Passwort bestätigen: ")
                        
                        if new_password != confirm_password:
                            print("❌ Passwörter stimmen nicht überein!")
                            continue
                        
                        success, msg = auth.change_password(username, old_password, new_password)
                        
                        if success:
                            print(f"✅ {msg}")
                            print("🔄 Bitte melden Sie sich erneut an...")
                            break
                        else:
                            print(f"❌ {msg}")
                            
                    except KeyboardInterrupt:
                        print("\n❌ Passwort-Änderung abgebrochen.")
                        return
                        
            else:
                attempts += 1
                remaining = max_attempts - attempts
                if remaining > 0:
                    print(f"⚠️ Noch {remaining} Versuche übrig.")
                print()
                
        except KeyboardInterrupt:
            print("\n\n👋 Anmeldung abgebrochen.")
            return
        except Exception as e:
            print(f"❌ Unerwarteter Fehler: {e}")
            return
    
    if attempts >= max_attempts:
        print("❌ Zu viele fehlgeschlagene Anmeldeversuche!")
        print("🔒 Bitte versuchen Sie es später erneut.")

# ---------------------- LEGACY COMPATIBILITY ----------------------
def load_users() -> Dict:
    """Legacy-Funktion für Kompatibilität"""
    auth_manager = AuthManager()
    users = auth_manager.load_users()
    
    # Konvertiere zu altem Format
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

def save_users(users: Dict) -> None:
    """Legacy-Funktion für Kompatibilität"""
    auth_manager = AuthManager()
    
    # Konvertiere von altem Format
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
    
    auth_manager.save_users(new_users)

def authenticate_user(username: str, password: str) -> Tuple[bool, str, bool]:
    """Legacy-Funktion für Kompatibilität"""
    auth_manager = AuthManager()
    result, message, role = auth_manager.authenticate_user(username, password)
    
    success = result in [LoginResult.SUCCESS, LoginResult.PASSWORD_CHANGE_REQUIRED]
    password_change_required = result == LoginResult.PASSWORD_CHANGE_REQUIRED
    
    return success, message, password_change_required

# ---------------------- ANSWERS (unverändert) ----------------------
def load_answers() -> list:
    """Lädt Antworten aus dem answers-Verzeichnis"""
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

# ---------------------- MAIN ENTRY POINT ----------------------
if __name__ == "__main__":
    console_login()