"""Procurement signal generator.

Reads the monthly raw material dataset, looks at the latest month, and turns the
macro risk recorded for that month into a single, plain recommendation per
material so buyers get one clear action instead of a wall of numbers.

Output: signals.json, consumed by the procurement dashboard.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

DATA_FILE = Path("procurement_dataset.csv")
OUTPUT_FILE = Path("signals.json")

MATERIALS = ("PP", "PA6", "Steel")

# Signal colors for the dashboard: green for actionable/positive, red for warning/negative.
COLOR_POSITIVE = "#2e7d4f"
COLOR_NEGATIVE = "#c04a3b"

# Macro risk to recommendation mapping. Each entry carries the buyer-facing
# reasoning so the dashboard can explain the signal without extra lookups.
RISK_RULES = {
    "Turkey minimum wage increase": {
        "signal": "Buy now",
        "rationale": "Local conversion costs will rise with the wage increase; secure volumes before suppliers reprice.",
    },
    "Red Sea shipping disruption": {
        "signal": "Buy now",
        "rationale": "Freight costs are surging; build stock before the increase feeds into local prices.",
    },
    "Geopolitical supply disruption": {
        "signal": "Delay",
        "rationale": "Market volatility is extreme; wait it out rather than buying at a peak.",
    },
}

# Fallback when no macro risk is recorded: follow the month-on-month price trend.
TREND_RULES = {
    "Up": {
        "signal": "Delay",
        "rationale": "Prices are trending up with no macro trigger; revisit once the move settles.",
    },
    "Down": {
        "signal": "Buy now",
        "rationale": "Prices are easing; current levels offer a cost saving against last month.",
    },
    "Stable": {
        "signal": "Delay",
        "rationale": "Prices are flat; no timing advantage in committing yet.",
    },
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def has_risk(value: str | None) -> bool:
    return bool(value) and value.strip().lower() not in {"none", "n/a", "-"}


def latest_row_for(rows: list[dict[str, str]], material: str) -> dict[str, str]:
    material_rows = [row for row in rows if row["Material"] == material]
    if not material_rows:
        raise ValueError(f"No rows found for material: {material}")
    return max(material_rows, key=lambda row: datetime.strptime(row["Date"], "%Y-%m-%d"))


def build_signal(row: dict[str, str]) -> dict[str, object]:
    risk_factor = row.get("Macro_Risk_Factor", "")
    risk_value = row.get("Macro_Risk_Value", "")

    if has_risk(risk_factor) and risk_factor in RISK_RULES:
        rule = RISK_RULES[risk_factor]
        driver = risk_factor
        driver_value = risk_value if has_risk(risk_value) else None
    else:
        rule = TREND_RULES.get(row.get("Price_Trend", "Stable"), TREND_RULES["Stable"])
        driver = "Price trend"
        driver_value = row.get("Price_Trend")

    is_positive = rule["signal"] == "Buy now"

    return {
        "material": row["Material"],
        "date": row["Date"],
        "volume_tons_year": int(row["Volume_Tons_Year"]),
        "current_price_eur": float(row["Current_Price_EUR"]),
        "price_trend": row["Price_Trend"],
        "macro_risk_factor": risk_factor if has_risk(risk_factor) else None,
        "macro_risk_value": risk_value if has_risk(risk_value) else None,
        "driver": driver,
        "driver_value": driver_value,
        "signal": rule["signal"],
        "rationale": rule["rationale"],
        "sentiment": "positive" if is_positive else "negative",
        "color": COLOR_POSITIVE if is_positive else COLOR_NEGATIVE,
    }


def main() -> None:
    rows = read_rows(DATA_FILE)
    signals = [build_signal(latest_row_for(rows, material)) for material in MATERIALS]

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_file": DATA_FILE.name,
        "as_of": signals[0]["date"] if signals else None,
        "legend": {"positive": COLOR_POSITIVE, "negative": COLOR_NEGATIVE},
        "signals": signals,
    }

    OUTPUT_FILE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    for signal in signals:
        print(f"{signal['material']}: {signal['signal']} — {signal['driver']}")


if __name__ == "__main__":
    main()
