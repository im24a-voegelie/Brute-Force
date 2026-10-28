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
result = run_poly_alphabet_attack(
    store, username, login_fn=protected_login
)
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
