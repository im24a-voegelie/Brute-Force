"""Captcha/User-Interaktion nach mehreren Login-Fehlversuchen."""

import logging
import secrets
from collections import defaultdict
from collections.abc import Callable

LoginFunction = Callable[[str, str], bool]
InputFunction = Callable[[str], str]
LOGGER = logging.getLogger(__name__)


def apply_captcha_challenge(
    login_fn: LoginFunction,
    failure_threshold: int = 3,
    input_fn: InputFunction | None = None,
) -> LoginFunction:
    """Fordert ab dem Schwellwert vor jedem Login eine Rechenaufgabe an."""
    if failure_threshold < 1:
        raise ValueError("failure_threshold muss mindestens 1 sein.")

    failed_attempts: dict[str, int] = defaultdict(int)

    def defended_login(username: str, password: str) -> bool:
        if failed_attempts[username] >= failure_threshold:
            left = secrets.randbelow(9) + 1
            right = secrets.randbelow(9) + 1
            answer = (input if input_fn is None else input_fn)(
                f"Captcha: Was ist {left} + {right}? "
            )
            if answer.strip() != str(left + right):
                LOGGER.warning("Captcha für Benutzer %r nicht bestanden.", username)
                return False

        if login_fn(username, password):
            failed_attempts.pop(username, None)
            return True

        failed_attempts[username] += 1
        if failed_attempts[username] == failure_threshold:
            LOGGER.warning(
                "Captcha für Benutzer %r wird ab dem nächsten Login verlangt.",
                username,
            )
        return False

    return defended_login


def main() -> None:
    """Zeigt, dass nach drei Fehlern eine Captcha-Eingabe nötig wird."""
    from common.demo_target import DEMO_PASSWORD, build_demo_target

    store, username = build_demo_target()
    protected_login = apply_captcha_challenge(store.login)

    for attempt in range(1, 4):
        protected_login(username, "falsches-passwort")
        print(f"Fehlversuch {attempt}/3")

    print("Jetzt wird vor dem Login eine Rechenaufgabe abgefragt.")
    print("Richtiges Passwort akzeptiert:", protected_login(username, DEMO_PASSWORD))


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
    main()
