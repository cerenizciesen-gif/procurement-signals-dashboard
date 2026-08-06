# Tests – Procurement Signals Dashboard

Dieses Verzeichnis enthält den vollständigen Testplan, die Testdaten,
automatisierte Testskripte, manuelle Bewertungen und Ergebnisdateien für das
Procurement Signals Dashboard.

## 1. Zentrale Dokumente

| Datei | Beschreibung |
|---|---|
| [TESTPLAN.md](TESTPLAN.md) | Testziele, Testfälle, Mockup-Daten, Erwartungswerte und Akzeptanzkriterien |
| [TEST_REPORT.md](TEST_REPORT.md) | Testdurchführung, Ergebnisse, Einschränkungen, Iterationen und Empfehlungen |
| [benchmark_strang_1_2.md](benchmark_strang_1_2.md) | Ableitung der Testanforderungen aus Benchmark Strang 1 und Strang 2 |
| [test_cases.csv](test_cases.csv) | Übersicht der definierten Testfälle T01 bis T13 |

## 2. Testdaten

### Interne Beschaffungsdaten

- [data/procurement_baseline.csv](data/procurement_baseline.csv)

Fester Mockup-Datensatz für:

- Jahresausgaben,
- monatliche Preisentwicklung,
- Verzögerungskosten,
- Buy-now-/Delay-Entscheidungen.

### Nachrichten-Goldstandard

- [data/headlines_gold.csv](data/headlines_gold.csv)

Enthält relevante und irrelevante Schlagzeilen für die Messung von:

- Precision,
- Recall,
- F1-Score,
- Exact Classification Accuracy.

## 3. Automatisierte Tests

### Baseline Benchmark

- [run_baseline_test.py](run_baseline_test.py)

Geprüft werden:

- Verzögerungskosten für PP, PA6 und Steel,
- Buy-now-/Delay-Entscheidungen,
- Übereinstimmung mit dem Goldstandard.

Ergebnisdateien:

- [results/baseline_test_results.csv](results/baseline_test_results.csv)
- [results/baseline_metrics.json](results/baseline_metrics.json)

### Classifier Benchmark

- [run_classifier_test.py](run_classifier_test.py)

Geprüft werden:

- Erkennung relevanter Nachrichten,
- Erkennung irrelevanter Nachrichten,
- Material- und Risikozuordnung,
- Precision, Recall, F1 und Accuracy.

Ergebnisdateien:

- [results/headlines_test_results.csv](results/headlines_test_results.csv)
- [results/headlines_metrics.json](results/headlines_metrics.json)

## 4. Fachliche Bewertung der KI-Argumente

Bewertungsdatei:

- [manual/argument_expert_evaluation.csv](manual/argument_expert_evaluation.csv)

Zusammenfassung:

- [results/argument_expert_metrics.json](results/argument_expert_metrics.json)

Bewertungskriterien:

1. korrektes Material,
2. korrektes Makrorisiko,
3. Übereinstimmung mit der Handlungsempfehlung,
4. korrekte Zahlen,
5. konkrete und nutzbare nächste Handlung.

## 5. Prozesswirkung und UX

Beispieldateien:

- [manual/examples/process_effect_test_example.xlsx](manual/examples/process_effect_test_example.xlsx)
- [manual/examples/ux_usability_test_example.xlsx](manual/examples/ux_usability_test_example.xlsx)

> **Wichtiger Hinweis:** Diese beiden Excel-Dateien enthalten simulierte
> Beispieldaten. Sie demonstrieren das Testverfahren und dürfen nicht als
> tatsächlich erhobene Ergebnisse realer Testpersonen ausgewiesen werden.

Der technische und fachliche Prototypentest wurde durchgeführt.

Die empirische Prozess- und UX-Validierung mit realen Testpersonen ist noch
offen.

## 6. Aktueller Teststatus

| Testbereich | Status |
|---|---|
| Baseline-Berechnungen | Pass |
| Buy-now-/Delay-Entscheidungen | Pass |
| Nachrichtenklassifikation | Pass |
| Fachliche Bewertung der KI-Argumente | Pass |
| Prozesswirkungsmethodik | Dokumentiert |
| Reale Prozesswirkungserhebung | Offen |
| UX-Testmethodik | Dokumentiert |
| Reale UX-Erhebung | Offen |

## 7. Ausführung in GitHub Actions

Im Bereich **Actions** werden die folgenden Workflows ausgeführt:

- `Baseline Benchmark`
- `Classifier Benchmark`

Nach erfolgreicher Ausführung werden die Ergebnisdateien unter `tests/results/`
aktualisiert.

## 8. Empfohlene Lesereihenfolge

1. [benchmark_strang_1_2.md](benchmark_strang_1_2.md)
2. [TESTPLAN.md](TESTPLAN.md)
3. [test_cases.csv](test_cases.csv)
4. Dateien unter `data/`
5. Automatisierte Testskripte
6. Dateien unter `results/`
7. [TEST_REPORT.md](TEST_REPORT.md)

## 9. Gesamtbewertung

**Technischer und fachlicher Prototypentest: bestanden.**

**Empirische Prozess- und UX-Validierung: noch offen.**
