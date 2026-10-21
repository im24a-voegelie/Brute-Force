"""Poly-Alphabet-Angriff gegen das simulierte lokale Login-System."""

from dataclasses import dataclass
from itertools import product

from common.account_store import AccountStore
from common.demo_target import build_demo_target


@dataclass(frozen=True)
class AttackResult:
    """Ergebnis eines lokal simulierten Angriffs."""

    password: str | None
    attempts: int


def run_poly_alphabet_attack(
    account_store: AccountStore,
    username: str,
    alphabet: str = "Gtm0",
    max_length: int = 4,
) -> AttackResult:
    """Prüft Kombinationen aus einem kleinen, kombinierten Zeichensatz."""
    if not alphabet:
        raise ValueError("Der Zeichensatz darf nicht leer sein.")
    if len(set(alphabet)) != len(alphabet):
        raise ValueError("Der Zeichensatz darf keine doppelten Zeichen enthalten.")
    if not 1 <= max_length <= 10:
        raise ValueError("Die Maximallänge muss zwischen 1 und 10 liegen.")

    attempts = 0
    for length in range(1, max_length + 1):
        for characters in product(alphabet, repeat=length):
            candidate = "".join(characters)
            attempts += 1
            if account_store.login(username, candidate):
                return AttackResult(password=candidate, attempts=attempts)
    return AttackResult(password=None, attempts=attempts)


def main() -> None:
    """Führt den Poly-Alphabet-Angriff gegen den gemeinsamen Demo-Account aus."""
    account_store, username = build_demo_target()
    result = run_poly_alphabet_attack(account_store, username)
    if result.password is None:
        print(f"Kein Treffer nach {result.attempts} Kandidaten.")
    else:
        print(
            f"Treffer im lokalen Demo-Account: {result.password} "
            f"({result.attempts} Kandidaten geprüft)."
        )


if __name__ == "__main__":
    main()
