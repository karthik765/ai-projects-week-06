import argparse
import json

from .loader import load_jobs
from .planner import DEFAULT_PRICES, plan_jobs


def _prices(values):
    prices = dict(DEFAULT_PRICES)
    for value in values:
        model, input_price, output_price = value.split(",")
        prices[model] = (float(input_price), float(output_price))
    return prices


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan rate-limited AI batch jobs")
    parser.add_argument("jobs")
    parser.add_argument("--rpm", type=int, default=5)
    parser.add_argument("--tpm", type=int, default=4000)
    parser.add_argument("--price", action="append", default=[], metavar="MODEL,INPUT,OUTPUT")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    jobs, errors = load_jobs(args.jobs)
    result = plan_jobs(jobs, args.rpm, args.tpm, _prices(args.price), errors)
    if args.as_json:
        print(json.dumps(result.as_dict(), indent=2))
    else:
        print(f"Plan: {len(result.waves)} wave(s), {result.total_tokens} tokens, ${result.total_cost_usd:.6f}")
        for wave in result.waves:
            print(f"  Wave {wave.number} at minute {wave.start_minute:.1f}: {', '.join(w.id for w in wave.jobs)} ({wave.tokens} tokens)")
        for warning in result.warnings:
            print(f"WARNING: {warning}")
    return 1 if result.rejected else 0

