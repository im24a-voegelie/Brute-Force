"""Protokolliert fehlgeschlagene Logins und meldet auffällige Häufungen."""

import argparse
import csv
import logging
from collections import defaultdict, deque
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path

from common.demo_target import DEMO_PASSWORD, build_demo_target

LoginFunction = Callable[[str, str], bool]
LOGGER = logging.getLogger(__name__)
DEFAULT_LOG_PATH = Path(__file__).resolve().parents[1] / "logs" / "login_attempts.csv"


def _append_log_row(log_path: Path, timestamp: str, event: str, username: str) -> None:
    """Hängt einen strukturierten Eintrag an die CSV-Protokolldatei an."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not log_path.exists() or log_path.stat().st_size == 0
    with log_path.open("a", newline="", encoding="utf-8") as log_file:
        writer = csv.writer(log_file)
        if write_header:
            writer.writerow(["timestamp_utc", "event", "username"])
        writer.writerow([timestamp, event, username])


def apply_logging_defense(
    login_fn: LoginFunction,
    failure_threshold: int = 3,
    window_seconds: int = 60,
    log_path: Path = DEFAULT_LOG_PATH,
) -> LoginFunction:
    """Protokolliert Fehlversuche und löst bei einer Häufung einen Alarm aus.

    Die Verteidigung blockiert keine Logins. Sie meldet, wenn derselbe
    Benutzername mindestens `failure_threshold` Fehlversuche innerhalb des
    gleitenden Zeitfensters `window_seconds` verursacht.
    """
    if failure_threshold < 1:
        raise ValueError("failure_threshold muss mindestens 1 sein.")
    if window_seconds < 1:
        raise ValueError("window_seconds muss mindestens 1 sein.")

    failed_at: dict[str, deque[datetime]] = defaultdict(deque)
    alarm_active: set[str] = set()

    def defended_login(username: str, password: str) -> bool:
        success = login_fn(username, password)
        if success:
            failed_at.pop(username, None)
            alarm_active.discard(username)
            return True

        now = datetime.now(UTC)
        attempts = failed_at[username]
        cutoff = now - timedelta(seconds=window_seconds)
        while attempts and attempts[0] < cutoff:
            attempts.popleft()
        attempts.append(now)

        timestamp = now.isoformat()
        _append_log_row(log_path, timestamp, "LOGIN_FAILED", username)
        if len(attempts) >= failure_threshold and username not in alarm_active:
            _append_log_row(log_path, timestamp, "ALARM", username)
            LOGGER.warning(
                "Alarm: %d fehlgeschlagene Logins für %r innerhalb von %d Sekunden.",
                len(attempts),
                username,
                window_seconds,
            )
            alarm_active.add(username)
        elif len(attempts) < failure_threshold:
            alarm_active.discard(username)
        return False

    return defended_login


def main() -> None:
    """Führt drei Fehlversuche aus und zeigt Protokoll und Alarm."""
    parser = argparse.ArgumentParser(description="Login-Logging mit Alarm (3.3)")
    parser.add_argument(
        "--log-file",
        type=Path,
        default=DEFAULT_LOG_PATH,
        help="CSV-Datei für Fehlversuche und Alarmereignisse",
    )
    args = parser.parse_args()

    store, username = build_demo_target()
    protected_login = apply_logging_defense(store.login, log_path=args.log_file)

    for attempt in range(1, 4):
        accepted = protected_login(username, "falsches-passwort")
        print(f"Fehlversuch {attempt}/3: Login akzeptiert = {accepted}")

    accepted = protected_login(username, DEMO_PASSWORD)
    print(f"Richtiges Passwort danach akzeptiert = {accepted}")
    print(f"Protokoll: {args.log_file.resolve()}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
    main()
