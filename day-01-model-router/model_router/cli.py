"""Command-line interface for the model router."""

import argparse
import json
import sys
from pathlib import Path

from .catalog import default_catalog
from .policy import RouteRequest, RoutingError, route


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Choose an AI model from explicit constraints")
    parser.add_argument("request", type=Path, help="JSON request file")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args(argv)
    try:
        request = RouteRequest.from_dict(json.loads(args.request.read_text(encoding="utf-8")))
        result = route(request, default_catalog())
    except (OSError, json.JSONDecodeError, RoutingError, TypeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Selected: {result['selected_model']} (score {result['score']:.4f})")
        print(f"Estimated cost: ${result['estimated_cost_per_million_tokens']:.2f}/M tokens")
        print("Eligible order: " + ", ".join(result["eligible_models"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
