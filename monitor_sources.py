"""Market monitor — turns external events into structured macro risks.

This closes the gap the concept called "News- und Industry-Monitoring": until now the macro
risk was typed into the dataset by hand, so the system used a risk a human had already
identified. This script identifies it instead.

Two sources, both public and free, neither needing a credential:

  1. The Turkish central bank publishes the daily USD/TRY reference rate as XML. The rate is
     read for today and for roughly thirty days ago, and the change is computed in code.
  2. A news search feed is queried for a small set of procurement-relevant topics. Headlines
     are then classified into the project's macro risk taxonomy.

Classification runs in one of two modes, mirroring the argument generation in
analyze_data.py:

  * with an API key   — a language model reads each headline and decides whether it is
                        relevant, which risk it belongs to and which materials it touches
  * without a key     — keyword rules flag candidates; honest pattern matching, not a model

Every finding records how it was produced, so the dashboard and the test can distinguish
model output from rule output. Network failures never abort the run: a source that cannot be
reached is recorded as unavailable and the rest continues.

Output: macro_signals.json. Read by analyze_data.py, which stays authoritative for money.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

OUTPUT_FILE = Path("macro_signals.json")

MATERIALS = ("PP", "PA6", "Steel")

REQUEST_TIMEOUT = 25
USER_AGENT = "procurement-monitor/1.0"

# --- Exchange rate -------------------------------------------------------------------

TCMB_URL = "https://www.tcmb.gov.tr/kurlar/{yyyymm}/{ddmmyyyy}.xml"
TCMB_TODAY_URL = "https://www.tcmb.gov.tr/kurlar/today.xml"
FX_LOOKBACK_DAYS = 30
# Move in USD/TRY over the lookback window that counts as a macro risk, in percent.
FX_ALERT_THRESHOLD = 3.0

# --- News ----------------------------------------------------------------------------

NEWS_URL = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
NEWS_QUERIES = [
    "Red Sea shipping container freight rates",
    "Turkey minimum wage decision",
    "steel scrap price Turkey mill",
    "polypropylene polyamide resin supply Europe",
    "export ban sanctions raw material supply disruption",
]
HEADLINES_PER_QUERY = 6
MAX_HEADLINES_CLASSIFIED = 24

# The taxonomy the rest of the system understands. A finding that does not fit one of these
# is discarded rather than invented into a new category.
RISK_TAXONOMY = {
    "Turkey minimum wage increase": {
        "materials": ["PP", "PA6", "Steel"],
        "keywords": ["minimum wage", "asgari ucret", "asgari ücret", "wage hike", "wage increase"],
    },
    "Red Sea shipping disruption": {
        "materials": ["PA6", "PP"],
        "keywords": ["red sea", "houthi", "suez", "freight rate", "container rate", "shipping disruption", "rerouting"],
    },
    "Geopolitical supply disruption": {
        "materials": ["Steel", "PA6", "PP"],
        "keywords": ["export ban", "sanction", "port closure", "strike", "supply disruption", "force majeure", "embargo"],
    },
}

# --- Generative classification -------------------------------------------------------

ANTHROPIC_URL = "https://api.deepseek.com/anthropic/v1/messages"
ANTHROPIC_MODEL = "deepseek-v4-flash"
ANTHROPIC_VERSION = "2023-06-01"
MAX_TOKENS = 3500

CLASSIFIER_SYSTEM_PROMPT = (
    "You screen news headlines for a procurement team that buys Steel, PA6 and PP for "
    "automotive production in Turkey.\n\n"
    "For each headline decide whether it describes an event that would move the purchase "
    "price of one of those materials in Turkey.\n\n"
    "Rules you must follow:\n"
    "1. Classify only into these three categories, using the exact wording:\n"
    "   - Turkey minimum wage increase\n"
    "   - Red Sea shipping disruption\n"
    "   - Geopolitical supply disruption\n"
    "   If a headline fits none of them, mark it as not relevant. Never invent a category.\n"
    "2. Judge only what the headline states. Do not infer facts that are not there, and "
    "never invent a number, a percentage or a date.\n"
    "3. Only extract a value if the headline itself contains one. Otherwise use null.\n"
    "4. Severity is one of low, medium, high — your assessment of the price impact.\n"
    "5. Reply with a JSON array and nothing else. No prose, no code fence.\n\n"
    "Each element must be exactly:\n"
    '{"index": <int>, "relevant": <bool>, "risk_factor": <string or null>, '
    '"materials": [<subset of PP, PA6, Steel>], "value": <string or null>, '
    '"severity": <"low"|"medium"|"high"|null>}'
)


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
        return response.read()


# --- Exchange rate -------------------------------------------------------------------


def tcmb_rate_on(day: datetime) -> tuple[float, str] | None:
    """USD/TRY selling rate for a given day, walking back over weekends and holidays."""
    for offset in range(7):
        target = day - timedelta(days=offset)
        url = TCMB_URL.format(yyyymm=target.strftime("%Y%m"), ddmmyyyy=target.strftime("%d%m%Y"))
        try:
            root = ET.fromstring(fetch(url))
        except (urllib.error.URLError, urllib.error.HTTPError, ET.ParseError):
            continue
        for currency in root.findall("Currency"):
            if currency.get("CurrencyCode") == "USD":
                text = (currency.findtext("ForexSelling") or "").strip()
                if text:
                    return float(text), target.strftime("%Y-%m-%d")
    return None


def read_exchange_rate() -> dict[str, object]:
    today = datetime.now(timezone.utc)
    current = tcmb_rate_on(today)
    if current is None:
        try:
            root = ET.fromstring(fetch(TCMB_TODAY_URL))
            for currency in root.findall("Currency"):
                if currency.get("CurrencyCode") == "USD":
                    text = (currency.findtext("ForexSelling") or "").strip()
                    if text:
                        current = (float(text), today.strftime("%Y-%m-%d"))
        except (urllib.error.URLError, urllib.error.HTTPError, ET.ParseError):
            current = None

    if current is None:
        print("  exchange rate: source unavailable")
        return {"available": False, "source": "Turkish central bank daily reference rate"}

    rate, rate_date = current
    past = tcmb_rate_on(today - timedelta(days=FX_LOOKBACK_DAYS))
    result: dict[str, object] = {
        "available": True,
        "source": "Turkish central bank daily reference rate",
        "pair": "USD/TRY",
        "rate": round(rate, 4),
        "rate_date": rate_date,
    }

    if past:
        past_rate, past_date = past
        change = ((rate - past_rate) / past_rate) * 100
        result.update(
            {
                "reference_rate": round(past_rate, 4),
                "reference_date": past_date,
                "change_pct": round(change, 2),
                "lookback_days": FX_LOOKBACK_DAYS,
                # A weaker lira raises the local cost of imported raw materials.
                "is_risk": change >= FX_ALERT_THRESHOLD,
            }
        )
        print(f"  exchange rate: {rate:.4f} ({change:+.2f}% over {FX_LOOKBACK_DAYS} days)")
    else:
        print(f"  exchange rate: {rate:.4f} (no reference value for the lookback window)")

    return result


# --- News ----------------------------------------------------------------------------


def strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()


def read_headlines() -> tuple[list[dict[str, str]], list[str]]:
    headlines: list[dict[str, str]] = []
    failed: list[str] = []
    seen: set[str] = set()

    for query in NEWS_QUERIES:
        url = NEWS_URL.format(query=urllib.parse.quote(query))
        try:
            root = ET.fromstring(fetch(url))
        except (urllib.error.URLError, urllib.error.HTTPError, ET.ParseError) as error:
            print(f"  news source unavailable for '{query}': {error}")
            failed.append(query)
            continue

        for item in root.findall(".//item")[:HEADLINES_PER_QUERY]:
            title = strip_tags(item.findtext("title") or "")
            if not title or title in seen:
                continue
            seen.add(title)
            headlines.append(
                {
                    "title": title,
                    "link": (item.findtext("link") or "").strip(),
                    "published": (item.findtext("pubDate") or "").strip(),
                    "query": query,
                }
            )

    print(f"  news: {len(headlines)} headlines retrieved from {len(NEWS_QUERIES) - len(failed)} of {len(NEWS_QUERIES)} queries")
    return headlines[:MAX_HEADLINES_CLASSIFIED], failed


def classify_by_keywords(headlines: list[dict[str, str]]) -> list[dict[str, object]]:
    findings = []
    for headline in headlines:
        lowered = headline["title"].lower()
        for risk_factor, spec in RISK_TAXONOMY.items():
            hit = next((k for k in spec["keywords"] if k in lowered), None)
            if not hit:
                continue
            findings.append(
                {
                    "risk_factor": risk_factor,
                    "materials": spec["materials"],
                    "value": None,
                    "severity": "medium",
                    "headline": headline["title"],
                    "link": headline["link"],
                    "published": headline["published"],
                    "matched_on": hit,
                    "method": "keyword rules",
                }
            )
            break
    return findings


def classify_by_model(
    headlines: list[dict[str, str]],
    api_key: str,
) -> list[dict[str, object]] | None:
    numbered = "\n".join(
        f"{i}. {headline['title']}"
        for i, headline in enumerate(headlines)
    )

    payload = json.dumps(
        {
            "model": ANTHROPIC_MODEL,
            "max_tokens": 3500,
            "thinking": {"type": "disabled"},
            "system": CLASSIFIER_SYSTEM_PROMPT,
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Headlines:\n{numbered}\n\n"
                        "Return exactly one valid JSON array. "
                        "Do not use Markdown or code fences. "
                        "The first character must be [ and the last character must be ]."
                    ),
                }
            ],
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
        with urllib.request.urlopen(request, timeout=90) as response:
            body = json.loads(response.read().decode("utf-8"))

        text = "".join(
            block.get("text", "")
            for block in body.get("content", [])
            if block.get("type") == "text"
        ).strip()

        if not text:
            raise ValueError(
                "Model returned empty text. "
                f"stop_reason={body.get('stop_reason')}, "
                f"usage={body.get('usage')}"
            )

        # Remove Markdown fences if the model added them.
        text = re.sub(
            r"^\s*```(?:json)?\s*|\s*```\s*$",
            "",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        ).strip()

        # Extract only the JSON array if explanatory text was added.
        array_start = text.find("[")
        array_end = text.rfind("]")

        if array_start == -1 or array_end == -1 or array_end < array_start:
            raise ValueError(
                f"No JSON array found in model response: {text[:200]!r}"
            )

        parsed = json.loads(text[array_start : array_end + 1])

        if not isinstance(parsed, list):
            raise ValueError("Model response is valid JSON but is not an array.")

    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        json.JSONDecodeError,
        ValueError,
        KeyError,
    ) as error:
        print(
            f"  classification failed ({error}), "
            "falling back to keyword rules"
        )
        return None

    findings: list[dict[str, object]] = []

    for entry in parsed:
        if not isinstance(entry, dict) or not entry.get("relevant"):
            continue

        risk_factor = entry.get("risk_factor")

        # Discard categories outside the predefined taxonomy.
        if risk_factor not in RISK_TAXONOMY:
            continue

        index = entry.get("index")
        if not isinstance(index, int) or not 0 <= index < len(headlines):
            continue

        materials = [
            material
            for material in entry.get("materials", [])
            if material in MATERIALS
        ]

        findings.append(
            {
                "risk_factor": risk_factor,
                "materials": (
                    materials
                    or RISK_TAXONOMY[risk_factor]["materials"]
                ),
                "value": entry.get("value"),
                "severity": entry.get("severity") or "medium",
                "headline": headlines[index]["title"],
                "link": headlines[index]["link"],
                "published": headlines[index]["published"],
                "matched_on": None,
                "method": ANTHROPIC_MODEL,
            }
        )

    print(
        f"  classification: {len(findings)} relevant "
        f"of {len(headlines)} headlines, by {ANTHROPIC_MODEL}"
    )

    return findings


def summarise_by_material(findings: list[dict[str, object]], fx: dict[str, object]) -> dict[str, object]:
    """Strongest finding per material, so downstream code has one clear input each."""
    order = {"high": 3, "medium": 2, "low": 1}
    summary: dict[str, object] = {}

    for material in MATERIALS:
        relevant = [f for f in findings if material in f["materials"]]
        if not relevant:
            summary[material] = None
            continue
        strongest = max(relevant, key=lambda f: order.get(f.get("severity"), 0))
        summary[material] = {
            "risk_factor": strongest["risk_factor"],
            "value": strongest["value"],
            "severity": strongest["severity"],
            "headline": strongest["headline"],
            "method": strongest["method"],
        }

    # The exchange rate is a measured figure rather than a headline, so it is offered
    # separately and only when it actually breaches the threshold.
    if fx.get("is_risk"):
        for material in MATERIALS:
            if summary[material] is None:
                summary[material] = {
                    "risk_factor": "USD/TRY rate surge",
                    "value": f"{fx['change_pct']:+.2f}% over {fx['lookback_days']} days",
                    "severity": "medium",
                    "headline": f"USD/TRY at {fx['rate']} (central bank reference rate)",
                    "method": "measured",
                }
    return summary


def main() -> None:
    print("Scanning external sources:")
    fx = read_exchange_rate()
    headlines, failed_queries = read_headlines()

    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    findings = None
    if headlines and api_key:
        findings = classify_by_model(headlines, api_key)
    elif headlines:
        print("  no API key configured, using keyword rules")

    method = ANTHROPIC_MODEL
    if findings is None:
        findings = classify_by_keywords(headlines)
        method = "keyword rules"
        print(f"  classification: {len(findings)} relevant of {len(headlines)} headlines, by keyword rules")

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "classification_method": method,
        "sources": {
            "exchange_rate": fx,
            "news": {
                "queries": NEWS_QUERIES,
                "unavailable_queries": failed_queries,
                "headlines_screened": len(headlines),
            },
        },
        "findings": findings,
        "by_material": summarise_by_material(findings, fx),
    }

    OUTPUT_FILE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("\nDetected macro risks:")
    for material in MATERIALS:
        entry = payload["by_material"][material]
        print(f"  {material}: {entry['risk_factor'] if entry else 'none detected'}")


if __name__ == "__main__":
    main()
