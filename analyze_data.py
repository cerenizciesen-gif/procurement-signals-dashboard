"""Procurement signal generator — direct purchasing, Turkish market.

Pipeline per material (Steel, PA6, PP):
  1. read the monthly price series from the dataset
  2. compute the opportunity cost deterministically  (money, in Python — never by a model)
  3. derive the buy/delay signal from the recorded macro risk  (auditable rules)
  4. have a language model phrase the negotiation argument  (generative step)

The split in steps 2-4 is deliberate and is the governance argument of this prototype:
every number is computed by code and can be recalculated by hand; the model only turns
figures that already exist into an argument a buyer can use in a supplier conversation.
It is never asked to calculate, forecast or judge — so a hallucinated number cannot
enter the recommendation.

If no API key is configured the run still succeeds and falls back to a fixed sentence,
so the scheduled job never breaks. The output file records which path was taken.

Output: signals.json, consumed by the procurement dashboard.
"""

from __future__ import annotations

import csv
import json
import math
import os
import statistics
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

DATA_FILE = Path("procurement_dataset.csv")
MONITOR_FILE = Path("macro_signals.json")
OUTPUT_FILE = Path("signals.json")

# The dataset is the deterministic input the test plan relies on, so live detections from
# monitor_sources.py are only allowed to drive the decision when explicitly switched on.
# Either way the monitor's findings are attached to the output so the dashboard can show
# what was detected.
USE_LIVE_MACRO = os.environ.get("USE_LIVE_MACRO", "").strip() in {"1", "true", "yes"}

MATERIALS = ("PP", "PA6", "Steel")

# Price basis per material, needed to turn a price into an annual spend.
# The dataset carries prices per kg for the polymers and per ton for steel.
PRICE_UNIT = {"PP": "kg", "PA6": "kg", "Steel": "ton"}
KG_PER_TON = 1000

# Horizon the opportunity cost is projected over, in months.
OPPORTUNITY_HORIZON_MONTHS = 6

# Forecast horizon shown on the dashboard chart, in months.
FORECAST_HORIZON_MONTHS = 6

# Alert rules. Evaluated against the latest month on every run. Delivery to a real channel
# is not implemented — see ALERT_DELIVERY below; the status here is the honest result of
# checking the rule, not a claim that anyone was notified.
ALERT_RULES = [
    {"id": 1, "material": "Steel", "type": "price_above", "threshold": 800.0, "channel": "email", "created": "2026-07-20"},
    {"id": 2, "material": "PA6", "type": "price_below", "threshold": 2.55, "channel": "email", "created": "2026-07-22"},
    {"id": 3, "material": "PP", "type": "price_above", "threshold": 1.15, "channel": "email", "created": "2026-07-24"},
    {"id": 4, "material": "Steel", "type": "monthly_change_above", "threshold": 1.0, "channel": "sms", "created": "2026-07-27"},
]

ALERT_DELIVERY = {
    "implemented": False,
    "note": (
        "Conditions are evaluated on every run against the latest data. Dispatch to an email "
        "or SMS channel is not implemented: it needs a provider credential and a recipient "
        "list, both of which are the practice partner's to supply."
    ),
}

# Signal colors for the dashboard: green for actionable/positive, red for warning/negative.
COLOR_POSITIVE = "#2e7d4f"
COLOR_NEGATIVE = "#c04a3b"

# Marks an argument that was not produced by a model.
FALLBACK_SOURCE = "rule-based fallback"

# Generative step. Model is pinned so a run is reproducible; see prompts.md for the
# prompt protocol and the reasoning behind each instruction.
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_MODEL = "claude-sonnet-4-5-20250929"
ANTHROPIC_VERSION = "2023-06-01"
MAX_TOKENS = 400
REQUEST_TIMEOUT = 60

SYSTEM_PROMPT = (
    "You support a procurement manager who buys direct raw materials for automotive "
    "production in Turkey. You write the negotiation argument the buyer takes into a "
    "supplier conversation.\n\n"
    "Rules you must follow:\n"
    "1. Use only the figures given to you. Never calculate, estimate or invent a number, "
    "a date or a source. If a figure is not provided, do not refer to it.\n"
    "2. Do not question the recommendation you are given. Your task is to justify it.\n"
    "3. Write two to three sentences, plain English, no bullet points, no headings.\n"
    "4. Name the macro risk and what it does to cost, then state what the buyer should do "
    "and by when.\n"
    "5. Sentence case only. Do not write words in all capitals except acronyms such as PP, "
    "PA6 or USD/TRY.\n"
    "6. No brand names, no supplier names, no company names.\n"
    "7. Sober, factual tone. No sales language, no exclamation marks."
)

# Macro risk to recommendation mapping. Auditable rules, deliberately not left to a model:
# the buyer must be able to see why a signal appeared.
RISK_RULES = {
    "Turkey minimum wage increase": {
        "signal": "Buy now",
        "reasoning": "Local conversion costs rise with the wage increase, so current price levels will not hold.",
    },
    "Red Sea shipping disruption": {
        "signal": "Buy now",
        "reasoning": "Freight costs are surging and will feed into local list prices with a delay.",
    },
    "Geopolitical supply disruption": {
        "signal": "Delay",
        "reasoning": "Market volatility is extreme, so committing now risks buying at a peak.",
    },
    "USD/TRY rate surge": {
        "signal": "Buy now",
        "reasoning": "A weaker lira raises the local cost of imported material, so waiting means paying more in local currency.",
    },
}

# Fallback when no macro risk is recorded: follow the month-on-month price trend.
TREND_RULES = {
    "Up": {"signal": "Delay", "reasoning": "Prices are trending up with no macro trigger."},
    "Down": {"signal": "Buy now", "reasoning": "Prices are easing against last month."},
    "Stable": {"signal": "Delay", "reasoning": "Prices are flat, so there is no timing advantage."},
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_previous_arguments() -> dict[str, dict[str, str]]:
    """Arguments from the last run, indexed by material.

    A scheduled run without a working model must not replace a real generated argument
    with the weaker rule sentence — that would silently degrade the output. Arguments that
    were genuinely generated (manually or by an earlier automated run) are therefore kept
    until a new generation succeeds.
    """
    if not OUTPUT_FILE.exists():
        return {}
    try:
        previous = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    kept = {}
    for entry in previous.get("signals", []):
        source = entry.get("argument_source")
        argument = entry.get("negotiation_argument")
        if argument and source and source != FALLBACK_SOURCE:
            kept[entry.get("material")] = {"argument": argument, "source": source}
    return kept


def has_value(value: str | None) -> bool:
    return bool(value) and value.strip().lower() not in {"none", "n/a", "-", ""}


def series_for(rows: list[dict[str, str]], material: str) -> list[dict[str, str]]:
    selected = [row for row in rows if row["Material"] == material]
    if not selected:
        raise ValueError(f"No rows found for material: {material}")
    return sorted(selected, key=lambda row: datetime.strptime(row["Date"], "%Y-%m-%d"))


def annual_spend_eur(material: str, price: float, volume_tons: float) -> float:
    """Annual purchasing volume in euros, from the price basis of the material."""
    if PRICE_UNIT[material] == "kg":
        return volume_tons * KG_PER_TON * price
    return volume_tons * price


def monthly_trend(prices: list[float], window: int = 3) -> float:
    """Average month-on-month change over the last `window` steps, as a ratio."""
    usable = prices[-(window + 1):]
    if len(usable) < 2:
        return 0.0
    steps = [
        (usable[i] - usable[i - 1]) / usable[i - 1]
        for i in range(1, len(usable))
        if usable[i - 1]
    ]
    return sum(steps) / len(steps) if steps else 0.0


def build_opportunity(material: str, prices: list[float], volume_tons: float) -> dict[str, object]:
    """Cost of moving the purchase decision by the horizon, in euros.

    Einsparpotenzial = Jahresvolumen x Preisdelta, per the concept. The price delta is the
    observed three-month trend extrapolated over the horizon — an extrapolation, not a
    forecast model, and labelled as such in the output.
    """
    current = prices[-1]
    trend = monthly_trend(prices)
    delta_ratio = trend * OPPORTUNITY_HORIZON_MONTHS
    spend = annual_spend_eur(material, current, volume_tons)
    return {
        "annual_spend_eur": round(spend, 2),
        "monthly_trend_pct": round(trend * 100, 2),
        "horizon_months": OPPORTUNITY_HORIZON_MONTHS,
        "projected_price_delta_pct": round(delta_ratio * 100, 2),
        # Positive = delaying costs this much more. Negative = delaying would save this much.
        "delay_cost_eur": round(spend * delta_ratio, 2),
        "basis": (
            f"annual volume {volume_tons:,.0f} t x current price, "
            f"three-month trend extrapolated over {OPPORTUNITY_HORIZON_MONTHS} months"
        ),
    }


def read_monitor() -> dict[str, object]:
    """Findings written by monitor_sources.py, or an empty structure if it has not run."""
    if not MONITOR_FILE.exists():
        return {}
    try:
        return json.loads(MONITOR_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def build_forecast(prices: list[float]) -> dict[str, object]:
    """Forward price path and a confidence band, computed from the observed series.

    The central path extrapolates the same three-month trend the opportunity cost uses, so
    the chart and the money figure can never disagree. The band is the historical volatility
    of month-on-month changes, widened with the square root of the horizon — the standard
    way uncertainty grows over a random walk. This is an extrapolation with an error
    estimate, not a forecast model, and it is labelled as such wherever it is shown.
    """
    current = prices[-1]
    trend = monthly_trend(prices)

    steps = [
        (prices[i] - prices[i - 1]) / prices[i - 1]
        for i in range(1, len(prices))
        if prices[i - 1]
    ]
    volatility = statistics.pstdev(steps) if len(steps) > 1 else 0.0

    values, low, high = [], [], []
    for month in range(1, FORECAST_HORIZON_MONTHS + 1):
        centre = current * (1 + trend * month)
        spread = centre * volatility * math.sqrt(month)
        values.append(round(centre, 4))
        low.append(round(centre - spread, 4))
        high.append(round(centre + spread, 4))

    return {
        "horizon_months": FORECAST_HORIZON_MONTHS,
        "values": values,
        "low": low,
        "high": high,
        "monthly_volatility_pct": round(volatility * 100, 2),
        "method": "three-month trend extrapolation, band = historical volatility x sqrt(month)",
    }


def evaluate_alerts(signals: list[dict[str, object]]) -> list[dict[str, object]]:
    """Check every alert rule against the latest figures."""
    by_material = {s["material"]: s for s in signals}
    results = []

    for rule in ALERT_RULES:
        signal = by_material.get(rule["material"])
        if not signal:
            continue

        price = signal["current_price_eur"]
        change = signal["opportunity"]["monthly_trend_pct"]
        unit = signal["price_unit"]

        if rule["type"] == "price_above":
            triggered = price > rule["threshold"]
            condition = f"Price > EUR {rule['threshold']:g} per {unit}"
            observed = f"EUR {price:g} per {unit}"
        elif rule["type"] == "price_below":
            triggered = price < rule["threshold"]
            condition = f"Price < EUR {rule['threshold']:g} per {unit}"
            observed = f"EUR {price:g} per {unit}"
        else:
            triggered = change > rule["threshold"]
            condition = f"Monthly change > {rule['threshold']:g}%"
            observed = f"{change:+.2f}% per month"

        results.append(
            {
                "id": rule["id"],
                "material": rule["material"],
                "condition": condition,
                "observed": observed,
                "status": "Triggered" if triggered else "Active",
                "channel": rule["channel"],
                "created": rule["created"],
                "delivered": False,
            }
        )

    return results


def decide(row: dict[str, str], live: dict[str, object] | None) -> tuple[dict[str, str], str, str | None, str]:
    """Returns (rule, driver, driver value, where the driver came from)."""
    if USE_LIVE_MACRO and live and live.get("risk_factor") in RISK_RULES:
        factor = live["risk_factor"]
        value = live.get("value") or live.get("severity")
        return RISK_RULES[factor], factor, value, "live monitor"

    risk_factor = row.get("Macro_Risk_Factor", "")
    risk_value = row.get("Macro_Risk_Value", "")

    if has_value(risk_factor) and risk_factor in RISK_RULES:
        return RISK_RULES[risk_factor], risk_factor, risk_value if has_value(risk_value) else None, "dataset"

    rule = TREND_RULES.get(row.get("Price_Trend", "Stable"), TREND_RULES["Stable"])
    return rule, "Price trend", row.get("Price_Trend"), "dataset"


def build_prompt(record: dict[str, object]) -> str:
    """Facts handed to the model. Every figure here was computed in Python."""
    opportunity = record["opportunity"]
    delay_cost = opportunity["delay_cost_eur"]
    if delay_cost >= 0:
        money_line = (
            f"Delaying the decision by {opportunity['horizon_months']} months would cost about "
            f"EUR {delay_cost:,.0f} extra on the annual volume."
        )
    else:
        money_line = (
            f"Delaying the decision by {opportunity['horizon_months']} months would save about "
            f"EUR {abs(delay_cost):,.0f} on the annual volume."
        )

    # Where the price trend points against the recommendation, name the tension explicitly
    # so the argument reconciles it instead of quietly ignoring the figure.
    waiting_is_dearer = delay_cost >= 0
    buying_now = record["signal"] == "Buy now"
    if buying_now == waiting_is_dearer:
        tension_line = "The price trend and the macro risk point in the same direction."
    elif waiting_is_dearer:
        tension_line = (
            "Note the tension: the rising price trend argues against waiting, but the macro "
            "risk is the reason the recommendation is to wait anyway. Address this."
        )
    else:
        tension_line = (
            "Note the tension: the falling price trend argues for waiting, but the macro risk "
            "is the reason the recommendation is to buy now anyway. Address this."
        )

    return "\n".join(
        [
            f"Material: {record['material']}",
            f"Market: Turkey, direct purchasing",
            f"Annual volume: {record['volume_tons_year']:,.0f} tons per year",
            f"Current price: EUR {record['current_price_eur']} per {PRICE_UNIT[record['material']]}",
            f"Price trend last month: {record['price_trend']}",
            f"Average monthly change over the last three months: {opportunity['monthly_trend_pct']:+.2f} percent",
            f"Annual purchasing volume: EUR {opportunity['annual_spend_eur']:,.0f}",
            money_line,
            f"Macro risk: {record['driver']}"
            + (f" ({record['driver_value']})" if record.get("driver_value") else ""),
            f"Recommendation to justify: {record['signal']}",
            f"Reason the recommendation was triggered: {record['reasoning']}",
            tension_line,
            "",
            "Write the negotiation argument for the buyer. Refer to the euro figure.",
        ]
    )


def generate_argument(record: dict[str, object], previous: dict[str, dict[str, str]]) -> tuple[str, str]:
    """Returns (argument, source).

    Order of preference: a fresh model completion, then a generated argument kept from the
    previous run, then the rule sentence.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    material = record["material"]
    kept = previous.get(material)

    def fall_back(note: str) -> tuple[str, str]:
        if kept:
            print(f"  {material}: {note}, keeping the argument from the previous run")
            return kept["argument"], kept["source"]
        print(f"  {material}: {note}, using rule-based text")
        return record["reasoning"], FALLBACK_SOURCE

    if not api_key:
        return fall_back("no API key configured")

    payload = json.dumps(
        {
            "model": ANTHROPIC_MODEL,
            "max_tokens": MAX_TOKENS,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": build_prompt(record)}],
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        ANTHROPIC_URL,
        data=payload,
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": ANTHROPIC_VERSION,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            body = json.loads(response.read().decode("utf-8"))
        text = "".join(
            block.get("text", "") for block in body.get("content", []) if block.get("type") == "text"
        ).strip()
        if not text:
            raise ValueError("empty completion")
        print(f"  {material}: argument generated by {ANTHROPIC_MODEL}")
        return text, ANTHROPIC_MODEL
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, KeyError) as error:
        return fall_back(f"generation failed ({error})")


def build_signal(
    rows: list[dict[str, str]],
    previous: dict[str, dict[str, str]],
    monitor: dict[str, object],
) -> dict[str, object]:
    latest = rows[-1]
    material = latest["Material"]
    prices = [float(row["Current_Price_EUR"]) for row in rows]
    volume_tons = float(latest["Volume_Tons_Year"])

    live = (monitor.get("by_material") or {}).get(material)
    rule, driver, driver_value, driver_origin = decide(latest, live)
    is_positive = rule["signal"] == "Buy now"

    record: dict[str, object] = {
        "material": material,
        "date": latest["Date"],
        "volume_tons_year": volume_tons,
        "price_unit": PRICE_UNIT[material],
        "current_price_eur": float(latest["Current_Price_EUR"]),
        "price_trend": latest["Price_Trend"],
        "macro_risk_factor": latest["Macro_Risk_Factor"] if has_value(latest.get("Macro_Risk_Factor")) else None,
        "macro_risk_value": latest["Macro_Risk_Value"] if has_value(latest.get("Macro_Risk_Value")) else None,
        "driver": driver,
        "driver_value": driver_value,
        "driver_origin": driver_origin,
        "detected_risk": live,
        "signal": rule["signal"],
        "reasoning": rule["reasoning"],
        "sentiment": "positive" if is_positive else "negative",
        "color": COLOR_POSITIVE if is_positive else COLOR_NEGATIVE,
        "opportunity": build_opportunity(material, prices, volume_tons),
        "forecast": build_forecast(prices),
    }

    argument, source = generate_argument(record, previous)
    record["negotiation_argument"] = argument
    record["argument_source"] = source
    return record


def main() -> None:
    rows = read_rows(DATA_FILE)
    previous = read_previous_arguments()
    monitor = read_monitor()
    if monitor:
        mode = "driving the decision" if USE_LIVE_MACRO else "attached for display only"
        print(f"Market monitor found ({mode}).")
    print("Generating signals:")
    signals = [build_signal(series_for(rows, material), previous, monitor) for material in MATERIALS]

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_file": DATA_FILE.name,
        "as_of": signals[0]["date"] if signals else None,
        "scope": {
            "function": "Direct purchasing",
            "market": "Turkey",
            "materials": list(MATERIALS),
            "currency": "EUR",
        },
        "legend": {"positive": COLOR_POSITIVE, "negative": COLOR_NEGATIVE},
        "alerts": {"delivery": ALERT_DELIVERY, "rules": evaluate_alerts(signals)},
        "market_monitor": {
            "available": bool(monitor),
            "drives_decision": USE_LIVE_MACRO,
            "generated_at": monitor.get("generated_at"),
            "classification_method": monitor.get("classification_method"),
            "exchange_rate": (monitor.get("sources") or {}).get("exchange_rate"),
            "headlines_screened": ((monitor.get("sources") or {}).get("news") or {}).get("headlines_screened"),
            "findings": (monitor.get("findings") or [])[:6],
        },
        "signals": signals,
    }

    OUTPUT_FILE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("\nResult:")
    for signal in signals:
        delay = signal["opportunity"]["delay_cost_eur"]
        print(f"  {signal['material']}: {signal['signal']} — delay cost EUR {delay:,.0f}")


if __name__ == "__main__":
    main()
