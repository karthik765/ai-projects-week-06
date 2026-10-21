# AI Usage Budget Monitor

An offline, dependency-free utility for turning JSONL model usage events into an explainable spend and budget report. It is useful for development teams that need a quick answer to “which models are costing us money, and did we exceed the budget?” without sending telemetry to a third party.

## What it does

- Validates JSONL usage records and reports the line that failed.
- Estimates input and output token cost using a small, editable model-rate catalog.
- Aggregates spend by model and UTC calendar day.
- Compares totals with an optional total and per-day budget.
- Emits readable text or machine-friendly JSON from the command line.

This is an estimate: rates are examples and should be replaced with the prices used by your provider.

## Project structure

```text
usage_monitor/
  analyzer.py     parsing, pricing, aggregation, and budget checks
  cli.py          command-line interface
  models.py       typed report objects and rate catalog
examples/
  usage.jsonl     sample events
tests/
  test_analyzer.py
```

## Requirements

- Python 3.10+
- No third-party packages

## Run it

From this directory:

```bash
python -m usage_monitor.cli examples/usage.jsonl --budget 0.10 --daily-budget 0.06
python -m usage_monitor.cli examples/usage.jsonl --budget 0.10 --json
```

The input format is one object per line:

```json
{"timestamp":"2026-10-21T12:00:00Z","model":"atlas-small","input_tokens":1200,"output_tokens":300}
```

Use `--rate MODEL=INPUT_PER_MILLION,OUTPUT_PER_MILLION` to override or add a model rate. Repeat the option for multiple models.

## Test

```bash
python -m unittest discover -s tests -v
```

The tests cover validation, token pricing, aggregation, daily budgets, custom rates, and JSON serialization.
