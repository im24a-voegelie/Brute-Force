"""Lineare Latenzzeit (3.1a).

Wartet nach jedem Login-Versuch eine feste Zeit (0.5-2 Sekunden), egal ob
er erfolgreich war oder nicht. Das verlangsamt Brute-Force-Angriffe linear
mit der Anzahl Versuche, ohne den Account zu sperren.
"""

import argparse
import time
from collections.abc import Callable

from common.demo_target import DEMO_PASSWORD, build_demo_target

LoginFunction = Callable[[str, str], bool]


def apply_linear_delay(
    login: LoginFunction, delay_seconds: float = 1.0
) -> LoginFunction:
    """Gibt eine login()-Funktion zurueck, die nach jedem Versuch wartet."""

    def protected_login(username: str, password: str) -> bool:
        result = login(username, password)
        time.sleep(delay_seconds)
        return result

    return protected_login


def main() -> None:
    parser = argparse.ArgumentParser(description="Demo: Lineare Latenzzeit (3.1a)")
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Wartezeit in Sekunden nach jedem Versuch (Vorgabe: 0.5-2s)",
    )
    parser.add_argument(
        "--attempts",
        type=int,
        default=3,
        help="Anzahl simulierter Fehlversuche vor dem korrekten Passwort",
    )
    args = parser.parse_args()

    store, username = build_demo_target()
    protected_login = apply_linear_delay(store.login, args.delay)

    for attempt in range(1, args.attempts + 1):
        start = time.perf_counter()
        success = protected_login(username, "falsches-passwort")
        duration = time.perf_counter() - start
        print(f"Versuch {attempt}: erfolgreich={success}, Dauer={duration:.2f}s")

    start = time.perf_counter()
    success = protected_login(username, DEMO_PASSWORD)
    duration = time.perf_counter() - start
    print(
        f"Versuch mit korrektem Passwort: erfolgreich={success}, Dauer={duration:.2f}s"
    )


if __name__ == "__main__":
    main()
