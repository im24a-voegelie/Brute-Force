# Brute-Force Showcase (M183 LB2) — Implementierungsplan

## Context

Dies ist ein Schulprojekt (M183, LU02f/LB2) mit dem Fokusthema BruteForce. Bewertet werden getrennt **Angriffe** (2.1–2.3) und **Verteidigungen** (3.1–3.3) in Python, ohne Frontend nötig (CLI genügt). Volle Basispunkte (4.1/4.2) gibt es für je eine Variante pro Stufe; Zusatzpunkte (4.3.2) gibt es für eine zweite Variante in Stufe 2 (mittel) und Stufe 3 (komplex) — sowohl bei Angriffen als auch Verteidigungen. Das Repo ist aktuell leer (nur README), das Projekt wird komplett neu aufgebaut.

Entscheidungen aus Rückfrage mit dem User:
- **Sprache:** Kommentare/Docstrings/README auf Deutsch (englische Fachbegriffe wo passender), Variablen-/Funktionsnamen auf Englisch.
- **Scope:** Basis + Bonus-Varianten (siehe unten), um 4.3.2 mitzunehmen.
- **Zielsystem:** Ein simuliertes lokales Login-System (gehashte User/Passwort-Paare + `login()`-Funktion), gegen das Online-Angriffe laufen und an das Verteidigungen angehängt werden. Rainbow-Table-Angriff arbeitet offline direkt gegen den gespeicherten Hash.
- **Tests:** Kein automatisiertes Test-Suite (pytest) — die Rubrik verlangt es nicht; Verifikation erfolgt durch manuelles Ausführen der Skripte/Demo. Spart Aufwand, birgt aber das Risiko, dass ein Bug erst beim Fachgespräch auffällt — darauf beim manuellen Testen jedes Schritts achten.
- **Team-Tracking:** Dieser Plan wird zusätzlich als `PLAN.md` im Repo-Root abgelegt (Checkliste mit Kästchen pro Schritt), damit beide Teammitglieder die Schritte gemeinsam abarbeiten und abhaken können. Das ist der allererste Implementierungsschritt.

### Abdeckung der Rubrik

| Stufe | Angriffe | Verteidigungen |
|---|---|---|
| 2.1 / 3.1 (einfach) | Mono-Alphabet (einzige gelistete Variante) | Linear Delay + Progressive Delay (beide, günstig umsetzbar) |
| 2.2 / 3.2 (mittel) | Dictionary **und** Poly-Alphabet (Bonus 4.3.2) | Counter-Limit **und** Captcha/User-Interaktion (Bonus 4.3.2) |
| 2.3 / 3.3 (komplex) | Rainbow-Table **und** Parallelisiert (Bonus 4.3.2) | Logging + Alarm (einzige gelistete Variante) |

Jeder Angriff/jede Verteidigung liegt in einer eigenen Datei (4.1.4 / 4.2.4).

## Architektur

```
Brute-Force/
├── README.md                      # Projektbeschreibung, Setup, wie man jedes Skript ausführt
├── PLAN.md                        # Diese Checkliste als abhakbare Team-Todo-Liste
├── requirements.txt
├── .gitignore
├── common/
│   ├── account_store.py           # simuliertes Login-System: User anlegen, login(username, password) -> bool
│   └── hashing.py                 # Hash-Hilfsfunktionen (SHA-256, bewusst ohne Salt für die Übung)
├── attacks/
│   ├── mono_alphabet_attack.py    # 2.1
│   ├── dictionary_attack.py       # 2.2a
│   ├── poly_alphabet_attack.py    # 2.2b
│   ├── rainbow_table_attack.py    # 2.3a
│   └── parallel_bruteforce_attack.py  # 2.3b
├── defenses/
│   ├── linear_delay.py            # 3.1a
│   ├── progressive_delay.py       # 3.1b
│   ├── counter_limit.py           # 3.2a
│   ├── captcha_challenge.py       # 3.2b
│   └── logging_defense.py         # 3.3
├── data/
│   ├── wordlist.txt               # Basis-Wordlist für Dictionary-Angriff
│   ├── victim_profile.json        # Beispiel-Personendaten (Email, Geburtsdatum, Name) für Permutationen
│   └── rainbow_table.csv          # von scripts/build_rainbow_table.py generiert
├── scripts/
│   └── build_rainbow_table.py     # generiert die Lookup-Datei für 2.3a
└── demo/
    └── run_demo.py                # CLI: Angriff + optionale Verteidigung wählen, Ergebnis/Zeit anzeigen
```

Verteidigungen werden als Wrapper um `account_store.login()` gebaut (z.B. Decorator/Kompositions-Funktion `apply_defenses(login_fn, [...])`), damit sie einzeln oder kombiniert vor jeden Angriff geschaltet werden können — das ist auch die Basis für `demo/run_demo.py`.

Passwortlängen werden gemäss Vorgabe bis 10 Zeichen unterstützt, aber die Demo-Standardwerte (z.B. 4–6 Zeichen) werden bewusst klein gehalten, damit Mono-/Poly-Alphabet- und Rainbow-Table-Angriffe in nützlicher Zeit durchlaufen — im README kurz begründen.

## Umsetzungsschritte

0. **PLAN.md anlegen**: Diese Schritte als abhakbare Checkliste (`- [ ] ...`) in `PLAN.md` im Repo-Root ablegen, damit beide Teammitglieder gemeinsam den Fortschritt sehen und Schritte abhaken können.
1. **Projekt-Setup**: Ordnerstruktur anlegen, `requirements.txt`, `.gitignore`, README-Grundgerüst (Beschreibung, Setup, Ausführung). Erster Commit.
2. **Gemeinsame Basis**: `common/hashing.py` und `common/account_store.py` — simulierte User-Datenbank mit gehashten Passwörtern, `login(username, password)` gibt True/False zurück.
3. **Einfacher Angriff (2.1)**: `attacks/mono_alphabet_attack.py` — probiert alle Kombinationen aus einem einzigen Zeichensatz (0-9 / a-z / A-Z) bis 10 Zeichen (mit sinnvoll kleinem Demo-Default) gegen `account_store.login()`.
4. **Mittlere Angriffe (2.2)**: `attacks/dictionary_attack.py` (nutzt `data/wordlist.txt` + Permutationen aus `data/victim_profile.json`) und `attacks/poly_alphabet_attack.py` (kombinierter Zeichensatz).
5. **Komplexe Angriffe (2.3)**: `scripts/build_rainbow_table.py` (erzeugt `data/rainbow_table.csv` für einen kleinen Passwortraum) + `attacks/rainbow_table_attack.py` (Lookup statt Berechnung); `attacks/parallel_bruteforce_attack.py` (multiprocessing, Keyspace pro Prozess aufgeteilt).
6. **Einfache Verteidigungen (3.1)**: `defenses/linear_delay.py`, `defenses/progressive_delay.py`.
7. **Mittlere Verteidigungen (3.2)**: `defenses/counter_limit.py` (Sperre nach N Fehlversuchen), `defenses/captcha_challenge.py` (einfache CLI-Challenge nach Schwellwert).
8. **Komplexe Verteidigung (3.3)**: `defenses/logging_defense.py` — protokolliert Fehlversuche mit Zeitstempel, löst Alarm-Meldung aus, wenn Schwellwert in Zeitfenster überschritten wird.
9. **Demo-Harness**: `demo/run_demo.py` — Angriff + Verteidigungskombination per CLI wählbar, zeigt Erfolg/Fehlschlag und Laufzeit (Grundlage für Fachgespräch).
10. **Code-Qualität & Doku**: PEP8/Linting (z.B. `ruff` oder `flake8`), Docstrings, README finalisieren (Architektur, Ausführungsbeispiele pro Skript) — vermeidet Malus 4.4.1.
11. **Fachgespräch-Vorbereitung**: Sicherstellen, dass beide Teammitglieder jedes Skript erklären können; Commits über beide Teammitglieder verteilt (vermeidet Malus 4.4.2/4.4.3).

## Verifikation

Kein automatisiertes Test-Suite (Entscheidung des Users) — stattdessen nach jedem Schritt manuell verifizieren:
- Jedes Angriffsskript manuell ausführen (`python -m attacks.mono_alphabet_attack ...` etc.) und Erfolg gegen den simulierten Account-Store zeigen.
- `demo/run_demo.py` mit und ohne aktive Verteidigung laufen lassen, um sichtbaren Effekt (Verzögerung/Sperre/Captcha/Logeintrag) zu demonstrieren.
- `data/rainbow_table.csv` neu generieren und prüfen, dass der Lookup-Angriff das korrekte Passwort ohne erneute Hash-Berechnung findet.
