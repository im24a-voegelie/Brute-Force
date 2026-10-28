"""Poly-Alphabet-Angriff gegen das simulierte lokale Login-System.

Die Vorgabe erlaubt bis zu 10 Zeichen aus Grossbuchstaben, Kleinbuchstaben,
Ziffern und Sonderzeichen kombiniert. Der Demo-Default ist bewusst kleiner
(Klein­buchstaben + Ziffern, Laenge 4), damit ein Lauf ohne Argumente in
nuetzlicher Zeit durchlaeuft; mit --alphabet/--max-length laesst sich der
volle Suchraum testen.
"""

from collections.abc import Callable
from dataclasses import dataclass
from itertools import product
from string import ascii_lowercase, digits
from time import perf_counter

from common.account_store import AccountStore
from common.demo_target import build_demo_target

DEFAULT_ALPHABET = ascii_lowercase + digits


@dataclass(frozen=True)
class AttackResult:
    """Ergebnis eines lokal simulierten Angriffs."""

    password: str | None
    attempts: int
    elapsed_seconds: float


def run_poly_alphabet_attack(
    account_store: AccountStore,
    username: str,
    alphabet: str = DEFAULT_ALPHABET,
    max_length: int = 4,
    login_fn: Callable[[str, str], bool] | None = None,
) -> AttackResult:
    """Prüft Kombinationen aus sichtbaren ASCII-Buchstaben, Ziffern und Satzzeichen."""
    if not alphabet:
        raise ValueError("Der Zeichensatz darf nicht leer sein.")
    if len(set(alphabet)) != len(alphabet):
        raise ValueError("Der Zeichensatz darf keine doppelten Zeichen enthalten.")
    if not 1 <= max_length <= 10:
        raise ValueError("Die Maximallänge muss zwischen 1 und 10 liegen.")

    start_time = perf_counter()
    login = account_store.login if login_fn is None else login_fn
    attempts = 0
    for length in range(1, max_length + 1):
        for characters in product(alphabet, repeat=length):
            candidate = "".join(characters)
            attempts += 1
            if login(username, candidate):
                return AttackResult(
                    password=candidate,
                    attempts=attempts,
                    elapsed_seconds=perf_counter() - start_time,
                )
    return AttackResult(
        password=None,
        attempts=attempts,
        elapsed_seconds=perf_counter() - start_time,
    )


def main() -> None:
    """Führt den Poly-Alphabet-Angriff gegen den gemeinsamen Demo-Account aus."""
    account_store, username = build_demo_target()
    result = run_poly_alphabet_attack(account_store, username)
    if result.password is None:
        print(
            f"Kein Treffer nach {result.attempts} Kandidaten "
            f"in {result.elapsed_seconds:.6f} Sekunden."
        )
    else:
        print(
            f"Treffer im lokalen Demo-Account: {result.password} "
            f"({result.attempts} Kandidaten in {result.elapsed_seconds:.6f} "
            "Sekunden geprüft)."
        )


if __name__ == "__main__":
    main()
