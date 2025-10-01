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
    created_at: datetime = datetime.now()
    last_login: Optional[datetime] = None
    using_default: bool = True
    salt: str = ""

# ---------------------- AUTH MANAGER ----------------------
class AuthManager:
    def __init__(self):
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=30)
        self.users = self.load_users()

    # ---------- Password Hash ----------
    def hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        if salt is None:
            salt = secrets.token_hex(16)
        hash_bytes = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100_000)
        return hash_bytes.hex(), salt

    def verify_password(self, password: str, user: User) -> bool:
        pw_hash, _ = self.hash_password(password, user.salt)
        return pw_hash == user.password_hash

    # ---------- Users Load/Save ----------
    def load_users(self) -> Dict[str, User]:
        if not os.path.exists(USERS_FILE):
            return {}
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        users = {}
        for uname, udata in data.items():
            users[uname] = User(
                username=uname,
                password_hash=udata["password"],
                role=UserRole(udata["is_admin"]),
                active=udata.get("active", True),
                created_at=datetime.fromisoformat(udata["created_at"]),
                last_login=datetime.fromisoformat(udata["last_login"]) if udata.get("last_login") else None,
                using_default=udata.get("using_default", True),
                salt=udata.get("salt", "")
            )
        return users

    def save_users(self):
        data = {}
        for uname, user in self.users.items():
            data[uname] = {
                "password_hash": user.password_hash,
                "role": user.role.value,
                "active": user.active,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "using_default": user.using_default,
                "salt": user.salt
            }
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ---------- Login ----------
    def login(self, username: str, password: str) -> dict:
        # Neuer Benutzer automatisch mit DEFAULT_PASSWORD
        if username not in self.users:
            if password != DEFAULT_PASSWORD:
                return {"success": False, "message": "Neuer Benutzer: bitte Standard-Passwort verwenden", "role": None}
            pw_hash, salt = self.hash_password(password)
            self.users[username] = User(username=username, password_hash=pw_hash, role=UserRole.USER, using_default=True, salt=salt)
            self.save_users()
            return {"success": True, "message": "Neuer Benutzer erstellt. Bitte Passwort ändern.", "using_default": True, "role": UserRole.USER}

        user = self.users[username]
        if not self.verify_password(password, user):
            return {"success": False, "message": "Ungültige Anmeldedaten", "role": None}

        user.last_login = datetime.now()
        self.save_users()
        return {"success": True, "message": "Erfolgreich angemeldet", "using_default": user.using_default, "role": user.role}

    # ---------- Register ----------
    def register(self, username: str, password: str) -> dict:
        if username in self.users:
            return {"success": False, "message": "Benutzer existiert bereits", "role": None}
        if password != DEFAULT_PASSWORD:
            return {"success": False, "message": "Bitte Standard-Passwort verwenden", "role": None}
        return self.login(username, password)

    # ---------- Password Change ----------
    def change_password(self, username: str, old_password: str, new_password: str) -> dict:
        if username not in self.users:
            return {"success": False, "message": "Benutzer nicht gefunden"}
        user = self.users[username]
        if not self.verify_password(old_password, user):
            return {"success": False, "message": "Altes Passwort falsch"}
        pw_hash, salt = self.hash_password(new_password)
        user.password_hash = pw_hash
        user.salt = salt
        user.using_default = False
        self.save_users()
        return {"success": True, "message": "Passwort erfolgreich geändert"}
