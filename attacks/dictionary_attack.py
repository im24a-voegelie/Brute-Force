"""Dictionary-Angriff gegen das simulierte lokale Login-System."""

import json
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from common.account_store import AccountStore
from common.demo_target import build_demo_target

DATA_DIRECTORY = Path(__file__).resolve().parents[1] / "data"


@dataclass(frozen=True)
class AttackResult:
    """Ergebnis eines lokal simulierten Angriffs."""

    password: str | None
    attempts: int


def generate_candidates(wordlist_path: Path, profile_path: Path) -> Iterator[str]:
    """Liefert Wörterlisten-Einträge und einfache Varianten mit Profildaten."""
    words = [
        line.strip()
        for line in wordlist_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    if not isinstance(profile, dict):
        raise TypeError("Das Beispielprofil muss ein JSON-Objekt sein.")

    name = profile.get("name")
    birth_year = profile.get("birth_year")
    if not isinstance(name, str) or not isinstance(birth_year, (str, int)):
        raise TypeError("Das Beispielprofil braucht 'name' und 'birth_year'.")

    year = str(birth_year)
    seeds = [*words, name]
    seen: set[str] = set()
    for seed in seeds:
        variants = (seed, seed.lower(), seed.capitalize())
        for variant in variants:
            for candidate in (variant, f"{variant}{year}", f"{variant}{year[-2:]}"):
                if candidate not in seen:
                    seen.add(candidate)
                    yield candidate


def run_dictionary_attack(
    account_store: AccountStore,
    username: str,
    wordlist_path: Path = DATA_DIRECTORY / "wordlist.txt",
    profile_path: Path = DATA_DIRECTORY / "victim_profile.json",
) -> AttackResult:
    """Prüft eine kleine Kandidatenliste ausschliesslich über lokales login()."""
    attempts = 0
    for candidate in generate_candidates(wordlist_path, profile_path):
        attempts += 1
        if account_store.login(username, candidate):
            return AttackResult(password=candidate, attempts=attempts)
    return AttackResult(password=None, attempts=attempts)


def main() -> None:
    """Führt den Dictionary-Angriff gegen den gemeinsamen Demo-Account aus."""
    account_store, username = build_demo_target()
    result = run_dictionary_attack(account_store, username)
    if result.password is None:
        print(f"Kein Treffer nach {result.attempts} Kandidaten.")
    else:
        print(
            f"Treffer im lokalen Demo-Account: {result.password} "
            f"({result.attempts} Kandidaten geprüft)."
        )


if __name__ == "__main__":
    main()