import argparse
import json
import sys

from .detector import detect_drift
from .loader import load_records
from .models import Thresholds


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare baseline and candidate AI evaluation runs.")
    parser.add_argument("baseline")
    parser.add_argument("candidate")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--min-pass-rate-delta", type=float, default=-0.05)
    parser.add_argument("--latency-threshold", type=float, default=0.20)
    parser.add_argument("--cost-threshold", type=float, default=0.15)
    parser.add_argument("--min-cases", type=int, default=3)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = detect_drift(load_records(args.baseline), load_records(args.candidate), Thresholds(args.min_pass_rate_delta, args.latency_threshold, args.cost_threshold, args.min_cases))
    except ValueError as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2
    if args.as_json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(f"Matched {report.matched_count}/{report.baseline_count} baseline cases")
        print(f"Pass rate: {report.baseline_pass_rate:.1%} -> {report.candidate_pass_rate:.1%} ({report.pass_rate_delta:+.1%})")
        print(f"Latency: {report.baseline_latency_ms:.1f} -> {report.candidate_latency_ms:.1f} ms")
        print(f"Cost: ${report.baseline_cost_usd:.4f} -> ${report.candidate_cost_usd:.4f} per case")
        for finding in report.findings:
            label = finding.severity.upper()
            suffix = f" [{finding.case_id}]" if finding.case_id else ""
            print(f"{label} {finding.kind}{suffix}: {finding.message}")
    return 1 if report.regressed else 0
