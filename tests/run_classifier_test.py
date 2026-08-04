"""Run the fixed DeepSeek headline benchmark and calculate quality metrics."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from monitor_sources import ANTHROPIC_MODEL, classify_by_model  # noqa: E402

GOLD_FILE = ROOT / "tests" / "data" / "headlines_gold.csv"
RESULTS_DIR = ROOT / "tests" / "results"
RESULTS_FILE = RESULTS_DIR / "headlines_test_results.csv"
METRICS_FILE = RESULTS_DIR / "headlines_metrics.json"


def as_bool(value: str) -> bool:
    return value.strip().lower() in {"true", "1", "yes"}


def safe_ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is missing.")

    with GOLD_FILE.open(newline="", encoding="utf-8-sig") as handle:
        gold_rows = list(csv.DictReader(handle))

    headlines = [
        {
            "title": row["Headline"],
            "link": "",
            "published": "",
            "query": "fixed gold benchmark",
        }
        for row in gold_rows
    ]

    findings = classify_by_model(headlines, api_key)
    if findings is None:
        raise RuntimeError("Model classification failed; benchmark cannot be scored.")

    predicted_by_headline = {
        str(item["headline"]): item
        for item in findings
    }

    tp = fp = fn = tn = 0
    exact_correct = 0
    risk_correct = 0
    material_correct = 0
    relevant_count = 0
    result_rows: list[dict[str, object]] = []

    for row in gold_rows:
        headline = row["Headline"]
        expected_relevant = as_bool(row["Expected_Relevant"])
        expected_risk = row["Expected_Risk"].strip()
        expected_materials = {
            value.strip()
            for value in row["Expected_Materials"].split(";")
            if value.strip()
        }

        predicted = predicted_by_headline.get(headline)
        predicted_relevant = predicted is not None
        predicted_risk = str(predicted.get("risk_factor", "")) if predicted else ""
        predicted_materials = (
            {str(value) for value in predicted.get("materials", [])}
            if predicted
            else set()
        )

        if expected_relevant and predicted_relevant:
            tp += 1
        elif not expected_relevant and predicted_relevant:
            fp += 1
        elif expected_relevant and not predicted_relevant:
            fn += 1
        else:
            tn += 1

        risk_match = (
            not expected_relevant
            or (predicted_relevant and predicted_risk == expected_risk)
        )
        material_match = (
            not expected_relevant
            or (predicted_relevant and predicted_materials == expected_materials)
        )
        exact_match = (
            expected_relevant == predicted_relevant
            and risk_match
        )

        if expected_relevant:
            relevant_count += 1
            risk_correct += int(risk_match)
            material_correct += int(material_match)

        exact_correct += int(exact_match)

        result_rows.append(
            {
                "ID": row["ID"],
                "Headline": headline,
                "Expected_Relevant": expected_relevant,
                "Expected_Risk": expected_risk,
                "Expected_Materials": ";".join(sorted(expected_materials)),
                "Predicted_Relevant": predicted_relevant,
                "Predicted_Risk": predicted_risk,
                "Predicted_Materials": ";".join(sorted(predicted_materials)),
                "Risk_Correct": int(risk_match),
                "Materials_Correct": int(material_match),
                "Exact_Correct": int(exact_match),
            }
        )

    precision = safe_ratio(tp, tp + fp)
    recall = safe_ratio(tp, tp + fn)
    f1 = (
        round(2 * precision * recall / (precision + recall), 4)
        if precision + recall
        else 0.0
    )

    metrics = {
        "model": ANTHROPIC_MODEL,
        "dataset": str(GOLD_FILE.relative_to(ROOT)),
        "total_headlines": len(gold_rows),
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "true_negative": tn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "exact_classification_accuracy": safe_ratio(exact_correct, len(gold_rows)),
        "risk_accuracy_relevant_cases": safe_ratio(risk_correct, relevant_count),
        "material_mapping_accuracy_relevant_cases": safe_ratio(
            material_correct,
            relevant_count,
        ),
        "json_parse_success": True,
        "acceptance_targets": {
            "precision_min": 0.80,
            "recall_min": 0.80,
            "f1_min": 0.80,
            "exact_classification_accuracy_min": 0.80,
        },
    }
    metrics["overall_pass"] = all(
        [
            precision >= 0.80,
            recall >= 0.80,
            f1 >= 0.80,
            metrics["exact_classification_accuracy"] >= 0.80,
        ]
    )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with RESULTS_FILE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result_rows[0].keys()))
        writer.writeheader()
        writer.writerows(result_rows)

    METRICS_FILE.write_text(
        json.dumps(metrics, indent=2) + "\n",
        encoding="utf-8",
    )

    print("\nClassifier benchmark results:")
    print(f"  Precision: {precision:.2%}")
    print(f"  Recall:    {recall:.2%}")
    print(f"  F1:        {f1:.2%}")
    print(
        "  Exact classification accuracy: "
        f"{metrics['exact_classification_accuracy']:.2%}"
    )
    print(f"  Overall pass: {metrics['overall_pass']}")
    print(f"  Results written to {RESULTS_FILE.relative_to(ROOT)}")
    print(f"  Metrics written to {METRICS_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
