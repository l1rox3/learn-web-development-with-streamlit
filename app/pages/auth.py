import os
import json
import hashlib
import secrets
from enum import Enum
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, Dict, Tuple, List

# ---------------------- KONSTANTEN ----------------------
USERS_FILE = "./data/users.json"
BAD_WORDS_FILE = "./data/bad_words.txt"
DEFAULT_PASSWORD = "4-26-2011"
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=30)

# ---------------------- ENUMS ----------------------
class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"

# ---------------------- DATACLASS ----------------------
@dataclass
class User:
    username: str
    password_hash: str
    role: UserRole
    active: bool = True
    created_at: datetime = None
    last_login: Optional[datetime] = None
    using_default: bool = True
    salt: str = ""
    failed_attempts: int = 0
    locked_until: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def is_locked(self) -> bool:
        """Prüft ob der Account gesperrt ist"""
        if self.locked_until is None:
            return False
        if datetime.now() >= self.locked_until:
            # Sperre ist abgelaufen
            self.locked_until = None
            self.failed_attempts = 0
            return False
        return True
    
    def get_lockout_remaining(self) -> Optional[timedelta]:
        """Gibt verbleibende Sperrzeit zurück"""
        if self.locked_until is None:
            return None
        remaining = self.locked_until - datetime.now()
        return remaining if remaining.total_seconds() > 0 else None

# ---------------------- AUTH MANAGER ----------------------
class AuthManager:
    def __init__(self):
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        self.max_failed_attempts = MAX_FAILED_ATTEMPTS
        self.lockout_duration = LOCKOUT_DURATION
        self.users = self.load_users()
        self.bad_words = self.load_bad_words()

    # ---------- Bad Words ----------
    def load_bad_words(self) -> List[str]:
        """Lädt verbotene Benutzernamen aus Datei"""
        if not os.path.exists(BAD_WORDS_FILE):
            print(f"Info: {BAD_WORDS_FILE} existiert nicht – erstelle leere Datei")
            os.makedirs(os.path.dirname(BAD_WORDS_FILE), exist_ok=True)
            with open(BAD_WORDS_FILE, "w", encoding="utf-8") as f:
                f.write("# Verbotene Benutzernamen (ein Name pro Zeile)\nadmin\nroot\nsystem\n")
            return ["admin", "root", "system"]
        
        try:
            with open(BAD_WORDS_FILE, "r", encoding="utf-8") as f:
                words = []
                for line in f:
                    line = line.strip().lower()
                    if line and not line.startswith("#"):
                        words.append(line)
                print(f"Info: {len(words)} verbotene Namen geladen")
                return words
        except Exception as e:
            print(f"ERROR: Fehler beim Laden von {BAD_WORDS_FILE}: {e}")
            return []
    
    def is_username_allowed(self, username: str) -> Tuple[bool, str]:
        """Prüft ob der Benutzername erlaubt ist"""
        username_lower = username.lower().strip()
        
        if not username_lower:
            return False, "Benutzername darf nicht leer sein"
        
        if len(username_lower) < 3:
            return False, "Benutzername muss mindestens 3 Zeichen lang sein"
        
        if len(username_lower) > 20:
            return False, "Benutzername darf maximal 20 Zeichen lang sein"
        
        if not all(c.isalnum() or c in ['_', '-'] for c in username_lower):
            return False, "Benutzername darf nur Buchstaben, Zahlen, _ und - enthalten"
        
        if username_lower in self.bad_words:
            return False, "Dieser Benutzername ist nicht erlaubt"
        
        for bad_word in self.bad_words:
            if bad_word in username_lower and len(bad_word) > 3:
                return False, f"Benutzername darf '{bad_word}' nicht enthalten"
        
        return True, "OK"

    # ---------- Password Hash ----------
    def hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """Hash a password with PBKDF2"""
        if salt is None:
            salt = secrets.token_hex(16)
        hash_bytes = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100_000)
        return hash_bytes.hex(), salt

    def verify_password(self, password: str, user: User) -> bool:
        """Verify a password against stored hash"""
        if not user.salt:
            return self.hash_password_simple(password) == user.password_hash
        pw_hash, _ = self.hash_password(password, user.salt)
        return pw_hash == user.password_hash
    
    def hash_password_simple(self, password: str) -> str:
        """Simple hash for backward compatibility"""
        return hashlib.sha256(password.encode()).hexdigest()

    # ---------- Account Locking ----------
    def handle_failed_login(self, user: User):
        """Behandelt fehlgeschlagene Anmeldeversuche"""
        user.failed_attempts += 1
        
        if user.failed_attempts >= self.max_failed_attempts:
            user.locked_until = datetime.now() + self.lockout_duration
            print(f"Warning: Account '{user.username}' gesperrt bis {user.locked_until}")
        
        self.save_users()
    
    def reset_failed_attempts(self, user: User):
        """Setzt fehlgeschlagene Versuche zurück nach erfolgreicher Anmeldung"""
        user.failed_attempts = 0
        user.locked_until = None

    # ---------- Users Load/Save ----------
    def load_users(self) -> Dict[str, User]:
        """Load users from JSON file with robust error handling"""
        if not os.path.exists(USERS_FILE):
            print(f"Info: {USERS_FILE} existiert nicht, starte mit leerer Benutzerliste")
            return {}
        
        if os.path.getsize(USERS_FILE) == 0:
            print(f"Warning: {USERS_FILE} ist leer")
            return {}
        
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    print(f"Warning: {USERS_FILE} enthält keine Daten")
                    return {}
                data = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"ERROR: Fehler beim Laden von {USERS_FILE}: {e}")
            backup_file = f"{USERS_FILE}.corrupt.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                import shutil
                shutil.copy2(USERS_FILE, backup_file)
                print(f"Backup der korrupten Datei erstellt: {backup_file}")
            except:
                pass
            return {}
        except Exception as e:
            print(f"ERROR: Unerwarteter Fehler beim Laden: {e}")
            return {}
        
        if not isinstance(data, dict):
            print(f"ERROR: {USERS_FILE} hat ungültiges Format (erwartet: dict)")
            return {}
        
        if not data:
            print(f"Info: {USERS_FILE} enthält keine Benutzer")
            return {}
        
        users = {}
        for username, udata in data.items():
            if not isinstance(udata, dict):
                print(f"Warning: Ungültige Daten für Benutzer '{username}' - überspringe")
                continue
            
            try:
                user = self._parse_user(username, udata)
                if user:
                    users[username] = user
            except Exception as e:
                print(f"ERROR: Fehler beim Parsen von Benutzer '{username}': {e}")
                continue
        
        print(f"Info: {len(users)} Benutzer erfolgreich geladen")
        return users
    
    def _parse_user(self, username: str, udata: dict) -> Optional[User]:
        """Parse a single user from JSON data"""
        password_hash = udata.get("password_hash") or udata.get("password")
        if not password_hash:
            print(f"Warning: Kein Passwort für Benutzer '{username}' - überspringe")
            return None
        
        role = UserRole.USER
        try:
            if "role" in udata:
                role_value = udata["role"]
                if isinstance(role_value, str):
                    role = UserRole(role_value)
                elif isinstance(role_value, bool):
                    role = UserRole.ADMIN if role_value else UserRole.USER
            elif "is_admin" in udata:
                is_admin = udata["is_admin"]
                if isinstance(is_admin, bool):
                    role = UserRole.ADMIN if is_admin else UserRole.USER
        except (ValueError, KeyError, TypeError):
            role = UserRole.USER
        
        active = udata.get("active", True)
        if not isinstance(active, bool):
            active = True
        
        created_at = datetime.now()
        if "created_at" in udata and udata["created_at"]:
            try:
                created_at = datetime.fromisoformat(udata["created_at"])
            except:
                pass
        
        last_login = None
        if "last_login" in udata and udata["last_login"]:
            try:
                last_login = datetime.fromisoformat(udata["last_login"])
            except:
                pass
        
        using_default = udata.get("using_default", True)
        salt = udata.get("salt", "")
        failed_attempts = udata.get("failed_attempts", 0)
        
        locked_until = None
        if "locked_until" in udata and udata["locked_until"]:
            try:
                locked_until = datetime.fromisoformat(udata["locked_until"])
            except:
                pass
        
        return User(
            username=username,
            password_hash=password_hash,
            role=role,
            active=active,
            created_at=created_at,
            last_login=last_login,
            using_default=using_default,
            salt=salt,
            failed_attempts=failed_attempts,
            locked_until=locked_until
        )

    def save_users(self, users: dict = None):
        """Speichert die Benutzerliste"""
        if users is None:
            users = self.users

        data = {}
        for username, user in users.items():
            data[username] = {
                "password_hash": user.password_hash,
                "role": user.role.value,
                "active": user.active,
                "created_at": user.created_at.isoformat() if user.created_at else datetime.now().isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "using_default": user.using_default,
                "salt": user.salt,
                "failed_attempts": user.failed_attempts,
                "locked_until": user.locked_until.isoformat() if user.locked_until else None
            }

        try:
            temp_file = f"{USERS_FILE}.tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            if os.path.exists(USERS_FILE):
                import shutil
                backup = f"{USERS_FILE}.backup"
                shutil.copy2(USERS_FILE, backup)

            os.replace(temp_file, USERS_FILE)
            print(f"Info: {len(data)} Benutzer gespeichert")
        except Exception as e:
            print(f"ERROR: Fehler beim Speichern der Benutzer: {e}")
            if os.path.exists(temp_file):
                os.remove(temp_file)

    # ---------- Login ----------
    def login(self, username: str, password: str) -> dict:
        """Login a user or auto-register with default password"""
        allowed, message = self.is_username_allowed(username)
        if not allowed:
            return {
                "success": False,
                "message": message,
                "role": None,
                "using_default": False
            }
        
        if username not in self.users:
            if password != DEFAULT_PASSWORD:
                return {
                    "success": False,
                    "message": f"Neuer Benutzer: bitte Standard-Passwort '{DEFAULT_PASSWORD}' verwenden",
                    "role": None,
                    "using_default": False
                }
            
            print(f"Info: Neuer Benutzer '{username}' wird registriert")
            pw_hash, salt = self.hash_password(password)
            self.users[username] = User(
                username=username,
                password_hash=pw_hash,
                role=UserRole.USER,
                using_default=True,
                salt=salt
            )
            self.users[username].last_login = datetime.now()
            self.save_users()
            
            return {
                "success": True,
                "message": "Willkommen! Bitte ändere dein Passwort.",
                "using_default": True,
                "role": UserRole.USER
            }

        user = self.users[username]
        
        if user.is_locked():
            remaining = user.get_lockout_remaining()
            if remaining:
                minutes = int(remaining.total_seconds() / 60)
                return {
                    "success": False,
                    "message": f"Account gesperrt. Versuche es in {minutes} Minuten erneut.",
                    "role": None,
                    "using_default": False
                }
        
        if not user.active:
            return {
                "success": False,
                "message": "Benutzer ist deaktiviert",
                "role": None,
                "using_default": False
            }
        
        if not self.verify_password(password, user):
            self.handle_failed_login(user)
            attempts_left = self.max_failed_attempts - user.failed_attempts
            
            if user.is_locked():
                return {
                    "success": False,
                    "message": f"Zu viele Fehlversuche. Account für {int(self.lockout_duration.total_seconds() / 60)} Minuten gesperrt.",
                    "role": None,
                    "using_default": False
                }
            
            return {
                "success": False,
                "message": f"Ungültige Anmeldedaten. Noch {attempts_left} Versuche übrig.",
                "role": None,
                "using_default": False
            }

        self.reset_failed_attempts(user)
        user.last_login = datetime.now()
        self.save_users()
        
        print(f"Info: Benutzer '{username}' erfolgreich angemeldet (Rolle: {user.role.value})")
        return {
            "success": True,
            "message": "Erfolgreich angemeldet",
            "using_default": user.using_default,
            "role": user.role
        }

    # ---------- Register ----------
    def register(self, username: str, password: str) -> dict:
        """Register a new user"""
        allowed, message = self.is_username_allowed(username)
        if not allowed:
            return {
                "success": False,
                "message": message,
                "role": None,
                "using_default": False
            }
        
        if username in self.users:
            return {
                "success": False,
                "message": "Benutzer existiert bereits",
                "role": None,
                "using_default": False
            }
        
        if password != DEFAULT_PASSWORD:
            return {
                "success": False,
                "message": f"Bitte Standard-Passwort '{DEFAULT_PASSWORD}' verwenden",
                "role": None,
                "using_default": False
            }
        
        return self.login(username, password)

    # ---------- Password Change ----------
    def change_password(self, username: str, old_password: str, new_password: str) -> Tuple[bool, str]:
        """Change user password"""
        if username not in self.users:
            return False, "Benutzer nicht gefunden"
        
        user = self.users[username]
        if not self.verify_password(old_password, user):
            return False, "Altes Passwort falsch"
        
        if len(new_password) < 6:
            return False, "Neues Passwort muss mindestens 6 Zeichen lang sein"
        
        pw_hash, salt = self.hash_password(new_password)
        user.password_hash = pw_hash
        user.salt = salt
        user.using_default = False
        self.save_users()
        
        print(f"Info: Passwort für '{username}' erfolgreich geändert")
        return True, "Passwort erfolgreich geändert"
    
    # ---------- Authentication (für main.py Kompatibilität) ----------
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, str, bool]:
        """Returns (success, message, using_default) - für Kompatibilität mit main.py"""
        result = self.login(username, password)
        return result["success"], result["message"], result.get("using_default", False)
    
    # ========== ⚠️ KRITISCH: SESSION VALIDATION (BEI JEDEM SEITENAUFRUF!) ==========
    def validate_session(self, username: str) -> Tuple[bool, str, Optional[UserRole]]:
        """
        ⚠️ WICHTIG: MUSS bei JEDEM Seitenaufruf/Button-Klick aufgerufen werden!
        
        Überprüft ob der Benutzer noch aktiv/entsperrt ist.
        Lädt IMMER die aktuellsten Daten von der Festplatte!
        
        Returns:
            (is_valid, message, role)
            - is_valid: True = weitermachen, False = SOFORT RAUSWERFEN
            - message: Grund für Logout oder "OK"
            - role: UserRole wenn gültig, None wenn nicht
        """
        # ⚠️ WICHTIG: Lade FRISCHE Daten von Festplatte (falls Admin was geändert hat)
        fresh_users = self.load_users()
        
        # Check 1: Benutzer existiert nicht (mehr)?
        if username not in fresh_users:
            print(f"🔒 SECURITY: Benutzer '{username}' existiert nicht mehr - kicke raus!")
            return False, "Dein Account wurde gelöscht", None
        
        user = fresh_users[username]
        
        # Check 2: Benutzer wurde deaktiviert?
        if not user.active:
            print(f"🔒 SECURITY: Benutzer '{username}' wurde deaktiviert - kicke raus!")
            return False, "Dein Account wurde deaktiviert", None
        
        # Check 3: Benutzer wurde gesperrt?
        if user.is_locked():
            remaining = user.get_lockout_remaining()
            if remaining:
                minutes = int(remaining.total_seconds() / 60)
                print(f"🔒 SECURITY: Benutzer '{username}' ist gesperrt - kicke raus!")
                return False, f"Dein Account wurde gesperrt (noch {minutes} Min.)", None
        
        # ✅ Alles OK - User darf weitermachen
        # Aktualisiere self.users mit frischen Daten
        self.users = fresh_users
        return True, "OK", user.role
    
    def check_user_status(self, username: str) -> dict:
        """
        ⚠️ DIESE FUNKTION IN STREAMLIT BEI JEDEM SEITENAUFRUF AUFRUFEN!
        
        Kompakte Version für Streamlit-Integration.
        
        Usage in Streamlit:
        ```python
        if "username" in st.session_state:
            status = auth_manager.check_user_status(st.session_state.username)
            if status["should_logout"]:
                st.error(status["message"])
                # Session State löschen
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        ```
        
        Returns:
            {
                "valid": bool,              # True = alles OK, False = RAUSWERFEN
                "message": str,             # Fehlermeldung oder "OK"
                "role": str or None,        # "admin" oder "user"
                "should_logout": bool       # True = SOFORT ausloggen!
            }
        """
        is_valid, message, role = self.validate_session(username)
        
        return {
            "valid": is_valid,
            "message": message,
            "role": role.value if role else None,
            "should_logout": not is_valid
        }
    
    # ---------- Admin Functions ----------
    def create_admin(self, username: str, password: str) -> Tuple[bool, str]:
        """Create an admin user"""
        allowed, message = self.is_username_allowed(username)
        if not allowed:
            return False, message
        
        if username in self.users:
            return False, "Benutzer existiert bereits"
        
        pw_hash, salt = self.hash_password(password)
        admin_user = User(
            username=username,
            password_hash=pw_hash,
            role=UserRole.ADMIN,
            using_default=(password == DEFAULT_PASSWORD),
            salt=salt
        )
        self.users[username] = admin_user
        self.save_users()
        
        print(f"Info: Admin-Benutzer '{username}' erstellt")
        return True, f"Admin-Benutzer '{username}' wurde erstellt"
    
    def get_all_users(self) -> Dict[str, User]:
        """Get all users - lädt frische Daten"""
        self.users = self.load_users()
        return self.users
    
    def delete_user(self, username: str) -> Tuple[bool, str]:
        """Delete a user"""
        if username not in self.users:
            return False, "Benutzer nicht gefunden"
        
        del self.users[username]
        self.save_users()
        
        print(f"Info: Benutzer '{username}' gelöscht")
        return True, f"Benutzer '{username}' wurde gelöscht"
    
    def toggle_user_active(self, username: str) -> Tuple[bool, str]:
        """Activate or deactivate a user"""
        # Lade frische Daten
        self.users = self.load_users()
        
        if username not in self.users:
            return False, "Benutzer nicht gefunden"
        
        user = self.users[username]
        user.active = not user.active
        self.save_users()
        
        status = "aktiviert" if user.active else "deaktiviert"
        print(f"Info: Benutzer '{username}' {status}")
        return True, f"Benutzer '{username}' wurde {status}"
    
    def promote_to_admin(self, username: str) -> Tuple[bool, str]:
        """Promote a user to admin"""
        self.users = self.load_users()
        
        if username not in self.users:
            return False, "Benutzer nicht gefunden"
        
        user = self.users[username]
        if user.role == UserRole.ADMIN:
            return False, "Benutzer ist bereits Administrator"
        
        user.role = UserRole.ADMIN
        self.save_users()
        
        print(f"Info: Benutzer '{username}' zu Admin befördert")
        return True, f"Benutzer '{username}' ist jetzt Administrator"
    
    def demote_from_admin(self, username: str) -> Tuple[bool, str]:
        """Demote an admin to regular user"""
        self.users = self.load_users()
        
        if username not in self.users:
            return False, "Benutzer nicht gefunden"
        
        user = self.users[username]
        if user.role == UserRole.USER:
            return False, "Benutzer ist kein Administrator"
        
        user.role = UserRole.USER
        self.save_users()
        
        print(f"Info: Admin-Rechte von '{username}' entfernt")
        return True, f"Benutzer '{username}' ist jetzt normaler Benutzer"
    
    def unlock_user(self, username: str) -> Tuple[bool, str]:
        """Entsperrt einen gesperrten Benutzer (für Admins)"""
        self.users = self.load_users()
        
        if username not in self.users:
            return False, "Benutzer nicht gefunden"
        
        user = self.users[username]
        user.locked_until = None
        user.failed_attempts = 0
        self.save_users()
        
        print(f"Info: Benutzer '{username}' entsperrt")
        return True, f"Benutzer '{username}' wurde entsperrt"

   
def load_answers(filepath="./data/answers.json"):
    """Lädt gespeicherte Antworten aus einer JSON-Datei."""
    if not os.path.exists(filepath):
        print(f"Info: {filepath} existiert nicht – starte mit leerer Antwortliste")
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Fehler beim Laden von {filepath}: {e}")
        return {}