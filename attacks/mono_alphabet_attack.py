"""Mono-Alphabet-Angriff (2.1).

Probiert alle Kombinationen aus einem einzigen Zeichensatz (nur Ziffern,
nur Kleinbuchstaben oder nur Grossbuchstaben) bis zu einer Maximallaenge
gegen ein login()-Callable durch. Das Passwort ist laut Vorgabe bis zu
10 Zeichen lang; der Demo-Default ist bewusst kleiner, damit der Angriff
in nuetzlicher Zeit durchlaeuft.

Greift den gemeinsamen Demo-Account aus common/demo_target.py an.
"""

import argparse
import itertools
import string
import time
from typing import Callable

from common.demo_target import DEMO_PASSWORD, build_demo_target

CHARSETS = {
    "digits": string.digits,
    "lower": string.ascii_lowercase,
    "upper": string.ascii_uppercase,
}


def mono_alphabet_attack(
    login: Callable[[str, str], bool],
    username: str,
    charset: str,
    max_length: int = 10,
) -> tuple[str | None, int]:
    """Probiert alle Passwoerter aus `charset` bis `max_length` Zeichen durch.

    Gibt ein Tupel (gefundenes_passwort, anzahl_versuche) zurueck. Ist das
    Passwort nicht im abgesuchten Raum, ist gefundenes_passwort None.
    """
    attempts = 0
    for length in range(1, max_length + 1):
        for combo in itertools.product(charset, repeat=length):
            password = "".join(combo)
            attempts += 1
            if login(username, password):
                return password, attempts
    return None, attempts


def main() -> None:
    parser = argparse.ArgumentParser(description="Mono-Alphabet Brute-Force-Angriff (2.1)")
    parser.add_argument("--charset", choices=sorted(CHARSETS), default="lower", help="Zeichensatz des gesuchten Passworts")
    parser.add_argument("--max-length", type=int, default=4, help="Maximale Passwortlaenge, die probiert wird (Vorgabe: bis 10)")
    args = parser.parse_args()

    charset = CHARSETS[args.charset]
    store, username = build_demo_target()
    print(f"Zeichensatz: {args.charset}, max. Laenge: {args.max_length}")
    print(f"Ziel-Passwort (nur zur Kontrolle, normalerweise unbekannt): {DEMO_PASSWORD}")

    start = time.perf_counter()
    found, attempts = mono_alphabet_attack(store.login, username, charset, args.max_length)
    duration = time.perf_counter() - start

    if found is not None:
        print(f"Passwort gefunden: '{found}' nach {attempts} Versuchen in {duration:.3f}s")
    else:
        print(f"Passwort nicht gefunden nach {attempts} Versuchen in {duration:.3f}s")


if __name__ == "__main__":
    main()
