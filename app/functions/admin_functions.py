# app/functions/admin_functions.py

import json
import os
from typing import Tuple, List

def get_active_users(users_file: str) -> List[str]:
    """
    Gibt eine Liste aller aktiven Benutzer zurück.
    """
    try:
        with open(users_file, "r", encoding="utf-8") as f:
            users = json.load(f)
        return [username for username, data in users.items() if data.get("active", True)]
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Fehler beim Laden der Benutzer: {e}")
        return []

def deactivate_user(admin_username: str, user_to_deactivate: str, users_file: str) -> Tuple[bool, str]:
    """
    Deaktiviert einen Benutzer und fügt ihn zur Blacklist hinzu.
    """
    try:
        with open(users_file, "r", encoding="utf-8") as f:
            users = json.load(f)

        # Prüfe, ob der ausführende Benutzer Admin ist
        if not users.get(admin_username, {}).get("is_admin", False):
            return False, "Nur Administratoren können Benutzer deaktivieren"

        if user_to_deactivate not in users:
            return False, f"Benutzer {user_to_deactivate} nicht gefunden"
            
        # Verhindere, dass Admins sich selbst deaktivieren
        if user_to_deactivate == admin_username:
            return False, "Administratoren können sich nicht selbst deaktivieren"

        # Deaktiviere den Benutzer
        users[user_to_deactivate]["active"] = False
        
        # Speichere die Änderungen
        with open(users_file, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4)
        
        return True, "Benutzer erfolgreich deaktiviert"
        
    except Exception as e:
        return False, f"Fehler beim Deaktivieren des Benutzers: {e}"

def reactivate_user(admin_username: str, user_to_reactivate: str, users_file: str) -> Tuple[bool, str]:
    """
    Reaktiviert einen deaktivierten Benutzer.
    """
    try:
        with open(users_file, "r", encoding="utf-8") as f:
            users = json.load(f)
        
        # Prüfe, ob der ausführende Benutzer Admin ist
        if not users.get(admin_username, {}).get("is_admin", False):
            return False, "Nur Administratoren können Benutzer reaktivieren"

        if user_to_reactivate not in users:
            return False, f"Benutzer {user_to_reactivate} nicht gefunden"

        # Reaktiviere den Benutzer
        users[user_to_reactivate]["active"] = True
        
        # Speichere die Änderungen
        with open(users_file, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4)
            
        return True, "Benutzer erfolgreich reaktiviert"
        
    except Exception as e:
        return False, f"Fehler beim Reaktivieren des Benutzers: {e}"