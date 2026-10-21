"""Gemeinsames Demo-Angriffsziel fuer alle Angriffs-Skripte.

Alle Angriffe in attacks/ greifen denselben simulierten Account an, damit
die verschiedenen Techniken direkt vergleichbar sind und dieselben
Verteidigungen (defenses/) vor genau diesen einen Account gesetzt werden
koennen.

Das Passwort ist bewusst kurz und einfach (Vorname des "Opfers") gewaehlt,
damit Mono-Alphabet-, Poly-Alphabet-, Dictionary- und Rainbow-Table-Angriff
es alle in nuetzlicher Demo-Zeit finden koennen.
"""

from common.account_store import AccountStore

DEMO_USERNAME = "demo_user"
DEMO_PASSWORD = "leon"


def build_demo_target() -> tuple[AccountStore, str]:
    """Baut den AccountStore mit dem Demo-User und gibt (store, username) zurueck."""
    store = AccountStore()
    store.add_user(DEMO_USERNAME, DEMO_PASSWORD)
    return store, DEMO_USERNAME
