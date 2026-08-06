# Testplan – Procurement Signals Dashboard

**Projekt:** Procurement Signals Dashboard  
**Dokumenttyp:** Testplan mit Mockup-Daten  
**Version:** 1.0  
**Stand:** 06.08.2026

## 1. Ziel des Testplans

Dieser Testplan beschreibt die strukturierte Prüfung des Procurement Signals Dashboards.

Geprüft werden:

- die korrekte Verarbeitung interner Beschaffungsdaten,
- die Klassifikation externer Nachrichtensignale,
- die fachliche Qualität KI-generierter Verhandlungsargumente,
- die Wirkung des Dashboards auf Bearbeitungszeit und Vollständigkeit,
- die Benutzerfreundlichkeit und Verständlichkeit der Oberfläche.

Die Testfälle wurden aus den Anforderungen der Benchmark-Stränge 1 und 2 abgeleitet.

## 2. Bezug zu Benchmark Strang 1 und Strang 2

### Strang 1: Interne Beschaffungsdaten

Strang 1 betrachtet die korrekte und effiziente Auswertung interner Preis-, Mengen- und Kostendaten.

Daraus wurden folgende Testbereiche abgeleitet:

- Berechnungsgenauigkeit,
- korrekte Buy-now-/Delay-Entscheidungen,
- Vollständigkeit der Ergebnisse,
- Bearbeitungszeit im Vergleich zur manuellen CSV-Auswertung.

### Strang 2: Externe Marktsignale und KI-Unterstützung

Strang 2 betrachtet die Erkennung relevanter externer Nachrichten sowie deren Überführung in Einkaufsrisiken und Verhandlungsargumente.

Daraus wurden folgende Testbereiche abgeleitet:

- Nachrichtenklassifikation,
- Precision, Recall und F1-Score,
- Material- und Risikozuordnung,
- fachliche Korrektheit der KI-Argumente,
- Verständlichkeit und Nutzbarkeit des Dashboards.

Die ausführliche Herleitung ist in `tests/benchmark_strang_1_2.md` dokumentiert.

## 3. Testgegenstand

Getestet werden folgende Bestandteile:

1. Verarbeitung der Datei `procurement_baseline.csv`
2. Berechnung von Jahresausgaben, Preisentwicklung und Verzögerungskosten
3. Ableitung der Handlungsempfehlung `Buy now` oder `Delay`
4. Klassifikation externer Nachrichten
5. Zuordnung von Material, Risikotreiber und Relevanz
6. Generierung von Verhandlungsargumenten
7. Darstellung der Ergebnisse im Dashboard
8. Prozesswirkung gegenüber einer manuellen Auswertung
9. UX und Usability

## 4. Testumgebung

- GitHub Repository: `procurement-signals-dashboard`
- Automatisierung: GitHub Actions
- Programmiersprache: Python
- Dashboard: GitHub Pages
- KI-Modell: `deepseek-v4-flash`
- Testdaten: feste Mockup- und Goldstandard-Datensätze
- Ergebnisablage: `tests/results/`

Die automatisierten Tests müssen mit demselben Commit ausgeführt werden, der auch für das Dashboard verwendet wird.

## 5. Testdaten und Dateien

| Datei | Zweck |
|---|---|
| `tests/data/procurement_baseline.csv` | Fester Mockup-Datensatz für Berechnungs- und Entscheidungstests |
| `tests/data/headlines_gold.csv` | Goldstandard für relevante und irrelevante Nachrichten |
| `tests/test_cases.csv` | Übersicht der definierten fachlichen Testfälle |
| `tests/run_baseline_test.py` | Automatisierter Baseline-Test |
| `tests/run_classifier_test.py` | Automatisierter Klassifikationstest |
| `tests/manual/argument_expert_evaluation.csv` | Manuelle Bewertung der KI-Argumente |
| `tests/manual/examples/process_effect_test_example.xlsx` | Simuliertes Beispiel für den Prozesswirkungstest |
| `tests/manual/examples/ux_usability_test_example.xlsx` | Simuliertes Beispiel für den UX-Test |

> **Wichtiger Hinweis:** Die Dateien im Ordner `tests/manual/examples/` enthalten simulierte Beispieldaten. Sie dienen zur Demonstration des Testverfahrens und dürfen nicht als tatsächlich erhobene Teilnehmerdaten ausgewiesen werden.

## 6. Erwartungswerte des Baseline-Datensatzes

| Material | Jahresausgaben | Monatlicher Trend | Verzögerungskosten | Entscheidung | Makrorisiko |
|---|---:|---:|---:|---|---|
| PP | 702.000,00 EUR | 1,18 % | 49.599,76 EUR | Buy now | Turkey minimum wage increase |
| PA6 | 3.432.000,00 EUR | -0,86 % | -178.060,52 EUR | Buy now | Red Sea shipping disruption |
| Steel | 3.925.000,00 EUR | 1,05 % | 246.229,80 EUR | Delay | Geopolitical supply disruption |

Für numerische Vergleiche gilt eine Toleranz von `0,01`.

## 7. Definierte Testfälle

| ID | Testbereich | Eingabe | Erwartetes Ergebnis | Testart |
|---|---|---|---|---|
| T01 | Verzögerungskosten PP | PP-Baseline-Daten | 49.599,76 EUR | Automatisiert |
| T02 | Verzögerungskosten PA6 | PA6-Baseline-Daten | -178.060,52 EUR | Automatisiert |
| T03 | Verzögerungskosten Steel | Steel-Baseline-Daten | 246.229,80 EUR | Automatisiert |
| T04 | Entscheidung PP | PP-Daten und Makrorisiko | Buy now | Automatisiert |
| T05 | Entscheidung PA6 | PA6-Daten und Makrorisiko | Buy now | Automatisiert |
| T06 | Entscheidung Steel | Steel-Daten und Makrorisiko | Delay | Automatisiert |
| T07 | KI-Argument PP | PP-Signal und Kostenwerte | Richtiges Material, Risiko, Entscheidung und Zahlen | Manuell |
| T08 | KI-Argument PA6 | PA6-Signal und Kostenwerte | Richtiges Material, Risiko, Entscheidung und Zahlen | Manuell |
| T09 | KI-Argument Steel | Steel-Signal und Kostenwerte | Richtiges Material, Risiko, Entscheidung und Zahlen | Manuell |
| T10 | Dashboard-Konsistenz | Generierte Signale | Dashboard und Ergebnisdateien zeigen dieselben Werte | Manuell |
| T11 | Nachrichtenklassifikation | 20 Goldstandard-Schlagzeilen | Relevante und irrelevante Meldungen korrekt erkennen | Automatisiert |
| T12 | Prozesswirkung | Manuelle CSV-Auswertung und Dashboard | Dashboard schneller und vollständiger | Nutzertest |
| T13 | UX und Usability | Drei Dashboard-Aufgaben | Hohe Erfolgsquote und verständliche Bedienung | Nutzertest |

## 8. Qualitätsmetriken

### 8.1 Nachrichtenklassifikation

Verwendete Kennzahlen:

- **Precision:** Anteil der korrekt als relevant erkannten Meldungen an allen als relevant klassifizierten Meldungen.
- **Recall:** Anteil der erkannten relevanten Meldungen an allen tatsächlich relevanten Meldungen.
- **F1-Score:** Harmonisches Mittel aus Precision und Recall.
- **Exact Classification Accuracy:** Anteil vollständig korrekter Klassifikationen.

Akzeptanzkriterien:

| Kennzahl | Zielwert |
|---|---:|
| Precision | mindestens 90 % |
| Recall | mindestens 90 % |
| F1-Score | mindestens 90 % |
| Exact Classification Accuracy | mindestens 90 % |

Der Goldstandard enthält 20 Schlagzeilen:

- 15 relevante Meldungen,
- 5 irrelevante Meldungen.

### 8.2 Berechnungs- und Entscheidungsqualität

| Kennzahl | Zielwert |
|---|---:|
| Berechnungsgenauigkeit | 100 % |
| Entscheidungsgenauigkeit | 100 % |
| Numerische Toleranz | maximal 0,01 |
| Material- und Risikozuordnung | 100 % |

### 8.3 Fachliche Korrektheit der KI-Argumente

Jedes Argument wird anhand von fünf binären Kriterien bewertet:

1. korrektes Material,
2. korrektes Makrorisiko,
3. Übereinstimmung mit der Handlungsempfehlung,
4. korrekte Zahlen,
5. konkrete und nutzbare nächste Handlung.

Bewertung:

- `1` = Kriterium erfüllt
- `0` = Kriterium nicht erfüllt

Akzeptanzkriterien:

| Kennzahl | Zielwert |
|---|---:|
| Gesamtpunktzahl pro Argument | mindestens 4 von 5 |
| Numerische Genauigkeit | 100 % |
| Entscheidungsübereinstimmung | 100 % |
| Bestehensquote | mindestens 90 % |

## 9. Prozesswirkung

Die Prozesswirkung wird durch einen Vergleich zwischen manueller CSV-Auswertung und Dashboard-Nutzung gemessen.

Aufgabe:

Für PP, PA6 und Steel werden jeweils folgende Angaben ermittelt:

- Handlungsempfehlung,
- Makrorisiko,
- Verzögerungskosten.

Erhobene Kennzahlen:

- Bearbeitungszeit in Sekunden,
- korrekte Empfehlungen,
- korrekte Risiken,
- korrekte Kostenwerte,
- Vollständigkeit,
- Entscheidungssicherheit.

Akzeptanzkriterien:

| Kennzahl | Zielwert |
|---|---:|
| Zeitersparnis durch das Dashboard | mindestens 30 % |
| Vollständigkeit Dashboard | mindestens 90 % |
| Empfehlungsgenauigkeit | mindestens 90 % |
| Risikogenauigkeit | mindestens 80 % |
| Kostengenauigkeit | 100 % |
| Entscheidungssicherheit Dashboard | mindestens 4 von 5 |

Für die finale empirische Auswertung sollen idealerweise fünf und mindestens drei unabhängige Testpersonen eingesetzt werden.

## 10. UX- und Usability-Test

Die Teilnehmenden bearbeiten drei Aufgaben:

1. PP-Empfehlung und Verzögerungskosten finden.
2. PA6-Makrorisiko und Handlungsempfehlung finden.
3. Steel-Handlungsempfehlung und nächste Aktion finden.

Anschließend werden acht Aussagen auf einer Skala von 1 bis 5 bewertet.

Bewertungsbereiche:

- Auffindbarkeit der Informationen,
- Verständlichkeit der Navigation,
- Klarheit der Entscheidungen,
- Übersichtlichkeit,
- Verständlichkeit der Risiken,
- Nutzen der Verhandlungsargumente,
- Vertrauen in die Ergebnisse,
- Bereitschaft zur Wiederverwendung.

Akzeptanzkriterien:

| Kennzahl | Zielwert |
|---|---:|
| Aufgabenquote | mindestens 90 % |
| Durchschnittlicher UX-Wert | mindestens 4,0 von 5 |
| Kritische Fehler | 0 |
| Q1 Informationen leicht gefunden | mindestens 4,0 |
| Q3 Entscheidungen klar | mindestens 4,0 |
| Q6 Argumente nützlich | mindestens 4,0 |
| Q8 Wiederverwendung | mindestens 4,0 |

## 11. Testdurchführung

Die Tests werden in folgender Reihenfolge durchgeführt:

1. Baseline-Datensatz und Erwartungswerte kontrollieren.
2. GitHub Action `Baseline Benchmark` ausführen.
3. Ergebnisdateien unter `tests/results/` prüfen.
4. GitHub Action `Classifier Benchmark` ausführen.
5. Precision, Recall, F1 und Accuracy prüfen.
6. KI-Argumente anhand des Bewertungsrasters beurteilen.
7. Prozesswirkungstest durchführen oder das Verfahren mit klar gekennzeichneten Beispieldaten demonstrieren.
8. UX-Test durchführen oder das Verfahren mit klar gekennzeichneten Beispieldaten demonstrieren.
9. Ergebnisse im Testbericht zusammenführen.
10. Abweichungen, Iterationsschritte und Empfehlungen dokumentieren.

## 12. Testnachweise

| Datei | Nachweis |
|---|---|
| `tests/results/baseline_test_results.csv` | Einzelergebnisse des Baseline-Tests |
| `tests/results/baseline_metrics.json` | Berechnungs- und Entscheidungsmetriken |
| `tests/results/headlines_test_results.csv` | Einzelergebnisse der Nachrichtenklassifikation |
| `tests/results/headlines_metrics.json` | Precision, Recall, F1 und Accuracy |
| `tests/manual/argument_expert_evaluation.csv` | Fachliche Bewertung der KI-Argumente |
| `tests/results/argument_expert_metrics.json` | Zusammenfassung der Argumentbewertung |
| GitHub-Actions-Protokolle | Technischer Ausführungsnachweis |
| Screenshots | Visueller Nachweis erfolgreicher Testläufe |

## 13. Fehlerbehandlung und Iteration

Ein Test gilt als fehlgeschlagen, wenn mindestens ein verpflichtendes Akzeptanzkriterium nicht erfüllt ist.

Bei einem Fehler wird folgender Ablauf verwendet:

1. Abweichung und betroffenen Testfall dokumentieren.
2. Ursache analysieren.
3. Code, Prompt, Entscheidungsregel oder Darstellung anpassen.
4. Betroffenen Test erneut ausführen.
5. Regressionstest für bereits bestandene Funktionen durchführen.
6. Ergebnis und Änderung im Testbericht dokumentieren.

Mögliche Iterationsmaßnahmen:

- Erweiterung des Goldstandard-Datensatzes um mehrdeutige Meldungen,
- Verbesserung des Klassifikationsprompts,
- Validierung und Rundung numerischer Modellantworten,
- klarere Erklärung der Buy-now-/Delay-Logik,
- bessere Hervorhebung von Risiken und Handlungsempfehlungen,
- Vereinfachung fachlicher Begriffe im Dashboard.

## 14. Ein- und Austrittskriterien

### Eintrittskriterien

Die Testdurchführung beginnt, wenn:

- alle Testdateien im Repository vorhanden sind,
- die GitHub Actions ausführbar sind,
- das Dashboard erreichbar ist,
- die Testdaten unverändert vorliegen,
- die erforderlichen API-Secrets konfiguriert sind.

### Austrittskriterien

Die Testphase gilt als abgeschlossen, wenn:

- alle automatisierten Tests ausgeführt wurden,
- alle verpflichtenden Metriken dokumentiert sind,
- die fachliche Bewertung abgeschlossen ist,
- Prozesswirkung und UX dokumentiert sind,
- fehlgeschlagene Tests erklärt oder korrigiert wurden,
- Empfehlungen und Iterationsschritte im Testbericht enthalten sind.

## 15. Rollen und Verantwortlichkeiten

| Rolle | Verantwortung |
|---|---|
| Testleitung | Planung, Durchführung und Dokumentation |
| Fachlicher Reviewer | Bewertung der KI-Verhandlungsargumente |
| Testpersonen | Durchführung von Prozess- und UX-Aufgaben |
| Entwicklungsteam | Fehleranalyse und Umsetzung von Verbesserungen |
| Projektteam | Freigabe von Testplan und Testbericht |

## 16. Ergebnisdokumentation

Die endgültigen Ergebnisse werden in folgender Datei dokumentiert:

`tests/TEST_REPORT.md`

Der Testbericht enthält:

- tatsächlich erreichte Metriken,
- Vergleich mit den Zielwerten,
- bestandene und fehlgeschlagene Testfälle,
- Einschränkungen der verwendeten Mockup-Daten,
- Iterationsschritte,
- Empfehlungen für die Weiterentwicklung.
