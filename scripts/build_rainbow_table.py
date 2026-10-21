"""Generiert eine Rainbow-Table (Hash-Plain-Lookup-Datei) fuer 2.3a.

Der eigentliche Angriff (attacks/rainbow_table_attack.py) berechnet dann
selbst keine Hashes mehr, sondern schlaegt nur noch in dieser Datei nach.
Deshalb wird hier bewusst nur ein kleiner Passwortraum (ein einzelner
Zeichensatz, kurze Laenge) vorgerechnet - das Prinzip ist dasselbe wie bei
einer echten Rainbow-Table, nur in handlichem Massstab fuer die Demo.
"""

import argparse
import csv
import itertools
import string
from pathlib import Path

from common.hashing import hash_password

DATA_DIRECTORY = Path(__file__).resolve().parents[1] / "data"
DEFAULT_OUTPUT = DATA_DIRECTORY / "rainbow_table.csv"

CHARSETS = {
    "digits": string.digits,
    "lower": string.ascii_lowercase,
    "upper": string.ascii_uppercase,
}


def build_rainbow_table(charset: str, max_length: int) -> dict[str, str]:
    """Berechnet fuer jede Kombination aus `charset` bis `max_length` den Hash."""
    table: dict[str, str] = {}
    for length in range(1, max_length + 1):
        for combo in itertools.product(charset, repeat=length):
            plain = "".join(combo)
            table[hash_password(plain)] = plain
    return table


def write_rainbow_table(table: dict[str, str], output_path: Path) -> None:
    """Schreibt die Lookup-Tabelle als CSV mit den Spalten hash,plain."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["hash", "plain"])
        for password_hash, plain in table.items():
            writer.writerow([password_hash, plain])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rainbow-Table fuer den Demo-Passwortraum vorberechnen (2.3a)"
    )
    parser.add_argument(
        "--charset", choices=sorted(CHARSETS), default="lower",
        help="Zeichensatz der vorberechneten Passwoerter",
    )
    parser.add_argument(
        "--max-length", type=int, default=4,
        help="Maximale Passwortlaenge, die vorberechnet wird",
    )
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_OUTPUT,
        help="Zieldatei fuer die Lookup-Tabelle",
    )
    args = parser.parse_args()

    charset = CHARSETS[args.charset]
    table = build_rainbow_table(charset, args.max_length)
    write_rainbow_table(table, args.output)
    print(f"{len(table)} Hash-Plain-Paare in {args.output} geschrieben.")


if __name__ == "__main__":
    main()
