import os
import json
import hashlib
import secrets
from enum import Enum
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, Dict, Tuple

# ---------------------- KONSTANTEN ----------------------
USERS_FILE = "./data/users.json"
DEFAULT_PASSWORD = "4-26-2011"

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
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

# ---------------------- AUTH MANAGER ----------------------
class AuthManager:
    def __init__(self):
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=30)
        self.users = self.load_users()

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
            # Fallback für alte Passwörter ohne Salt
            return self.hash_password_simple(password) == user.password_hash
        pw_hash, _ = self.hash_password(password, user.salt)
        return pw_hash == user.password_hash
    
    def hash_password_simple(self, password: str) -> str:
        """Simple hash for backward compatibility"""
        return hashlib.sha256(password.encode()).hexdigest()

    # ---------- Users Load/Save ----------
    def load_users(self) -> Dict[str, User]:
        """Load users from JSON file with robust error handling"""
        if not os.path.exists(USERS_FILE):
            print(f"Info: {USERS_FILE} existiert nicht, starte mit leerer Benutzerliste")
            return {}
        
        # Prüfe ob Datei leer ist
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
            print(f"Die Datei ist möglicherweise korrupt. Bitte prüfe sie manuell oder lösche sie.")
            # Erstelle Backup der korrupten Datei
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
        
        # Validiere JSON-Struktur
        if not isinstance(data, dict):
            print(f"ERROR: {USERS_FILE} hat ungültiges Format (erwartet: dict)")
            return {}
        
        if not data:
            print(f"Info: {USERS_FILE} enthält keine Benutzer")
            return {}
        
        # Parse jeden Benutzer
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
        # 1. Password Hash (erforderlich)
        password_hash = udata.get("password_hash") or udata.get("password")
        if not password_hash:
            print(f"Warning: Kein Passwort für Benutzer '{username}' - überspringe")
            return None
        
        # 2. Role - Handle verschiedene Formate
        role = UserRole.USER  # Default
        try:
            if "role" in udata:
                role_value = udata["role"]
                if isinstance(role_value, str):
                    # "admin" oder "user"
                    role = UserRole(role_value)
                elif isinstance(role_value, bool):
                    # True/False (sollte nicht vorkommen, aber zur Sicherheit)
                    role = UserRole.ADMIN if role_value else UserRole.USER
                    print(f"Warning: Benutzer '{username}' hat boolean role - konvertiere zu string")
            elif "is_admin" in udata:
                # Alte Format: is_admin = True/False
                is_admin = udata["is_admin"]
                if isinstance(is_admin, bool):
                    role = UserRole.ADMIN if is_admin else UserRole.USER
                    print(f"Info: Konvertiere is_admin für '{username}': {is_admin} → {role.value}")
                elif isinstance(is_admin, str):
                    # String "true"/"false" oder "admin"/"user"
                    if is_admin.lower() in ["true", "admin", "1"]:
                        role = UserRole.ADMIN
                    else:
                        role = UserRole.USER
                    print(f"Info: Konvertiere is_admin string für '{username}': '{is_admin}' → {role.value}")
        except (ValueError, KeyError, TypeError) as e:
            print(f"Warning: Fehler beim Parsen der Rolle für '{username}': {e} - verwende USER")
            role = UserRole.USER
        
        # 3. Active Status
        active = udata.get("active", True)
        if not isinstance(active, bool):
            active = True
        
        # 4. Created At
        created_at = datetime.now()
        if "created_at" in udata and udata["created_at"]:
            try:
                created_at = datetime.fromisoformat(udata["created_at"])
            except (ValueError, TypeError) as e:
                print(f"Warning: Ungültiges created_at für '{username}': {e}")
        
        # 5. Last Login
        last_login = None
        if "last_login" in udata and udata["last_login"]:
            try:
                last_login = datetime.fromisoformat(udata["last_login"])
            except (ValueError, TypeError) as e:
                print(f"Warning: Ungültiges last_login für '{username}': {e}")
        
        # 6. Using Default Password
        using_default = udata.get("using_default", True)
        if not isinstance(using_default, bool):
            using_default = True
        
        # 7. Salt
        salt = udata.get("salt", "")
        if not isinstance(salt, str):
            salt = ""
        
        return User(
            username=username,
            password_hash=password_hash,
            role=role,
            active=active,
            created_at=created_at,
            last_login=last_login,
            using_default=using_default,
            salt=salt
        )

    def save_users(self, users: dict = None):
        """
        Speichert die Benutzerliste.

        - users: optional, dict mit User-Objekten. 
          Wenn None, wird self.users verwendet.
        """
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
                "salt": user.salt
            }

        try:
            # Schreibe in temporäre Datei zuerst
            temp_file = f"{USERS_FILE}.tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Backup der alten Datei
            if os.path.exists(USERS_FILE):
                import shutil
                backup = f"{USERS_FILE}.backup"
                shutil.copy2(USERS_FILE, backup)

            # Überschreiben
            os.replace(temp_file, USERS_FILE)
            print(f"Info: {len(data)} Benutzer gespeichert")
        except Exception as e:
            print(f"ERROR: Fehler beim Speichern der Benutzer: {e}")
            if os.exists(temp_file):
                os.remove(temp_file)

    # ---------- Login ----------
    def login(self, username: str, password: str) -> dict:
        """Login a user or auto-register with default password"""
        # Neuer Benutzer automatisch mit DEFAULT_PASSWORD
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
            self.save_users()
            return {
                "success": True, 
                "message": "Neuer Benutzer erstellt. Bitte Passwort ändern.", 
                "using_default": True, 
                "role": UserRole.USER
            }

        # Bestehender Benutzer
        user = self.users[username]
        
        if not user.active:
            return {
                "success": False, 
                "message": "Benutzer ist deaktiviert", 
                "role": None,
                "using_default": False
            }
        
        if not self.verify_password(password, user):
            return {
                "success": False, 
                "message": "Ungültige Anmeldedaten", 
                "role": None,
                "using_default": False
            }

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
    
    # ---------- Admin Functions ----------
    def create_admin(self, username: str, password: str) -> Tuple[bool, str]:
        """Create an admin user"""
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
        """Get all users"""
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
        if username not in self.users:
            return False, "Benutzer nicht gefunden"
        
        user = self.users[username]
        if user.role == UserRole.USER:
            return False, "Benutzer ist kein Administrator"
        
        user.role = UserRole.USER
        self.save_users()
        
        print(f"Info: Admin-Rechte von '{username}' entfernt")
        return True, f"Benutzer '{username}' ist jetzt normaler Benutzer"
    
    

   
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