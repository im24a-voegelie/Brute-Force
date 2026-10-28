"""Rainbow-Table-Angriff (2.3a).

Berechnet waehrend des Angriffs selbst keine Hashes mehr, sondern schlaegt
nur noch in einer vorbereiteten Lookup-Datei (Hash-Plain) nach, die vorher
mit scripts/build_rainbow_table.py erzeugt wurde. Das ist der Unterschied
zu den Mono-/Poly-Alphabet-Angriffen, die pro Versuch jeweils neu hashen.
"""

import argparse
import csv
import time
from pathlib import Path

from common.account_store import AccountStore
from common.demo_target import build_demo_target

DATA_DIRECTORY = Path(__file__).resolve().parents[1] / "data"
DEFAULT_TABLE = DATA_DIRECTORY / "rainbow_table.csv"


def load_rainbow_table(table_path: Path) -> dict[str, str]:
    """Liest die Hash-Plain-Lookup-Datei in ein Dict (hash -> plain) ein."""
    if not table_path.exists():
        raise FileNotFoundError(
            f"{table_path} fehlt. Vorher 'python -m scripts.build_rainbow_table' ausfuehren."
        )
    table: dict[str, str] = {}
    with table_path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            table[row["hash"]] = row["plain"]
    return table


def rainbow_table_attack(
    account_store: AccountStore, username: str, table: dict[str, str]
) -> str | None:
    """Schlaegt den gespeicherten Passwort-Hash des Users in der Lookup-Tabelle nach."""
    password_hash = account_store.get_password_hash(username)
    if password_hash is None:
        return None
    return table.get(password_hash)


def main() -> None:
    parser = argparse.ArgumentParser(description="Rainbow-Table-Angriff (2.3a)")
    parser.add_argument(
        "--table",
        type=Path,
        default=DEFAULT_TABLE,
        help="Pfad zur vorberechneten Lookup-Datei",
    )
    args = parser.parse_args()

    store, username = build_demo_target()
    table = load_rainbow_table(args.table)
    print(f"Lookup-Tabelle geladen: {len(table)} Eintraege")

    start = time.perf_counter()
    found = rainbow_table_attack(store, username, table)
    duration = time.perf_counter() - start

    if found is not None:
        print(
            f"Passwort gefunden: '{found}' per Lookup in {duration:.6f}s (kein Hash berechnet)"
        )
    else:
        print(
            f"Passwort nicht in der Lookup-Tabelle enthalten (gesucht in {duration:.6f}s)"
        )


if __name__ == "__main__":
    main()
