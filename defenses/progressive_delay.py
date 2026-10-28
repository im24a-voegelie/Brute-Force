"""Zunehmende Latenzzeit (3.1b).

Nach einem Fehlversuch muss vor dem naechsten Versuch desselben Users immer
laenger gewartet werden: 10 Sekunden nach dem ersten Fehlversuch, danach
1 Minute, danach entsprechend weiter (Faktor pro weiterem Fehlversuch). Ein
erfolgreicher Login setzt den Zaehler wieder auf null zurueck.
"""

import argparse
import time
from typing import Callable

from common.demo_target import DEMO_PASSWORD, build_demo_target

LoginFunction = Callable[[str, str], bool]


def apply_progressive_delay(
    login: LoginFunction, base_delay: float = 10.0, multiplier: float = 6.0
) -> LoginFunction:
    """Gibt eine login()-Funktion zurueck, die nach Fehlversuchen immer laenger wartet.

    Erster Fehlversuch -> base_delay Sekunden warten, zweiter -> base_delay*multiplier,
    etc. Die Standardwerte (10s, dann 60s, ...) entsprechen der Vorgabe.
    """
    failed_attempts: dict[str, int] = {}

    def protected_login(username: str, password: str) -> bool:
        failures = failed_attempts.get(username, 0)
        if failures > 0:
            time.sleep(base_delay * multiplier ** (failures - 1))

        success = login(username, password)
        failed_attempts[username] = 0 if success else failures + 1
        return success

    return protected_login


def main() -> None:
    parser = argparse.ArgumentParser(description="Demo: Zunehmende Latenzzeit (3.1b)")
    parser.add_argument("--base-delay", type=float, default=10.0, help="Wartezeit nach dem ersten Fehlversuch in Sekunden")
    parser.add_argument("--multiplier", type=float, default=6.0, help="Faktor, um den die Wartezeit je weiterem Fehlversuch waechst")
    parser.add_argument("--attempts", type=int, default=1, help="Anzahl simulierter Fehlversuche vor dem korrekten Passwort")
    args = parser.parse_args()

    store, username = build_demo_target()
    protected_login = apply_progressive_delay(store.login, args.base_delay, args.multiplier)

    for attempt in range(1, args.attempts + 1):
        start = time.perf_counter()
        success = protected_login(username, "falsches-passwort")
        duration = time.perf_counter() - start
        print(f"Versuch {attempt}: erfolgreich={success}, Wartezeit davor={duration:.2f}s")

    start = time.perf_counter()
    success = protected_login(username, DEMO_PASSWORD)
    duration = time.perf_counter() - start
    print(f"Versuch mit korrektem Passwort: erfolgreich={success}, Wartezeit davor={duration:.2f}s")


if __name__ == "__main__":
    main()
