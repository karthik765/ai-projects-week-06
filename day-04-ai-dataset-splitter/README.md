# AI Dataset Splitter

Prepare small JSONL classification datasets for model training or evaluation without accidentally putting duplicates in different splits. The splitter validates records, uses a stable hash for deterministic assignment, preserves label proportions as closely as possible, and reports exact and normalized-text leakage.

## Features

- deterministic seeded train/validation/test assignment
- approximate stratification by label, including clear small-class warnings
- exact duplicate and normalized-text duplicate detection
- validation for required fields, blank text, and invalid labels
- human-readable or JSON reports
- standard-library-only implementation

## Setup

Requires Python 3.10 or newer. No third-party packages are needed.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

## Run

```powershell
python -m dataset_splitter examples/tickets.jsonl --output-dir out --seed 42
python -m dataset_splitter examples/tickets.jsonl --output-dir out --json
```

The command writes `train.jsonl`, `validation.jsonl`, and `test.jsonl`, plus a summary report. Use `--ratios 0.8,0.1,0.1` to customize split proportions. Every output record retains its original fields and adds no secret data.

## Test

```powershell
python -m unittest discover -s tests -v
```

## Input format

One JSON object per line with a non-empty `text` field and a `label` field, for example:

```json
{"id":"1","text":"The card was declined","label":"billing"}
```

The tool is a preparation aid, not a substitute for domain review. Hash-based assignment is reproducible, but it cannot identify semantic leakage that uses different wording.
