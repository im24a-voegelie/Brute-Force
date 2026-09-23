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
[Plan.md](Plan.md). Sobald die einzelnen Skripte umgesetzt sind, wird hier
pro Skript ein Ausführungsbeispiel ergänzt.
