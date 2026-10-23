# AI Eval Drift Detector

Compare two JSONL evaluation runs and turn subtle model regressions into an explainable release report. The detector matches cases by ID, compares pass rates and numeric metrics, and highlights missing cases, new failures, slower responses, and higher estimated costs.

## Features

- baseline-versus-candidate comparison by stable case ID
- aggregate pass rate, failure rate, latency, and cost deltas
- configurable regression thresholds and minimum sample count
- per-case findings for newly failing, recovered, missing, or changed cases
- human-readable and JSON output
- standard-library-only implementation

## Setup

Requires Python 3.10 or newer. No third-party packages are needed.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

## Run

```powershell
python -m drift_detector examples/baseline.jsonl examples/candidate.jsonl
python -m drift_detector examples/baseline.jsonl examples/candidate.jsonl --json --min-pass-rate-delta -0.03
```

The command exits with status 1 when a regression is detected, which makes it suitable for CI. Use `--latency-threshold 0.20` and `--cost-threshold 0.15` to change relative thresholds.

## Input format

One JSON object per line. Required fields are `id` and boolean `passed`; `latency_ms` and `cost_usd` are optional numeric metrics.

```json
{"id":"refund-01","passed":true,"latency_ms":410,"cost_usd":0.002}
```

Case IDs should be stable across runs. A missing case is reported separately from a failed case so evaluation-set changes are visible rather than silently counted as regressions.

## Test

```powershell
python -m unittest discover -s tests -v
```

This is a release-signal tool, not a statistical significance test. For small evaluation sets, review findings manually before blocking a deployment.
