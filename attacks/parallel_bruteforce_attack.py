"""Parallelisierter Brute-Force-Angriff (2.3b).

Teilt den Passwortraum (ein einzelner Zeichensatz, wie beim Mono-Alphabet-
Angriff) in gleich grosse Wertebereiche auf: jeder Prozess bekommt eine
Teilmenge der moeglichen ersten Zeichen und durchsucht nur Passwoerter, die
damit beginnen. Sobald ein Prozess das Passwort findet, brechen die anderen
ab, statt den Rest ihres Bereichs noch fertig zu durchsuchen.
"""

import argparse
import itertools
import string
import time
from multiprocessing import Event, Process, Queue

from common.account_store import AccountStore
from common.demo_target import DEMO_PASSWORD, build_demo_target
from common.hashing import hash_password

CHARSETS = {
    "digits": string.digits,
    "lower": string.ascii_lowercase,
    "upper": string.ascii_uppercase,
}


def _search_shard(
    target_hash: str,
    charset: str,
    max_length: int,
    first_characters: str,
    result_queue: Queue,
    stop_event,
) -> None:
    """Durchsucht nur Passwoerter, deren erstes Zeichen zu diesem Prozess gehoert.

    Wie beim Mono-Alphabet-Angriff werden kurze Laengen vor langen probiert
    (aussen nach Laenge, nicht nach Anfangszeichen) - sonst wuerde dieser
    Prozess erst alle langen Kandidaten mit seinem ersten Zeichen durchsuchen,
    bevor er ueberhaupt bei einer kuerzeren, aber erst spaeter zugeteilten
    Laenge ankommt.
    """
    attempts = 0
    for length in range(1, max_length + 1):
        if stop_event.is_set():
            break
        rest_length = length - 1
        for first_character in first_characters:
            if stop_event.is_set():
                break
            for rest in itertools.product(charset, repeat=rest_length):
                if stop_event.is_set():
                    break
                candidate = first_character + "".join(rest)
                attempts += 1
                if hash_password(candidate) == target_hash:
                    stop_event.set()
                    result_queue.put((candidate, attempts))
                    return
    result_queue.put((None, attempts))


def parallel_bruteforce_attack(
    account_store: AccountStore,
    username: str,
    charset: str,
    max_length: int,
    process_count: int,
) -> tuple[str | None, int]:
    """Teilt `charset` in process_count Wertebereiche auf und sucht parallel."""
    if process_count < 1:
        raise ValueError("process_count muss mindestens 1 sein.")

    target_hash = account_store.get_password_hash(username)
    if target_hash is None:
        return None, 0

    shards = [charset[i::process_count] for i in range(process_count)]
    shards = [shard for shard in shards if shard]

    result_queue: Queue = Queue()
    stop_event = Event()
    processes = [
        Process(
            target=_search_shard,
            args=(target_hash, charset, max_length, shard, result_queue, stop_event),
        )
        for shard in shards
    ]
    for process in processes:
        process.start()

    found_password: str | None = None
    total_attempts = 0
    for _ in processes:
        password, attempts = result_queue.get()
        total_attempts += attempts
        if password is not None:
            found_password = password

    for process in processes:
        process.join()

    return found_password, total_attempts


def main() -> None:
    parser = argparse.ArgumentParser(description="Parallelisierter Brute-Force-Angriff (2.3b)")
    parser.add_argument(
        "--charset", nargs="+", choices=sorted(CHARSETS), default=["lower"],
        help="Ein oder mehrere Zeichensaetze, die kombiniert werden "
        "(z.B. '--charset lower digits' fuer einen Poly-Alphabet-Suchraum)",
    )
    parser.add_argument("--max-length", type=int, default=4, help="Maximale Passwortlaenge, die probiert wird")
    parser.add_argument("--processes", type=int, default=4, help="Anzahl paralleler Instanzen/Prozesse")
    args = parser.parse_args()

    charset = "".join(dict.fromkeys("".join(CHARSETS[name] for name in args.charset)))
    store, username = build_demo_target()
    print(f"Zeichensatz: {'+'.join(args.charset)}, max. Laenge: {args.max_length}, Prozesse: {args.processes}")
    print(f"Ziel-Passwort (nur zur Kontrolle, normalerweise unbekannt): {DEMO_PASSWORD}")

    start = time.perf_counter()
    found, attempts = parallel_bruteforce_attack(store, username, charset, args.max_length, args.processes)
    duration = time.perf_counter() - start

    if found is not None:
        print(f"Passwort gefunden: '{found}' nach insgesamt {attempts} Versuchen in {duration:.3f}s")
    else:
        print(f"Passwort nicht gefunden nach insgesamt {attempts} Versuchen in {duration:.3f}s")


if __name__ == "__main__":
    main()
