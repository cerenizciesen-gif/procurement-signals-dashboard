# Prompt protocol

Reproducible documentation of the generative step in `analyze_data.py`, as required by the
group assignment ("Reproduzierbare Dokumentation: Prompts, Workflow-Export, Repository").

## Where generative AI is used — and where it is not

| Step | Method | Why |
| --- | --- | --- |
| Price series, annual spend, opportunity cost | Python arithmetic | Money must be recalculable by hand and identical on every run |
| Buy now / Delay signal | Rule table (`RISK_RULES`, `TREND_RULES`) | The buyer must be able to see why a signal appeared; an auditable rule survives a compliance review, a model output does not |
| Negotiation argument | Language model | Turning figures into a usable argument is a language task, not a calculation |

The model is never asked to calculate, forecast or decide. It receives figures that already
exist and phrases them. A hallucinated number therefore cannot enter the recommendation —
this is the core governance argument of the prototype and the reason the split exists.

## Model and parameters

| Parameter | Value |
| --- | --- |
| Provider | Anthropic Messages API |
| Model | `claude-sonnet-4-5-20250929` (pinned, not an alias) |
| `max_tokens` | 400 |
| Temperature | provider default (not set) |
| Credential | `ANTHROPIC_API_KEY`, injected as a GitHub Actions secret, never committed |
| Behaviour without a key | Keeps a previously generated argument if one exists, otherwise falls back to the rule sentence; the run always succeeds and `argument_source` records which path was taken |

## System prompt

```
You support a procurement manager who buys direct raw materials for automotive
production in Turkey. You write the negotiation argument the buyer takes into a
supplier conversation.

Rules you must follow:
1. Use only the figures given to you. Never calculate, estimate or invent a number,
   a date or a source. If a figure is not provided, do not refer to it.
2. Do not question the recommendation you are given. Your task is to justify it.
3. Write two to three sentences, plain English, no bullet points, no headings.
4. Name the macro risk and what it does to cost, then state what the buyer should do
   and by when.
5. Sentence case only. Do not write words in all capitals except acronyms such as PP,
   PA6 or USD/TRY.
6. No brand names, no supplier names, no company names.
7. Sober, factual tone. No sales language, no exclamation marks.
```

### Design rationale per rule

Following Mollick et al. (2024) on constraining agent behaviour through explicit role,
scope and output specification:

1. **Rule 1 — no invented figures.** The main hallucination risk in a procurement context
   is a plausible but wrong number quoted at a supplier. Restricting the model to supplied
   facts is the primary mitigation.
2. **Rule 2 — do not re-decide.** Separates the decision (rules, auditable) from its
   wording (model). Without this the model may contradict the signal shown next to it.
3. **Rule 3 — length and form.** Output is rendered in a fixed card in the dashboard; a
   non-functional requirement of the concept is that the buyer is not overloaded.
4. **Rule 4 — required content.** Guarantees the argument is usable in a conversation:
   cause, effect, action, timing.
5. **Rule 5 — typography.** Project-wide rule: no all-caps outside acronyms.
6. **Rule 6 — anonymity.** Supplier and partner data are confidential; nothing identifying
   may leave the system into a model context.
7. **Rule 7 — tone.** A vendor-style tone would undermine credibility in a negotiation.

## User prompt template

One request per material. Every value is computed in Python beforehand.

```
Material: {material}
Market: Turkey, direct purchasing
Annual volume: {volume_tons_year} tons per year
Current price: EUR {current_price_eur} per {price_unit}
Price trend last month: {price_trend}
Average monthly change over the last three months: {monthly_trend_pct} percent
Annual purchasing volume: EUR {annual_spend_eur}
Delaying the decision by {horizon_months} months would cost about EUR {delay_cost} extra
on the annual volume.            <- or "would save about EUR ..." when the trend is falling
Macro risk: {driver} ({driver_value})
Recommendation to justify: {signal}
Reason the recommendation was triggered: {reasoning}
{tension_line}

Write the negotiation argument for the buyer. Refer to the euro figure.
```

`{tension_line}` is set by code and handles the case where the price trend points against
the recommendation — for example a falling price (waiting would be cheaper) while the macro
risk still says buy now. The model is then told to address the tension rather than ignore
it, because a buyer who sees a favourable trend and a "buy now" signal side by side will
ask why.

## Filled example — PP, July 2026

```
Material: PP
Market: Turkey, direct purchasing
Annual volume: 600 tons per year
Current price: EUR 1.17 per kg
Price trend last month: Up
Average monthly change over the last three months: +1.51 percent
Annual purchasing volume: EUR 702,000
Delaying the decision by 6 months would cost about EUR 63,470 extra on the annual volume.
Macro risk: Turkey minimum wage increase (+15%)
Recommendation to justify: Buy now
Reason the recommendation was triggered: Local conversion costs rise with the wage
increase, so current price levels will not hold.
The price trend and the macro risk point in the same direction.

Write the negotiation argument for the buyer. Refer to the euro figure.
```

The PA6 case is the interesting one: the trend is falling, so waiting would save money,
yet the freight risk still triggers "buy now". There the tension line reads *"Note the
tension: the falling price trend argues for waiting, but the macro risk is the reason the
recommendation is to buy now anyway. Address this."*

## Opportunity cost formula

From the concept presentation: *Einsparpotenzial = Einkaufsvolumen × Preisdelta*.

```
annual spend      = annual volume (t) x 1000 x price per kg      (PP, PA6)
                  = annual volume (t) x price per ton            (Steel)
monthly trend     = mean month-on-month change over the last 3 months
price delta       = monthly trend x 6 months
delay cost (EUR)  = annual spend x price delta
```

A positive delay cost means waiting is more expensive; a negative one means waiting saves
money. The three-month trend extrapolation is an extrapolation, not a forecast model, and
is labelled as such in `signals.json` (`opportunity.basis`) and in the dashboard.

In the interface this figure is deliberately **not** phrased as an instruction ("cost of
waiting") but as a measurement ("price-trend effect on annual volume, 6 mo"). It is one
input to the decision, not a competing recommendation — otherwise a buyer reading a green
"buy now" signal next to a green "saving by waiting" figure receives two opposite
instructions in the same colour. Green and red are reserved for saving versus extra cost;
the recommendation itself is carried by the signal alone, and a reconciliation line states
which of the two factors outweighs the other.

## Execution modes

The generative step can run in two ways. Both use the identical prompt documented above, so
the output is comparable either way.

| Mode | How the call is made | `argument_source` records |
| --- | --- | --- |
| Automated | The scheduled job calls the API with the configured key | The pinned model name |
| Manual | The prompt is executed once in a chat interface and the result written into `signals.json` | The model used |
| No model | Neither is available | `rule-based fallback` |

The manual mode exists because an API credential was not available for the interim test run.
It is a documented, reproducible step, not an undocumented shortcut: the prompt is fixed in
this file, so the same input can be replayed at any time. A scheduled run without a working
key deliberately does **not** overwrite an argument that was generated this way — replacing a
real completion with the weaker rule sentence would degrade the output silently.

## Known limitations

- The price series is a mockup dataset, not live market data. The pipeline is real; the
  input is synthetic.
- The trend extrapolation is linear and reacts slowly to turning points. A production
  version would need a forecast model with a confidence interval.
- Signal thresholds are set by the project team, not by the practice partner. This is an
  open question in the concept.
- The model output is not automatically checked for factual consistency against the input
  figures. Verifying this is part of the test phase.
