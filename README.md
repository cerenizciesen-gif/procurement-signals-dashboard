# Automotive procurement dashboard

A raw material price monitor and negotiation assistant for direct purchasing in the Turkish
market. It reads a monthly price series, watches external sources for macro risks, computes
what the timing of a purchase decision is worth in euros, and turns that into one clear
recommendation per material: **buy now** or **delay**.

The system does not place orders and does not decide. It produces a recommendation with the
reasoning attached; a human makes the call.

Live dashboard: published from this repository via GitHub Pages.

## Scope

| Dimension | Value |
| --- | --- |
| Function | Direct purchasing only |
| Materials | Steel (5,000 t/yr), PA6 (1,300 t/yr), PP (600 t/yr) |
| Market | Turkey |
| Horizon | Continuous, open-ended |
| Currency | EUR is the data basis; USD and TRY are display conversions |
| Forecast | 6 months ahead |

## Quick start

Nothing to install. The dashboard is a static page and the scripts use only the Python
standard library.

```bash
# clone, then from the repository root:
python monitor_sources.py     # scan external sources  -> macro_signals.json
python analyze_data.py        # compute and decide     -> signals.json
python -m http.server 8000    # then open http://localhost:8000
```

Opening `index.html` by double-clicking will not work: browsers block `fetch` on `file://`,
so the page falls back to its built-in sample data and says so in the header. Serve it over
HTTP, or use the published GitHub Pages URL.

Python 3.10 or newer is required (the scripts use `X | None` type syntax).

## How it works

```
procurement_dataset.csv ─┐
                         ├─→ analyze_data.py ──→ signals.json ──→ index.html
macro_signals.json ──────┘                                          (browser)
        ↑
monitor_sources.py ←── central bank exchange rate, news feed
```

Each step writes a file the next step reads. The intermediate files are committed, so every
run leaves an auditable trace in the repository history.

### 1. `monitor_sources.py` — external sources

Reads the Turkish central bank's daily USD/TRY reference rate and computes the change over
the last thirty days. Queries a public news search feed for freight, wage, scrap, resin and
supply-disruption topics, then classifies the headlines into a fixed risk taxonomy:

- Turkey minimum wage increase
- Red Sea shipping disruption
- Geopolitical supply disruption

The taxonomy is closed. A classification outside these three is discarded in code rather
than accepted, because the decision table downstream only understands these three.

Writes `macro_signals.json`. A source that cannot be reached is recorded as unavailable and
the run continues.

### 2. `analyze_data.py` — computation and decision

- Computes annual spend, the three-month price trend and the opportunity cost of delaying
- Computes the forward price path and its confidence band from the observed series
- Derives the buy/delay signal from the recorded macro risk, via an inspectable rule table
- Evaluates every alert rule against the latest figures
- Produces the negotiation argument

Writes `signals.json`.

### 3. `index.html` — dashboard

A static page with no build step. On load it fetches `signals.json` and
`procurement_dataset.csv` and renders everything from them. There is no hardcoded material
data, forecast or signal in the page — if the backend files cannot be reached, it falls back
to sample values and labels the header "Sample data".

## Where generative AI sits

Two steps use a language model, and both are deliberately narrow.

| Step | Task |
| --- | --- |
| Screening (`monitor_sources.py`) | Read a headline, decide if it is price-relevant, assign the risk factor and severity |
| Phrasing (`analyze_data.py`) | Turn computed figures into the negotiation argument |

Everything else is code:

| Work | Done by | Why |
| --- | --- | --- |
| Money and trends | Python arithmetic | Must be recalculable by hand, identical every run |
| Buy / delay decision | Rule table | The buyer must see why a signal appeared |
| Wording of the argument | Language model | Turning a figure into an argument is a language task |

**The model is never asked to calculate, forecast or decide.** A hallucinated number
therefore cannot reach the recommendation. This split is the governance argument of the
prototype; the full prompt protocol is in [`prompts.md`](prompts.md).

### Current state

No API key is configured, so both generative steps run on their non-model fallbacks:
keyword matching for screening, and the rule sentence for the argument. The dashboard
labels this state openly rather than presenting rule output as model output.

The fallbacks have real limits, visible in the last run: the keyword matcher found the
minimum-wage story but did not notice it was from December 2025, and could not extract the
"27 percent" stated in the headline. Closing those two gaps is exactly what the model layer
is for.

### On retrieval-augmented generation

This is retrieval-grounded generation, not a classic RAG stack. There is no vector index and
no semantic search: retrieval is a direct read of the relevant rows, passed to the model in
full. At this data volume — three materials, twelve months — a vector index would add
machinery without adding capability. The three defining properties are present: knowledge is
fetched from an external source at run time, the output is built only from that fetched
data, and the knowledge lives outside the model and outside the code. See
[`architecture.md`](architecture.md).

## Configuration

Both settings live on the workflow file, `.github/workflows/procurement_bot.yml`.

| Name | Type | Default | Effect |
| --- | --- | --- | --- |
| `ANTHROPIC_API_KEY` | Repository secret | not set | Activates both generative steps. Without it the scripts fall back and still succeed |
| `USE_LIVE_MACRO` | Environment variable | `"0"` | `"1"` lets detected live risks drive the recommendation instead of the dataset |

To add the key: **Settings → Secrets and variables → Actions → New repository secret**, name
it `ANTHROPIC_API_KEY`. No code change is needed.

`USE_LIVE_MACRO` is off by default on purpose. The test plan needs a deterministic input, and
a live news feed would invalidate its expected values. Detected risks are still displayed on
the dashboard; they just do not drive the decision.

A scheduled run without a working key will **not** overwrite an argument that was genuinely
generated earlier — replacing a real completion with the weaker rule sentence would degrade
the output silently.

## Automation

The workflow runs daily at 05:00 UTC (08:00 Istanbul) and can also be started manually from
the Actions tab. It checks out the repository, sets up Python, scans external sources,
generates signals, and commits the two output files if they changed.

The scanning step is marked `continue-on-error`, so an outage in an external feed can never
block signal generation.

## Data format

`procurement_dataset.csv` — one row per material per month:

```
Date,Material,Volume_Tons_Year,Current_Price_EUR,Price_Trend,Macro_Risk_Factor,Macro_Risk_Value
2026-07-01,PP,600,1.170,Up,Turkey minimum wage increase,+15%
```

`Macro_Risk_Factor` and `Macro_Risk_Value` are `None` for all months except the last. This is
deliberate: the final month carries the hidden test cases the decision logic is checked
against.

To extend the series, append rows with a later date. The scripts always read the most recent
month per material.

## Repository contents

| File | Purpose |
| --- | --- |
| `procurement_dataset.csv` | Monthly price series, volumes, macro risks |
| `monitor_sources.py` | External source scanning and classification |
| `analyze_data.py` | Computation, decision rules, argument generation |
| `macro_signals.json` | Detected macro risks (generated) |
| `signals.json` | Per-material signal, figures, forecast, alerts (generated) |
| `index.html` | Dashboard |
| `styles.css`, `support.js`, `_ds_bundle.js` | Design system and runtime for the dashboard |
| `prompts.md` | Prompt protocol and the reasoning behind each rule |
| `architecture.md` | Justification of the technology choice |
| `.github/workflows/` | Scheduled workflow |

## What is real and what is mockup

| Element | State |
| --- | --- |
| Pipeline, scheduling, hosting, versioning | Real |
| Exchange rate | Real, read live from the central bank |
| News screening | Real feed; keyword classification until a key is configured |
| All monetary figures, trends, opportunity cost | Real computation |
| Forecast path and confidence band | Computed from the observed series |
| Alert evaluation | Real, checked against the latest figures on every run |
| Price series | Mockup dataset — no live price source is connected |
| Alert delivery | Not implemented — needs a provider credential and recipient list |

## Known limitations

- The price series is synthetic. The pipeline is real; the input is not.
- The forecast is a trend extrapolation with a volatility band, not a trained model. It
  reacts slowly to turning points.
- Signal thresholds were set by the project team, not confirmed by the practice partner.
- Model output is not automatically checked for consistency against the input figures. That
  belongs to the test phase.
- Detected events are not archived; each run overwrites the previous findings.
- No role-based access control.

## Documentation

- [`prompts.md`](prompts.md) — prompt protocol, design rationale, execution modes
- [`architecture.md`](architecture.md) — why GitHub instead of AWS, architectural equivalence

## Division of work

| Area | Owner |
| --- | --- |
| Concept and scope | Joint |
| Dataset, analysis, dashboard, automation | Umutcan Elmalı |
| Test plan and test execution | Ceren Esen |
| Management paper | Joint |
