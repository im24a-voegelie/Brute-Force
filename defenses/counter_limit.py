"""Counter-Limit-Verteidigung für das simulierte lokale Login-System."""

import logging
from collections import defaultdict
from collections.abc import Callable

LoginFunction = Callable[[str, str], bool]
LOGGER = logging.getLogger(__name__)


def apply_counter_limit(
    login_fn: LoginFunction, max_failures: int = 3
) -> LoginFunction:
    """Sperrt einen Benutzernamen nach `max_failures` falschen Passwörtern."""
    if max_failures < 1:
        raise ValueError("max_failures muss mindestens 1 sein.")

    failed_attempts: dict[str, int] = defaultdict(int)
    locked_users: set[str] = set()

    def defended_login(username: str, password: str) -> bool:
        if username in locked_users:
            return False

        if login_fn(username, password):
            failed_attempts.pop(username, None)
            return True

        failed_attempts[username] += 1
        if failed_attempts[username] >= max_failures:
            locked_users.add(username)
            LOGGER.warning(
                "Konto %r nach %d Fehlversuchen gesperrt.",
                username,
                max_failures,
            )
        return False

    return defended_login


def main() -> None:
    """Zeigt die Sperre am gemeinsamen Demo-Account."""
    from common.demo_target import DEMO_PASSWORD, build_demo_target

    store, username = build_demo_target()
    protected_login = apply_counter_limit(store.login)

    for attempt in range(1, 4):
        protected_login(username, "falsches-passwort")
        print(f"Fehlversuch {attempt}/3")

    print(
        "Richtiges Passwort nach der Sperre akzeptiert:",
        protected_login(username, DEMO_PASSWORD),
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
    main()
