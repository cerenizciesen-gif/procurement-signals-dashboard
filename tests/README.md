# Test Documentation – Procurement Signals Dashboard

Dieses Verzeichnis enthält die vollständige Testdokumentation des Prototyps.

## Zentrale Dokumente

- [TESTPLAN.md](TESTPLAN.md) – Testfälle, Mockup-Daten, Erwartungswerte und Akzeptanzkriterien
- [TEST_REPORT.md](TEST_REPORT.md) – Testdurchführung, Ergebnisse, Iterationen und Empfehlungen
- [benchmark_strang_1_2.md](benchmark_strang_1_2.md) – Ableitung aus Benchmark Strang 1 und Strang 2
- [test_cases.csv](test_cases.csv) – Definierte Testfälle

## Testdaten

- `data/procurement_baseline.csv`
- `data/headlines_gold.csv`

## Automatisierte Tests

- `run_baseline_test.py`
- `run_classifier_test.py`

## Ergebnisse

Die automatisierten Benchmarks erreichen aktuell:

- Berechnungsgenauigkeit: 100 %
- Entscheidungsgenauigkeit: 100 %
- Precision: 100 %
- Recall: 100 %
- F1-Score: 100 %
- Exact Classification Accuracy: 100 %
- Material Mapping Accuracy: 100 %

Die Ergebnisdateien befinden sich unter `results/`.

## Fachliche Bewertung

Die KI-generierten Verhandlungsargumente wurden anhand von Material,
Risiko, Entscheidung, numerischer Genauigkeit und Handlungsorientierung bewertet.

Siehe:

- `manual/argument_expert_evaluation.csv`
- `results/argument_expert_metrics.json`

## Prozesswirkung und UX

Die Dateien unter `manual/examples/` enthalten simulierte Beispieldaten zur
Demonstration des Testverfahrens.

Sie stellen keine real erhobenen Teilnehmerdaten dar.

**Technischer und fachlicher Prototypentest: bestanden.**

**Empirische Prozess- und UX-Validierung: noch offen.**
