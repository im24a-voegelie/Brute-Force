"""Hilfsfunktionen zum Hashen von Passwoertern.

Bewusst ohne Salt: Das ist fuer dieses Uebungsprojekt so gewollt, damit der
Rainbow-Table-Angriff (siehe attacks/rainbow_table_attack.py) gegen die
gespeicherten Hashes funktioniert. In einem echten System waere das
unsicher - Passwoerter sollten dort immer gesalzen gehasht werden.
"""

import hashlib


def hash_password(password: str) -> str:
    """Berechnet den SHA-256-Hash eines Passworts als Hex-String."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()
