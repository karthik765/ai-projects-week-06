# Model Router

Choose an AI model for a request using explicit product constraints instead of hard-coded model names. The router filters models that cannot satisfy context-window or capability requirements, then ranks the remaining candidates by quality, latency, and estimated cost. Every decision includes reasons so it can be reviewed or logged.

This is a dependency-free reference implementation for offline planning, CI checks, and prototyping. It does not call an AI provider and does not require API keys.

## Structure

```text
model_router/
  catalog.py   Built-in model metadata and catalog loading
  policy.py    Request validation, filtering, scoring, and explanations
  cli.py       JSON/file command-line interface
tests/         unittest coverage for routing behavior
examples/      Example request and output command
```

## Run

Requires Python 3.10+.

```bash
python -m unittest discover -s tests -v
python -m model_router.cli examples/request.json
python -m model_router.cli examples/request.json --json
```

From the project directory, the CLI accepts a JSON request such as:

```json
{
  "task": "Summarize a support conversation",
  "min_quality": 0.75,
  "max_latency_ms": 900,
  "max_cost_per_million_tokens": 2.0,
  "context_tokens": 12000,
  "required_capabilities": ["text"]
}
```

The output contains the selected model, score, estimated cost, and rejected candidates. A request with no eligible model exits with a non-zero status and explains which constraints caused rejection.

## Design notes

- Scores are normalized and deterministic; the same catalog and request produce the same result.
- Hard constraints are applied before preferences, so an inexpensive model cannot win if it lacks context capacity or a required capability.
- Prices are illustrative metadata only. Replace the catalog with current provider pricing before production use.
- Keep secrets and provider credentials outside the repository.
