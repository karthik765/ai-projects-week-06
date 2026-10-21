from __future__ import annotations

import argparse
import json
import sys

from .analyzer import analyze_file
from .models import ModelRate


def _rates(values: list[str]) -> dict[str, ModelRate]:
    result: dict[str, ModelRate] = {}
    for value in values:
        try:
            model, prices = value.split("=", 1)
            input_price, output_price = prices.split(",", 1)
            result[model] = ModelRate(float(input_price), float(output_price))
        except (ValueError, TypeError) as exc:
            raise ValueError(f"invalid rate {value!r}; use MODEL=INPUT_PER_MILLION,OUTPUT_PER_MILLION") from exc
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize JSONL AI usage and estimate spend.")
    parser.add_argument("path", help="JSONL usage file")
    parser.add_argument("--budget", type=float, help="total budget in USD")
    parser.add_argument("--daily-budget", type=float, help="per-UTC-day budget in USD")
    parser.add_argument("--rate", action="append", default=[], metavar="MODEL=INPUT,OUTPUT", help="price per million tokens; repeatable")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = analyze_file(args.path, rates=_rates(args.rate) or None, total_budget_usd=args.budget, daily_budget_usd=args.daily_budget)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
        return 0
    print(f"Events: {report.event_count}")
    print(f"Tokens: {report.input_tokens:,} input / {report.output_tokens:,} output")
    print(f"Estimated cost: ${report.total_cost_usd:.4f}")
    print("By model:")
    for model, cost in report.by_model.items():
        print(f"  {model}: ${cost:.4f}")
    print("By UTC day:")
    for day, cost in report.by_day.items():
        print(f"  {day}: ${cost:.4f}")
    for alert in report.alerts:
        print(f"ALERT: {alert}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
