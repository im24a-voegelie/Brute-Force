"""Demo-CLI: Angriff und optionale Verteidigung kombinieren (Schritt 9).

Verbindet einen Angriff aus attacks/ mit einer Verteidigung aus defenses/,
beide gegen denselben gemeinsamen Demo-Account aus common/demo_target.py.

Nicht jede Kombination verhaelt sich gleich:

- counter_limit und captcha_challenge geben nach dem Schwellwert sofort
  False zurueck, OHNE das echte login() nochmal aufzurufen. Deshalb bleiben
  sie auch mit einem grossen Suchraum (Mono-/Poly-Alphabet) schnell - der
  Angriff laeuft durch, meldet aber "nicht gefunden", weil der Account
  gesperrt ist.
- linear_delay und progressive_delay warten bei JEDEM Versuch wirklich
  (time.sleep). Bei zehntausenden Versuchen waere das Stunden - das ist
  genau der Sinn dieser Verteidigungen. Deshalb ist der Demo-Default fuer
  Mono-/Poly-Alphabet bewusst klein (--max-length 2) und fuer eine
  realistische, schnelle Demo eignet sich besser der Dictionary-Angriff
  (wenige Kandidaten von Natur aus).
- Der Rainbow-Table- und der parallelisierte Angriff rufen login() gar
  nicht auf (sie vergleichen Hashes direkt) - Verteidigungen haben dort
  keine Wirkung. Die Demo weist bei dieser Kombination ausdruecklich darauf
  hin, statt es stillschweigend zu ignorieren.
"""

import argparse
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass

from attacks.dictionary_attack import run_dictionary_attack
from attacks.mono_alphabet_attack import CHARSETS as MONO_CHARSETS
from attacks.mono_alphabet_attack import mono_alphabet_attack
from attacks.parallel_bruteforce_attack import CHARSETS as PARALLEL_CHARSETS
from attacks.parallel_bruteforce_attack import parallel_bruteforce_attack
from attacks.poly_alphabet_attack import run_poly_alphabet_attack
from attacks.rainbow_table_attack import (
    DEFAULT_TABLE,
    load_rainbow_table,
    rainbow_table_attack,
)
from common.account_store import AccountStore
from common.demo_target import build_demo_target
from defenses.captcha_challenge import apply_captcha_challenge
from defenses.counter_limit import apply_counter_limit
from defenses.linear_delay import apply_linear_delay
from defenses.logging_defense import DEFAULT_LOG_PATH, apply_logging_defense
from defenses.progressive_delay import apply_progressive_delay

LoginFunction = Callable[[str, str], bool]

ATTACK_CHOICES = ["dictionary", "mono", "poly", "rainbow_table", "parallel"]
DEFENSE_CHOICES = [
    "none",
    "linear_delay",
    "progressive_delay",
    "counter_limit",
    "captcha_challenge",
    "logging_defense",
]
ATTACKS_WITHOUT_LOGIN_CALL = {"rainbow_table", "parallel"}
POLY_DEMO_ALPHABET = "".join(
    dict.fromkeys(MONO_CHARSETS["lower"] + MONO_CHARSETS["digits"])
)


@dataclass
class DemoResult:
    """Einheitliches Ergebnis, egal welcher Angriff gelaufen ist."""

    password: str | None
    attempts: int | None
    elapsed_seconds: float


class DemoAttemptLimitReached(Exception):
    """Nur fuer die Demo-CLI: bricht einen Angriff nach zu vielen Versuchen ab.

    Kein Teil der eigentlichen Verteidigung - progressive_delay waechst
    exponentiell, daher waere ein nicht erfolgreicher Angriff nach wenigen
    Dutzend Versuchen praktisch nie fertig. Ein echter Angreifer haette hier
    laengst aufgegeben; die Demo bildet das nach, statt tatsaechlich Stunden
    oder Tage zu warten.
    """


def cap_attempts(login: LoginFunction, max_attempts: int | None) -> LoginFunction:
    """Bricht mit DemoAttemptLimitReached ab, sobald max_attempts ueberschritten ist."""
    if max_attempts is None:
        return login

    calls = 0

    def capped_login(username: str, password: str) -> bool:
        nonlocal calls
        calls += 1
        if calls > max_attempts:
            raise DemoAttemptLimitReached(calls - 1)
        return login(username, password)

    return capped_login


def _robot_cannot_solve_captcha(_prompt: str) -> str:
    """Simuliert einen automatisierten Angreifer, der die Rechenaufgabe nie loest."""
    return "ich-bin-kein-mensch"


def build_defended_login(
    account_store: AccountStore, args: argparse.Namespace
) -> LoginFunction:
    """Baut login() mit der per --defense gewaehlten Verteidigung (oder ohne)."""
    if args.defense == "none":
        return account_store.login
    if args.defense == "linear_delay":
        return apply_linear_delay(account_store.login, delay_seconds=args.delay)
    if args.defense == "progressive_delay":
        return apply_progressive_delay(
            account_store.login, base_delay=args.base_delay, multiplier=args.multiplier
        )
    if args.defense == "counter_limit":
        return apply_counter_limit(account_store.login, max_failures=args.max_failures)
    if args.defense == "captcha_challenge":
        return apply_captcha_challenge(
            account_store.login,
            failure_threshold=args.failure_threshold,
            input_fn=_robot_cannot_solve_captcha,
        )
    if args.defense == "logging_defense":
        return apply_logging_defense(
            account_store.login,
            failure_threshold=args.failure_threshold,
            window_seconds=args.window_seconds,
            log_path=args.log_file,
        )
    raise ValueError(f"Unbekannte Verteidigung: {args.defense}")


def run_attack(
    login: LoginFunction,
    account_store: AccountStore,
    username: str,
    args: argparse.Namespace,
) -> DemoResult:
    """Fuehrt den per --attack gewaehlten Angriff gegen `login` aus."""
    if args.attack == "dictionary":
        result = run_dictionary_attack(account_store, username, login_fn=login)
        return DemoResult(result.password, result.attempts, result.elapsed_seconds)

    if args.attack == "mono":
        start = time.perf_counter()
        password, attempts = mono_alphabet_attack(
            login, username, MONO_CHARSETS[args.charset], args.max_length
        )
        return DemoResult(password, attempts, time.perf_counter() - start)

    if args.attack == "poly":
        result = run_poly_alphabet_attack(
            account_store,
            username,
            alphabet=POLY_DEMO_ALPHABET,
            max_length=args.max_length,
            login_fn=login,
        )
        return DemoResult(result.password, result.attempts, result.elapsed_seconds)

    if args.attack == "rainbow_table":
        table = load_rainbow_table(DEFAULT_TABLE)
        start = time.perf_counter()
        found = rainbow_table_attack(account_store, username, table)
        return DemoResult(found, None, time.perf_counter() - start)

    if args.attack == "parallel":
        charset = PARALLEL_CHARSETS[args.charset]
        start = time.perf_counter()
        found, attempts = parallel_bruteforce_attack(
            account_store, username, charset, args.max_length, args.processes
        )
        return DemoResult(found, attempts, time.perf_counter() - start)

    raise ValueError(f"Unbekannter Angriff: {args.attack}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Demo: Angriff + Verteidigung kombinieren"
    )
    parser.add_argument(
        "--attack",
        choices=ATTACK_CHOICES,
        default="dictionary",
        help="Welcher Angriff laeuft",
    )
    parser.add_argument(
        "--defense",
        choices=DEFENSE_CHOICES,
        default="none",
        help="Welche Verteidigung davor geschaltet wird",
    )

    # Angriffs-Parameter (nur fuer die jeweils passenden Angriffe relevant)
    parser.add_argument(
        "--max-length",
        type=int,
        default=2,
        help="Maximale Passwortlaenge fuer mono/poly/parallel (klein, damit es mit "
        "Latenz-Verteidigungen in nuetzlicher Zeit bleibt; siehe Moduldoku)",
    )
    parser.add_argument(
        "--charset",
        choices=sorted(MONO_CHARSETS),
        default="lower",
        help="Zeichensatz fuer mono/parallel",
    )
    parser.add_argument(
        "--processes",
        type=int,
        default=2,
        help="Anzahl Prozesse fuer den parallelisierten Angriff",
    )

    # Verteidigungs-Parameter
    parser.add_argument(
        "--delay",
        type=float,
        default=0.05,
        help="linear_delay: Wartezeit je Versuch in Sekunden",
    )
    parser.add_argument(
        "--base-delay",
        type=float,
        default=0.3,
        help="progressive_delay: Wartezeit nach dem 1. Fehlversuch",
    )
    parser.add_argument(
        "--multiplier",
        type=float,
        default=2.0,
        help="progressive_delay: Wachstumsfaktor je Fehlversuch",
    )
    parser.add_argument(
        "--max-failures",
        type=int,
        default=3,
        help="counter_limit: Fehlversuche bis zur Sperre",
    )
    parser.add_argument(
        "--failure-threshold",
        type=int,
        default=3,
        help="captcha_challenge/logging_defense: Fehlversuche bis Captcha bzw. Alarm",
    )
    parser.add_argument(
        "--window-seconds",
        type=int,
        default=60,
        help="logging_defense: Zeitfenster fuer den Alarm",
    )
    parser.add_argument(
        "--log-file",
        type=type(DEFAULT_LOG_PATH),
        default=DEFAULT_LOG_PATH,
        help="logging_defense: Zieldatei",
    )
    parser.add_argument(
        "--demo-max-attempts",
        type=int,
        default=None,
        help="Bricht die Demo nach dieser Anzahl Versuche ab. Default: automatisch "
        "8 bei progressive_delay (waechst exponentiell), sonst unbegrenzt.",
    )
    return parser


def main() -> None:
    # captcha_challenge/counter_limit loggen pro blockiertem Versuch eine Warnung.
    # Bei einem erschoepfenden Angriff (hunderttausende Versuche) wuerde das die
    # Konsole ueberfluten, deshalb wird hier nur auf ERROR-Niveau protokolliert.
    logging.basicConfig(level=logging.ERROR)

    args = build_arg_parser().parse_args()

    if args.attack in ATTACKS_WITHOUT_LOGIN_CALL and args.defense != "none":
        print(
            f"Hinweis: '{args.attack}' ruft login() nicht auf (es vergleicht Hashes direkt), "
            f"'{args.defense}' hat hier also keine Wirkung.\n"
        )

    account_store, username = build_demo_target()
    login = build_defended_login(account_store, args)

    demo_max_attempts = args.demo_max_attempts
    if demo_max_attempts is None and args.defense == "progressive_delay":
        demo_max_attempts = 8
    login = cap_attempts(login, demo_max_attempts)

    print(f"Angriff: {args.attack}, Verteidigung: {args.defense}")
    try:
        result = run_attack(login, account_store, username, args)
    except DemoAttemptLimitReached as exc:
        attempts_done = exc.args[0]
        print(
            f"Demo nach {attempts_done} Versuchen abgebrochen: progressive_delay waechst "
            "exponentiell, ein echter Angreifer haette hier laengst aufgegeben "
            "(--demo-max-attempts anpassen, um mehr/weniger zu erlauben)."
        )
        return

    attempts_text = "unbekannt" if result.attempts is None else str(result.attempts)
    if result.password is not None:
        print(
            f"Passwort gefunden: '{result.password}' nach {attempts_text} Versuchen "
            f"in {result.elapsed_seconds:.3f}s"
        )
    else:
        print(
            f"Passwort nicht gefunden nach {attempts_text} Versuchen in {result.elapsed_seconds:.3f}s"
        )


if __name__ == "__main__":
    main()
