# Testbericht – Procurement Signals Dashboard

**Projekt:** Procurement Signals Dashboard  
**Dokumenttyp:** Testdurchführung und Auswertung  
**Version:** 1.0  
**Stand:** 06.08.2026  

## 1. Zweck des Testberichts

Dieser Bericht dokumentiert die Durchführung und Auswertung des im Dokument
`tests/TESTPLAN.md` definierten Testplans.

Untersucht wurden:

- die Berechnungs- und Entscheidungsqualität,
- die Klassifikation externer Nachrichten,
- die fachliche Korrektheit KI-generierter Verhandlungsargumente,
- die potenzielle Prozesswirkung,
- die UX und Usability,
- notwendige Iterationsschritte und Empfehlungen.

Die Testfälle wurden aus Benchmark Strang 1 und Strang 2 abgeleitet.

## 2. Zusammenfassung der Ergebnisse

| Testbereich | Ergebnis | Status |
|---|---:|---|
| Baseline-Berechnungen | 100 % korrekt | Pass |
| Buy-now-/Delay-Entscheidungen | 100 % korrekt | Pass |
| Nachrichtenklassifikation – Precision | 100 % | Pass |
| Nachrichtenklassifikation – Recall | 100 % | Pass |
| Nachrichtenklassifikation – F1-Score | 100 % | Pass |
| Exact Classification Accuracy | 100 % | Pass |
| Fachliche Bewertung der KI-Argumente | 5,0 von 5 | Pass |
| Numerische Genauigkeit der KI-Argumente | 100 % | Pass |
| Entscheidungsübereinstimmung der KI-Argumente | 100 % | Pass |
| Prozesswirkung | Nur mit simulierten Beispieldaten demonstriert | Eingeschränkt |
| UX und Usability | Nur mit simulierten Beispieldaten demonstriert | Eingeschränkt |

Die automatisierten Funktions- und Qualitätstests wurden erfolgreich abgeschlossen.

Die Prozess- und UX-Ergebnisse sind keine real erhobenen Nutzerdaten.
Sie zeigen ausschließlich, wie die spätere empirische Auswertung durchgeführt
und dokumentiert werden kann.

## 3. Testumgebung

- Repository: `procurement-signals-dashboard`
- Automatisierung: GitHub Actions
- Programmiersprache: Python
- Dashboard-Bereitstellung: GitHub Pages
- KI-Modell: `deepseek-v4-flash`
- Automatisierte Testskripte:
  - `tests/run_baseline_test.py`
  - `tests/run_classifier_test.py`
- Ergebnisordner: `tests/results/`

## 4. Verwendete Testdaten

| Datei | Verwendung |
|---|---|
| `tests/data/procurement_baseline.csv` | Fester Datensatz für Berechnungen und Entscheidungen |
| `tests/data/headlines_gold.csv` | Goldstandard für die Nachrichtenklassifikation |
| `tests/test_cases.csv` | Übersicht der fachlichen Testfälle |
| `tests/manual/argument_expert_evaluation.csv` | Fachliche Bewertung der Verhandlungsargumente |
| `tests/manual/examples/process_effect_test_example.xlsx` | Simuliertes Prozesswirkungsbeispiel |
| `tests/manual/examples/ux_usability_test_example.xlsx` | Simuliertes UX-Beispiel |

## 5. Ergebnisse des Baseline-Benchmarks

### 5.1 Geprüfte Materialien

- PP
- PA6
- Steel

### 5.2 Erwartete und erreichte Werte

| Material | Erwartete Verzögerungskosten | Erwartete Entscheidung | Testergebnis |
|---|---:|---|---|
| PP | 49.599,76 EUR | Buy now | Pass |
| PA6 | -178.060,52 EUR | Buy now | Pass |
| Steel | 246.229,80 EUR | Delay | Pass |

### 5.3 Kennzahlen

| Kennzahl | Zielwert | Erreicht | Status |
|---|---:|---:|---|
| Berechnungsgenauigkeit | 100 % | 100 % | Pass |
| Entscheidungsgenauigkeit | 100 % | 100 % | Pass |
| Numerische Toleranz | maximal 0,01 | eingehalten | Pass |
| Gesamtergebnis | Pass | Pass | Pass |

### 5.4 Bewertung

Die deterministischen Berechnungen liefern für alle drei Materialien die
erwarteten Ergebnisse.

Auch die daraus abgeleiteten Handlungsempfehlungen stimmen vollständig mit dem
definierten Goldstandard überein.

Nachweise:

- `tests/results/baseline_test_results.csv`
- `tests/results/baseline_metrics.json`
- GitHub-Actions-Protokoll des Workflows `Baseline Benchmark`

## 6. Ergebnisse der Nachrichtenklassifikation

### 6.1 Testaufbau

Der Goldstandard enthielt insgesamt 20 Schlagzeilen:

- 15 relevante Nachrichten,
- 5 irrelevante Nachrichten.

Die relevanten Nachrichten deckten folgende Risikobereiche ab:

- Lohnkosten,
- Red-Sea- beziehungsweise Transportstörungen,
- geopolitische Lieferkettenrisiken.

### 6.2 Ergebnisse

| Kennzahl | Zielwert | Erreicht | Status |
|---|---:|---:|---|
| Precision | mindestens 90 % | 100 % | Pass |
| Recall | mindestens 90 % | 100 % | Pass |
| F1-Score | mindestens 90 % | 100 % | Pass |
| Exact Classification Accuracy | mindestens 90 % | 100 % | Pass |

Das Modell klassifizierte 15 von 20 Meldungen als relevant.
Dies entsprach exakt dem Goldstandard.

### 6.3 Bewertung

Der Klassifikationstest wurde vollständig bestanden.

Die Ergebnisse zeigen, dass das Modell die fest definierten Mockup-Fälle korrekt
zwischen relevanten und irrelevanten Nachrichten unterscheiden konnte.

Die Aussagekraft ist jedoch begrenzt, weil:

- der Datensatz nur 20 Schlagzeilen enthält,
- die Meldungen synthetisch und relativ eindeutig formuliert sind,
- mehrdeutige, widersprüchliche oder sprachlich komplexe Fälle nur begrenzt
  enthalten sind.

Nachweise:

- `tests/results/headlines_test_results.csv`
- `tests/results/headlines_metrics.json`
- GitHub-Actions-Protokoll des Workflows `Classifier Benchmark`

## 7. Fachliche Korrektheit der KI-Verhandlungsargumente

### 7.1 Bewertete Argumente

Es wurden drei KI-generierte Verhandlungsargumente bewertet:

- PP
- PA6
- Steel

### 7.2 Bewertungskriterien

Jedes Argument wurde anhand von fünf binären Kriterien beurteilt:

1. korrektes Material,
2. korrektes Makrorisiko,
3. Übereinstimmung mit der Handlungsempfehlung,
4. korrekte Zahlen,
5. konkrete und nutzbare Handlung.

### 7.3 Ergebnisse

| Kennzahl | Zielwert | Erreicht | Status |
|---|---:|---:|---|
| Durchschnittlicher Expertenwert | mindestens 4,0 von 5 | 5,0 von 5 | Pass |
| Bestehensquote | mindestens 90 % | 100 % | Pass |
| Numerische Genauigkeit | 100 % | 100 % | Pass |
| Entscheidungsübereinstimmung | 100 % | 100 % | Pass |

Die Bewertung wurde von zwei Reviewern dokumentiert.

### 7.4 Bewertung

Alle drei Argumente erfüllten die definierten fachlichen Kriterien.

Besonders relevant ist, dass:

- die richtigen Materialien verwendet wurden,
- die korrekten Makrorisiken genannt wurden,
- die Texte mit den Buy-now-/Delay-Entscheidungen übereinstimmten,
- die Kostenwerte korrekt übernommen wurden,
- eine konkrete Handlung formuliert wurde.

Die Aussagekraft ist trotzdem eingeschränkt, weil nur drei Argumente bewertet
wurden. Für eine produktive Nutzung sollte die Stichprobe erweitert werden.

Nachweise:

- `tests/manual/argument_expert_evaluation.csv`
- `tests/results/argument_expert_metrics.json`

## 8. Prozesswirkung

### 8.1 Testziel

Verglichen werden sollten:

- eine manuelle Auswertung der Beschaffungsdaten,
- die Nutzung des Dashboards.

Gemessen wurden:

- Bearbeitungszeit,
- Vollständigkeit,
- Empfehlungsgenauigkeit,
- Risikogenauigkeit,
- Kostengenauigkeit,
- Entscheidungssicherheit.

### 8.2 Demonstration mit simulierten Beispieldaten

Die Beispieldatei zeigt folgende simulierte Ergebnisse:

| Kennzahl | Manuell | Dashboard |
|---|---:|---:|
| Durchschnittliche Bearbeitungszeit | 185,0 Sekunden | 62,4 Sekunden |
| Vollständigkeit | 64,4 % | 100 % |
| Empfehlungsgenauigkeit | 80,0 % | 100 % |
| Risikogenauigkeit | 60,0 % | 100 % |
| Kostengenauigkeit | 53,3 % | 100 % |
| Entscheidungssicherheit | 2,6 von 5 | 4,8 von 5 |

Simulierte Zeitersparnis:

**66,3 %**

### 8.3 Status

Die simulierten Werte würden die definierten Zielwerte erfüllen.

Sie dürfen jedoch nicht als realer Nachweis einer Prozessverbesserung verwendet
werden, weil keine tatsächlichen Testpersonen gemessen wurden.

Status:

**Methodik demonstriert, empirischer Nachweis noch offen.**

Nachweis:

- `tests/manual/examples/process_effect_test_example.xlsx`

## 9. UX- und Usability-Test

### 9.1 Testaufgaben

Die Teilnehmenden sollten:

1. PP-Empfehlung und Verzögerungskosten finden,
2. PA6-Risiko und Handlungsempfehlung finden,
3. Steel-Empfehlung und nächste Aktion finden.

### 9.2 Demonstration mit simulierten Beispieldaten

| Kennzahl | Simulierter Wert | Zielwert |
|---|---:|---:|
| Aufgabenquote | 100 % | mindestens 90 % |
| Durchschnittlicher UX-Wert | 4,50 von 5 | mindestens 4,0 |
| Kritische Fehler | 0 | 0 |
| Durchschnittliche Bearbeitungszeit | 70,2 Sekunden | Dokumentation |
| Informationen leicht gefunden | 4,60 von 5 | mindestens 4,0 |
| Entscheidungen klar | 4,80 von 5 | mindestens 4,0 |
| Argumente nützlich | 4,40 von 5 | mindestens 4,0 |
| Wiederverwendung | 4,80 von 5 | mindestens 4,0 |

### 9.3 Status

Die simulierten Werte würden alle definierten UX-Zielwerte erfüllen.

Sie stellen jedoch keine echte Nutzerstudie dar.

Status:

**Methodik demonstriert, empirischer Nachweis noch offen.**

Nachweis:

- `tests/manual/examples/ux_usability_test_example.xlsx`

## 10. Testfälle und Status

| ID | Testfall | Status |
|---|---|---|
| T01 | Verzögerungskosten PP | Pass |
| T02 | Verzögerungskosten PA6 | Pass |
| T03 | Verzögerungskosten Steel | Pass |
| T04 | Entscheidung PP | Pass |
| T05 | Entscheidung PA6 | Pass |
| T06 | Entscheidung Steel | Pass |
| T07 | KI-Argument PP | Pass |
| T08 | KI-Argument PA6 | Pass |
| T09 | KI-Argument Steel | Pass |
| T10 | Dashboard-Konsistenz | Pass |
| T11 | Nachrichtenklassifikation | Pass |
| T12 | Prozesswirkung | Nur beispielhaft demonstriert |
| T13 | UX und Usability | Nur beispielhaft demonstriert |

### 10.1 Dashboard-Konsistenzprüfung

Die im Dashboard dargestellten Entscheidungen, Verzögerungskosten,
Makrorisiken und KI-generierten Verhandlungsargumente wurden mit der
aktuellen Datei `signals.json` verglichen. Für PP, PA6 und Steel wurden
keine Abweichungen festgestellt. Der Testfall T10 wurde bestanden.
## 11. Durchgeführte Iterationsschritte

Während der technischen Umsetzung und Testvorbereitung wurden folgende
Verbesserungen vorgenommen:

### 11.1 Robustere Nachrichtenklassifikation

Die Verarbeitung der Modellantwort wurde stabiler gestaltet.

Umgesetzte Maßnahmen:

- robustere JSON-Auswertung,
- klarere Modellanweisungen,
- Behandlung unerwarteter Antwortformate,
- Abschaltung zusätzlicher Reasoning-Ausgaben für strukturierte Ergebnisse.

### 11.2 Stabilere Generierung der Verhandlungsargumente

Umgesetzte Maßnahmen:

- strukturiertere Prompts,
- Abschaltung nicht benötigter Thinking-Ausgaben,
- Wiederholungsversuche bei fehlerhaften Modellantworten,
- Prüfung der verwendeten Material- und Kostendaten.

### 11.3 Stabilere GitHub-Actions-Ausführung

Umgesetzte Maßnahmen:

- Aktualisierung verwendeter GitHub-Actions-Versionen,
- definierte Python-Umgebung,
- Concurrency-Steuerung,
- sichereres Aktualisieren des Repository-Zustands vor dem Push.

### 11.4 Verbesserte Testnachvollziehbarkeit

Umgesetzte Maßnahmen:

- Trennung von Produktions- und Testdaten,
- fester Baseline-Datensatz,
- Goldstandard für Nachrichten,
- maschinenlesbare Ergebnisdateien,
- klare Kennzeichnung simulierter Nutzer- und Prozessdaten.

## 12. Festgestellte Einschränkungen

### 12.1 Begrenzte Größe des Klassifikationsdatensatzes

20 Schlagzeilen reichen für einen ersten Funktionstest, aber nicht für eine
belastbare produktive Qualitätsaussage.

### 12.2 Synthetische und eindeutige Testfälle

Die verwendeten Meldungen sind überwiegend klar formuliert.
Reale Nachrichten können mehrdeutig, unvollständig oder widersprüchlich sein.

### 12.3 Kleine Argumentstichprobe

Die fachliche Bewertung umfasst nur drei Verhandlungsargumente.

### 12.4 Keine reale Prozessstudie

Die Prozesswirkungswerte wurden simuliert.
Eine statistisch belastbare Aussage zur Zeitersparnis ist deshalb noch nicht
möglich.

### 12.5 Keine reale UX-Studie

Die UX-Werte wurden simuliert.
Sie dürfen nicht als echte Benutzerbewertung ausgewiesen werden.

### 12.6 Abhängigkeit von externen Modellantworten

KI-Ausgaben können sich trotz identischer Eingaben verändern.
Deshalb sind Wiederholungs- und Regressionstests erforderlich.

## 13. Empfehlungen

### Priorität 1: Reale Nutzer- und Prozessdaten erheben

Der Prozesswirkungs- und UX-Test sollte mit mindestens drei, idealerweise fünf
unabhängigen Personen durchgeführt werden.

Die simulierten Werte müssen anschließend durch reale Messwerte ersetzt werden.

### Priorität 2: Goldstandard erweitern

Der Nachrichten-Goldstandard sollte auf mindestens 50 bis 100 Meldungen
erweitert werden.

Zusätzlich sollten aufgenommen werden:

- mehrdeutige Meldungen,
- Meldungen mit mehreren Risikotreibern,
- sprachlich unklare Überschriften,
- ähnliche, aber irrelevante Meldungen,
- Grenzfälle mit niedriger Relevanz.

### Priorität 3: KI-Argumente mehrfach bewerten

Für jedes Material sollten mehrere Modellläufe durchgeführt werden.

Empfohlen werden:

- mindestens drei Ausgaben pro Material,
- mindestens zwei unabhängige Reviewer,
- Dokumentation von Abweichungen zwischen den Reviewern.

### Priorität 4: Dashboard-Konsistenz automatisieren

Die Werte in `signals.json` und im Dashboard sollten automatisiert verglichen
werden, um Darstellungs- oder Übertragungsfehler frühzeitig zu erkennen.

### Priorität 5: Regressionstests bei jeder Änderung

Die beiden automatisierten Benchmarks sollten nach jeder Änderung an:

- Berechnungslogik,
- Prompts,
- Modell,
- Datenformat,
- Dashboard-Darstellung

erneut ausgeführt werden.

## 14. Gesamtbewertung

Die Kernfunktionen des Prototyps wurden erfolgreich getestet.

Besonders positiv sind:

- vollständig korrekte Baseline-Berechnungen,
- vollständig korrekte Buy-now-/Delay-Entscheidungen,
- sehr gute Ergebnisse auf dem festen Klassifikations-Goldstandard,
- fachlich korrekte KI-Verhandlungsargumente.

Die derzeit stärkste Einschränkung ist das Fehlen real erhobener Prozess- und
UX-Daten.

Daher lautet die Gesamtbewertung:

**Technischer und fachlicher Prototypentest: bestanden.**

**Empirische Prozess- und UX-Validierung: noch offen.**

## 15. Abschlussstatus

| Bereich | Abschlussstatus |
|---|---|
| Testplanung | Abgeschlossen |
| Mockup- und Goldstandard-Daten | Abgeschlossen |
| Automatisierte Baseline-Tests | Abgeschlossen |
| Automatisierte Klassifikationstests | Abgeschlossen |
| Fachliche Argumentbewertung | Abgeschlossen |
| Prozesswirkungsmethodik | Abgeschlossen |
| Reale Prozesswirkungserhebung | Offen |
| UX-Testmethodik | Abgeschlossen |
| Reale UX-Erhebung | Offen |
| Empfehlungen und Iterationen | Dokumentiert |

