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
[Plan.md](Plan.md).

## Einfacher Angriff (2.1)

Probiert alle Kombinationen aus einem einzigen Zeichensatz (nur Ziffern,
nur Klein- oder nur Grossbuchstaben) bis zu einer Maximallänge durch. Die
Vorgabe erlaubt bis zu 10 Zeichen; der Demo-Default ist bewusst kleiner
(4 Zeichen), damit ein Lauf ohne Argumente schnell fertig ist.

```bash
python -m attacks.mono_alphabet_attack
python -m attacks.mono_alphabet_attack --charset digits --max-length 3
```

## Mittlere Angriffe (2.2)

Beide Skripte verwenden `common/demo_target.py` und greifen damit denselben
simulierten In-Memory-Account (`demo_user`) wie die anderen Angriffe an. Sie
verbinden sich nicht mit einem Netzwerkdienst. Das Passwort `hans` ist für
die Demo absichtlich kurz gehalten.

```bash
python -m attacks.dictionary_attack
python -m attacks.poly_alphabet_attack
```

Der Dictionary-Angriff prüft die Beispiel-Wortliste in `data/wordlist.txt`
sowie Schreibweisen und Varianten mit dem fiktiven Namen/Geburtsjahr aus
`data/victim_profile.json`. Der Poly-Alphabet-Angriff kombiniert Gross- und
Kleinbuchstaben, Ziffern sowie sichtbare ASCII-Satzzeichen (ohne Leerzeichen
und Steuerzeichen). Beide Skripte zeigen neben dem Treffer und der Anzahl
geprüfter Kandidaten auch die gemessene Suchzeit in Sekunden an.

## Komplexe Angriffe (2.3)

Der Rainbow-Table-Angriff arbeitet offline: `scripts/build_rainbow_table.py`
berechnet einmalig alle Hashes für einen Zeichensatz/eine Maximallänge und
speichert sie als Hash-Plain-Lookup-Tabelle in `data/rainbow_table.csv`
(generiert, nicht versioniert - siehe `.gitignore`). Der eigentliche Angriff
berechnet danach keine Hashes mehr selbst, sondern schlägt nur noch in
dieser Datei nach.

```bash
python -m scripts.build_rainbow_table
python -m attacks.rainbow_table_attack
```

Der parallelisierte Angriff teilt einen Zeichensatz in gleich grosse
Wertebereiche auf: Jeder Prozess bekommt eine Teilmenge der möglichen
ersten Zeichen und durchsucht nur Passwörter, die damit beginnen. Sobald
ein Prozess das Passwort findet, brechen die anderen ab.

```bash
python -m attacks.parallel_bruteforce_attack
python -m attacks.parallel_bruteforce_attack --charset lower digits --processes 8
```

Beide Angriffe vergleichen Hashes direkt und rufen `AccountStore.login()`
nicht auf - Verteidigungen, die den Login-Aufruf umschliessen (siehe unten),
haben hier deshalb keine Wirkung.

## Einfache Verteidigungen (3.1)

Beide Verteidigungen umschliessen `AccountStore.login()` und verzögern
jeden Versuch. Linear wartet nach jedem Versuch dieselbe Zeit (0.5-2
Sekunden gemäss Vorgabe); progressiv wartet nach jedem weiteren
Fehlversuch länger (10 Sekunden, dann 1 Minute, ...).

```bash
python -m defenses.linear_delay
python -m defenses.progressive_delay
```

Die Demo-Defaults sind kleiner als die Vorgabe gewählt (z.B. 1 Sekunde
Verzögerung statt bis zu 2, bzw. nur ein simulierter Fehlversuch bei
progressive_delay), damit die Demo nicht unnötig lange läuft. Mit `--delay`
bzw. `--base-delay`/`--multiplier` lassen sich die echten Vorgabewerte
einstellen.

## Mittlere Verteidigungen (3.2)

Beide Verteidigungen umschliessen `AccountStore.login()` und gelten pro
Benutzername. Counter-Limit sperrt einen Benutzer nach drei falschen
Passwörtern für den Rest des Programmablaufs. Captcha verlangt nach drei
Fehlversuchen vor jedem weiteren Login eine einfache Rechenaufgabe.

```bash
python -m defenses.counter_limit
python -m defenses.captcha_challenge
```

Die Captcha-Demo ist interaktiv: Nach den drei absichtlichen Fehlversuchen
musst du die angezeigte Summe eingeben. Die Wrapper lassen sich auch direkt
in Python verwenden, indem du `apply_counter_limit(store.login)` oder
`apply_captcha_challenge(store.login)` anstelle von `store.login` aufrufst.
Für die mittleren Angriffe kann der geschützte Login direkt übergeben werden:

```python
protected_login = apply_counter_limit(store.login)
result = run_poly_alphabet_attack(store, username, login_fn=protected_login)
```

## Komplexe Verteidigung (3.3)

Die Logging-Verteidigung protokolliert fehlgeschlagene Logins mit UTC-Zeit und
Benutzername in `logs/login_attempts.csv`. Bei mindestens drei Fehlversuchen
desselben Benutzers innerhalb von 60 Sekunden wird ein Alarm ausgegeben und
als Ereignis protokolliert. Diese Variante meldet auffällige Aktivität, sie
sperrt den Benutzer nicht.

```powershell
python -m defenses.logging_defense
```

Zum Testen wird dreimal absichtlich ein falsches Passwort gesendet. Danach
zeigt die Demo, dass der Alarm ausgelöst wurde und das richtige Passwort
trotzdem akzeptiert wird. Eine eigene Protokolldatei kannst du angeben:

```powershell
python -m defenses.logging_defense --log-file logs\logging_test.csv
```

## Demo: Angriff + Verteidigung kombinieren

`demo/run_demo.py` wählt einen Angriff und optional eine Verteidigung per
CLI aus und zeigt Erfolg/Fehlschlag sowie die Laufzeit:

```bash
python -m demo.run_demo --attack mono --defense linear_delay
python -m demo.run_demo --attack dictionary --defense counter_limit
python -m demo.run_demo --attack rainbow_table --defense linear_delay
```

Nicht jede Kombination verhält sich gleich:

- `counter_limit` und `captcha_challenge` geben nach dem Schwellwert sofort
  `False` zurück, ohne den echten Login erneut zu prüfen. Deshalb bleiben
  sie auch mit einem grossen Suchraum (Mono-/Poly-Alphabet) schnell - der
  Angriff läuft durch, meldet aber "nicht gefunden", weil der Account
  gesperrt ist.
- `linear_delay` und `progressive_delay` warten bei jedem Versuch wirklich.
  Bei zehntausenden Versuchen wäre das sehr langsam - das ist der Sinn
  dieser Verteidigungen. `progressive_delay` wächst exponentiell und bricht
  die Demo deshalb automatisch nach wenigen Versuchen ab
  (einstellbar über `--demo-max-attempts`).
- Der Rainbow-Table- und der parallelisierte Angriff rufen `login()` nicht
  auf; die Demo weist in diesem Fall ausdrücklich darauf hin, dass die
  gewählte Verteidigung keine Wirkung hat, statt es stillschweigend zu
  ignorieren.

Alle Angriffs- und Verteidigungs-Parameter zeigt:

```bash
python -m demo.run_demo --help
```

## Aufteilung

| Teil | Wer |
| --- | --- |
| Planung | Gemeinsam |
| Setup | Ennio |
| Einfacher Angriff (2.1) | Ennio |
| Mittlere Angriffe (2.2) | Dario |
| Komplexe Angriffe (2.3) | Ennio |
| Einfache Verteidigungen (3.1) | Dario |
| Mittlere Verteidigungen (3.2) | Ennio |
| Komplexe Verteidigung (3.3) | Dario |
| Linting & README-Review | Gemeinsam |
