from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .loader import load_jsonl, write_jsonl
from .models import SplitRatios
from .splitter import split_records


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create deterministic, leakage-aware JSONL dataset splits.")
    parser.add_argument("path", help="input JSONL dataset")
    parser.add_argument("--output-dir", default="out", help="directory for split files")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--ratios", default="0.8,0.1,0.1", help="train,validation,test ratios")
    parser.add_argument("--json", action="store_true", help="emit the report as JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        ratios = SplitRatios(*(float(value) for value in args.ratios.split(",")))
        splits, report = split_records(load_jsonl(args.path), ratios, args.seed)
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        for name, records in splits.items():
            write_jsonl(output_dir / f"{name}.jsonl", records)
        (output_dir / "report.json").write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(f"Records: {report.total_records}")
        print("Splits: " + ", ".join(f"{name}={count}" for name, count in report.split_counts.items()))
        print(f"Exact duplicate groups: {len(report.exact_duplicate_groups)}")
        print(f"Normalized duplicate groups: {len(report.normalized_duplicate_groups)}")
        for warning in report.warnings:
            print(f"WARNING: {warning}")
    return 0
