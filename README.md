# Brute-Force

Ein BruteForce-Showcase im Rahmen von M183 LU02f/LB2 (Fokusthema BruteForce).

Das Projekt zeigt verschiedene Angriffs- und Verteidigungsvarianten gegen ein
simuliertes lokales Login-System. Es gibt bewusst kein Frontend — alles läuft
über die Kommandozeile.

Der vollständige Umsetzungsplan mit allen Schritten steht in [Plan.md](Plan.md).

## Setup

Benötigt wird nur Python 3.11+ (alle Angriffe/Verteidigungen nutzen die
Standardbibliothek). `ruff` ist optional für das Linting.

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

## Struktur

```
common/     Simuliertes Login-System (gehashte User/Passwort-Paare)
attacks/    Ein Skript pro Angriffsvariante (2.1-2.3)
defenses/   Ein Skript pro Verteidigungsvariante (3.1-3.3)
data/       Wordlist, Opferprofil, generierte Rainbow-Table
scripts/    Hilfsskripte, z.B. Rainbow-Table generieren
demo/       CLI, um Angriff + Verteidigung kombiniert auszuprobieren
```

Details zu jeder Komponente stehen im Architektur-Abschnitt von
[Plan.md](Plan.md). Weitere Ausführungsbeispiele werden ergänzt, sobald die
übrigen Skripte umgesetzt sind.

## Mittlere Angriffe (2.2)

Beide Skripte verwenden `common/demo_target.py` und greifen damit denselben
simulierten In-Memory-Account (`demo_user`) wie die anderen Angriffe an. Sie
verbinden sich nicht mit einem Netzwerkdienst. Das Passwort `Gtm0` ist für
die Demo absichtlich kurz gehalten.

```bash
python -m attacks.dictionary_attack
python -m attacks.poly_alphabet_attack
```

Der Dictionary-Angriff prüft die Beispiel-Wortliste in `data/wordlist.txt`
sowie Schreibweisen und Varianten mit dem fiktiven Namen/Geburtsjahr aus
`data/victim_profile.json`. Der Poly-Alphabet-Angriff kombiniert Buchstaben
und Ziffern aus einem kleinen Zeichensatz, der das Demo-Passwort enthält. Die
Demos halten Wortliste, Zeichensatz und Passwortlänge absichtlich klein,
damit sie schnell und nachvollziehbar laufen; grössere Suchräume wachsen sehr
schnell.
