"""Simuliertes lokales Login-System als Angriffsziel.

Haelt User/Passwort-Hash-Paare im Speicher und stellt eine login()-Funktion
bereit, gegen die die Skripte in attacks/ und defenses/ arbeiten.
"""

from common.hashing import hash_password


class AccountStore:
    """Einfache In-Memory-Nutzerverwaltung mit gehashten Passwoertern."""

    def __init__(self) -> None:
        self._password_hashes: dict[str, str] = {}

    def add_user(self, username: str, password: str) -> None:
        """Legt einen User an oder ueberschreibt sein Passwort."""
        self._password_hashes[username] = hash_password(password)

    def get_password_hash(self, username: str) -> str | None:
        """Gibt den gespeicherten Passwort-Hash zurueck, oder None falls unbekannt."""
        return self._password_hashes.get(username)

    def login(self, username: str, password: str) -> bool:
        """Prueft Benutzername und Passwort gegen den gespeicherten Hash."""
        stored_hash = self._password_hashes.get(username)
        if stored_hash is None:
            return False
        return stored_hash == hash_password(password)
