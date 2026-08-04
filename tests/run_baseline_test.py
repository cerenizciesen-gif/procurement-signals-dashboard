"""Benchmark deterministic calculations and procurement decisions."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analyze_data import (  # noqa: E402
    MATERIALS,
    build_opportunity,
    decide,
    read_rows,
    series_for,
)

DATA_FILE = ROOT / "tests" / "data" / "procurement_baseline.csv"
RESULTS_DIR = ROOT / "tests" / "results"
RESULTS_FILE = RESULTS_DIR / "baseline_test_results.csv"
METRICS_FILE = RESULTS_DIR / "baseline_metrics.json"

EXPECTED = {
    "PP": {
        "annual_spend_eur": 702000.00,
        "monthly_trend_pct": 1.18,
        "delay_cost_eur": 49599.76,
        "signal": "Buy now",
        "driver": "Turkey minimum wage increase",
    },
    "PA6": {
        "annual_spend_eur": 3432000.00,
        "monthly_trend_pct": -0.86,
        "delay_cost_eur": -178060.52,
        "signal": "Buy now",
        "driver": "Red Sea shipping disruption",
    },
    "Steel": {
        "annual_spend_eur": 3925000.00,
        "monthly_trend_pct": 1.05,
        "delay_cost_eur": 246229.80,
        "signal": "Delay",
        "driver": "Geopolitical supply disruption",
    },
}

MONEY_TOLERANCE_EUR = 0.01
PERCENT_TOLERANCE = 0.01


def close_enough(actual: float, expected: float, tolerance: float) -> bool:
    return abs(actual - expected) <= tolerance


def main() -> None:
    rows = read_rows(DATA_FILE)
    results: list[dict[str, object]] = []

    for material in MATERIALS:
        material_rows = series_for(rows, material)
        latest = material_rows[-1]
        prices = [float(row["Current_Price_EUR"]) for row in material_rows]
        volume_tons = float(latest["Volume_Tons_Year"])

        opportunity = build_opportunity(material, prices, volume_tons)
        rule, driver, _, driver_origin = decide(latest, None)
        expected = EXPECTED[material]

        checks = {
            "annual_spend_correct": close_enough(
                float(opportunity["annual_spend_eur"]),
                expected["annual_spend_eur"],
                MONEY_TOLERANCE_EUR,
            ),
            "monthly_trend_correct": close_enough(
                float(opportunity["monthly_trend_pct"]),
                expected["monthly_trend_pct"],
                PERCENT_TOLERANCE,
            ),
            "delay_cost_correct": close_enough(
                float(opportunity["delay_cost_eur"]),
                expected["delay_cost_eur"],
                MONEY_TOLERANCE_EUR,
            ),
            "signal_correct": rule["signal"] == expected["signal"],
            "driver_correct": driver == expected["driver"],
            "driver_origin_correct": driver_origin == "dataset",
        }

        results.append(
            {
                "Material": material,
                "Actual_Annual_Spend_EUR": opportunity["annual_spend_eur"],
                "Expected_Annual_Spend_EUR": expected["annual_spend_eur"],
                "Annual_Spend_Correct": int(checks["annual_spend_correct"]),
                "Actual_Monthly_Trend_Pct": opportunity["monthly_trend_pct"],
                "Expected_Monthly_Trend_Pct": expected["monthly_trend_pct"],
                "Monthly_Trend_Correct": int(checks["monthly_trend_correct"]),
                "Actual_Delay_Cost_EUR": opportunity["delay_cost_eur"],
                "Expected_Delay_Cost_EUR": expected["delay_cost_eur"],
                "Delay_Cost_Correct": int(checks["delay_cost_correct"]),
                "Actual_Signal": rule["signal"],
                "Expected_Signal": expected["signal"],
                "Signal_Correct": int(checks["signal_correct"]),
                "Actual_Driver": driver,
                "Expected_Driver": expected["driver"],
                "Driver_Correct": int(checks["driver_correct"]),
                "Driver_Origin": driver_origin,
                "Overall_Pass": int(all(checks.values())),
            }
        )

    total_checks = len(results) * 6
    passed_checks = sum(
        int(row[field])
        for row in results
        for field in (
            "Annual_Spend_Correct",
            "Monthly_Trend_Correct",
            "Delay_Cost_Correct",
            "Signal_Correct",
            "Driver_Correct",
            "Overall_Pass",
        )
    )

    calculation_checks = sum(
        int(row[field])
        for row in results
        for field in (
            "Annual_Spend_Correct",
            "Monthly_Trend_Correct",
            "Delay_Cost_Correct",
        )
    )
    decision_checks = sum(
        int(row[field])
        for row in results
        for field in ("Signal_Correct", "Driver_Correct")
    )

    metrics = {
        "dataset": str(DATA_FILE.relative_to(ROOT)),
        "materials_tested": len(results),
        "calculation_accuracy": round(calculation_checks / 9, 4),
        "decision_accuracy": round(decision_checks / 6, 4),
        "materials_full_pass_rate": round(
            sum(int(row["Overall_Pass"]) for row in results) / len(results),
            4,
        ),
        "money_tolerance_eur": MONEY_TOLERANCE_EUR,
        "percentage_point_tolerance": PERCENT_TOLERANCE,
        "overall_pass": all(bool(row["Overall_Pass"]) for row in results),
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with RESULTS_FILE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)

    METRICS_FILE.write_text(
        json.dumps(metrics, indent=2) + "\n",
        encoding="utf-8",
    )

    print("\nBaseline benchmark results:")
    for row in results:
        print(
            f"  {row['Material']}: "
            f"spend EUR {row['Actual_Annual_Spend_EUR']:,.2f}, "
            f"trend {row['Actual_Monthly_Trend_Pct']:+.2f}%, "
            f"delay cost EUR {row['Actual_Delay_Cost_EUR']:,.2f}, "
            f"signal {row['Actual_Signal']}, "
            f"pass={bool(row['Overall_Pass'])}"
        )

    print(f"  Calculation accuracy: {metrics['calculation_accuracy']:.2%}")
    print(f"  Decision accuracy:    {metrics['decision_accuracy']:.2%}")
    print(f"  Overall pass:         {metrics['overall_pass']}")
    print(f"  Results written to {RESULTS_FILE.relative_to(ROOT)}")
    print(f"  Metrics written to {METRICS_FILE.relative_to(ROOT)}")

    if not metrics["overall_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
