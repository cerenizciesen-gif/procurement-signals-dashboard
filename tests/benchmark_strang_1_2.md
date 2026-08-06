# Ableitung der Testanforderungen aus Benchmark Strang 1 und Strang 2

> Hinweis: Die folgende Darstellung wurde aus dem bestehenden Prototyp,
> den vorhandenen Testfällen und dem Testdesign rekonstruiert.
> Sie stellt keine wörtliche Wiedergabe eines ursprünglichen
> Benchmark-Dokuments dar.

## Strang 1: Interne Beschaffungsdaten und Entscheidungslogik

### Untersuchtes Thema

Interne Beschaffungs- und Preisdaten sowie der bisherige manuelle
Prozess zur Ableitung von Einkaufsempfehlungen.

### Zentrale Erkenntnisse

Die relevanten Einkaufsdaten liegen in tabellarischer Form vor und
enthalten unter anderem Material, Preisentwicklung, Einkaufsvolumen
und Kosteninformationen.

Die manuelle Auswertung erfordert mehrere Berechnungsschritte.
Insbesondere Jahresausgaben, monatliche Preisentwicklung und mögliche
Verzögerungskosten müssen für jedes Material einzeln ermittelt werden.

Aus den Eingangsdaten können standardisierte Handlungsempfehlungen wie
„Buy now“ oder „Delay“ abgeleitet werden.

### Identifiziertes Problem

Der manuelle Analyseprozess ist zeitaufwendig und fehleranfällig.

Berechnungen können unterschiedlich durchgeführt oder gerundet werden.
Außerdem fehlt eine einheitliche und nachvollziehbare Entscheidungslogik.

Dadurch können wichtige Kostenwirkungen übersehen und
Einkaufsentscheidungen verzögert werden.

### Anforderungen an das Dashboard

Das Dashboard soll:

- interne Beschaffungsdaten automatisiert auswerten,
- Jahresausgaben korrekt berechnen,
- Preisentwicklungen korrekt darstellen,
- Verzögerungskosten korrekt berechnen,
- für jedes Material eine Empfehlung „Buy now“ oder „Delay“ anzeigen,
- die verwendeten Werte und die Entscheidungslogik transparent machen,
- Ergebnisse schneller und vollständiger bereitstellen als eine
  manuelle CSV-Auswertung.

### Abgeleitete Tests

Aus Strang 1 wurden folgende Tests abgeleitet:

- Baseline-Benchmark
- Berechnungsgenauigkeit
- Entscheidungsgenauigkeit
- Prozesswirkung
- Bearbeitungszeit
- Vollständigkeit der Ergebnisse

---

## Strang 2: Externe Marktsignale und KI-Unterstützung

### Untersuchtes Thema

Externe Markt- und Nachrichtensignale sowie deren Nutzung für
Risikobewertung, Einkaufsentscheidungen und Verhandlungsvorbereitung.

### Zentrale Erkenntnisse

Externe Nachrichten enthalten sowohl relevante als auch irrelevante
Informationen.

Für den Einkauf sind insbesondere Signale zu folgenden Themen relevant:

- Lohnkosten
- Transportstörungen
- geopolitische Risiken
- Lieferkettenunterbrechungen

Diese Signale müssen einem betroffenen Material zugeordnet und nach
ihrer Relevanz bewertet werden.

Einkäufer benötigen neben einer Risikomeldung auch eine verständliche
Begründung und eine konkrete Handlungsempfehlung für
Lieferantengespräche.

### Identifiziertes Problem

Die manuelle Beobachtung externer Nachrichten erzeugt einen hohen
Informationsaufwand.

Relevante Signale können zwischen vielen irrelevanten Nachrichten
übersehen werden.

Die fachliche Einordnung hängt stark von einzelnen Personen ab und ist
daher nicht immer konsistent.

Außerdem besteht das Risiko, dass externe Ereignisse nicht rechtzeitig
mit internen Preis- und Kostendaten verknüpft werden.

### Anforderungen an das Dashboard

Das System soll:

- relevante Nachrichten automatisiert erkennen,
- irrelevante Nachrichten ausfiltern,
- erkannte Risiken einem Material zuordnen,
- einen passenden Risikotreiber bestimmen,
- die Relevanz oder Schwere des Risikos bewerten,
- interne Kostenwerte mit externen Signalen verbinden,
- fachlich korrekte Verhandlungsargumente erzeugen,
- korrekte Zahlen in den Argumenten verwenden,
- eine konkrete nächste Handlung empfehlen,
- die Ergebnisse verständlich und übersichtlich darstellen.

### Qualitätsanforderungen

Die Qualität der Nachrichtenklassifikation wird anhand folgender
Metriken bewertet:

- Precision
- Recall
- F1-Score
- Klassifikationsgenauigkeit

Die KI-generierten Verhandlungsargumente werden anhand folgender
Kriterien bewertet:

- korrektes Material,
- korrektes Risiko,
- Übereinstimmung mit der Entscheidung,
- korrekte Zahlen,
- konkrete und nutzbare Handlungsempfehlung.

### Abgeleitete Tests

Aus Strang 2 wurden folgende Tests abgeleitet:

- Nachrichtenklassifikation
- Precision
- Recall
- F1-Score
- fachliche Korrektheit der KI-Argumente
- Entscheidungsübereinstimmung
- numerische Genauigkeit
- UX- und Usability-Test

---

## Zusammenfassung der Ableitung

Die Testfälle wurden aus zwei Benchmark-Strängen abgeleitet.

Strang 1 fokussiert die korrekte und effiziente Auswertung interner
Beschaffungsdaten.

Strang 2 untersucht die automatisierte Verarbeitung externer
Marktsignale sowie deren Überführung in fachlich korrekte und
handlungsorientierte Einkaufsinformationen.

| Benchmark-Strang | Abgeleitete Testbereiche |
|---|---|
| Strang 1 | Baseline-Test, Berechnungen, Entscheidungen, Prozesswirkung |
| Strang 2 | Klassifikation, KI-Argumente, fachliche Korrektheit, UX |
