# AI Batch Planner

Turn a JSONL queue of AI jobs into an explainable, rate-limit-aware execution plan. The planner validates requests, estimates token cost, groups jobs into waves, and flags jobs that exceed per-request limits without calling an API.

## Features

- deterministic ordering by priority, deadline, and input order
- configurable requests-per-minute and tokens-per-minute limits
- per-job and per-wave token and cost estimates
- validation errors and capacity warnings in the output
- human-readable and JSON CLI output
- standard-library-only implementation

## Setup

Requires Python 3.10 or newer. No third-party packages are needed.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

## Run

```powershell
python -m batch_planner examples/jobs.jsonl --rpm 3 --tpm 1800 --json
python -m batch_planner examples/jobs.jsonl --rpm 2 --tpm 1000
```

The input is one JSON object per line. `id`, `model`, `input_tokens`, and `output_tokens` are required; `priority` (higher first), `max_cost_usd`, and `deadline_minutes` are optional. Model pricing is supplied with `--price model=input_price,output_price` and can be repeated.

```json
{"id":"refund-001","model":"swift","input_tokens":420,"output_tokens":180,"priority":2}
```

The planner is an estimate: actual provider tokenization and server-side scheduling can differ. Review warnings before dispatching jobs.

## Test

```powershell
python -m unittest discover -s tests -v
```

