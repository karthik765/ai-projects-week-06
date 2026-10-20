# AI Response Diff

A dependency-free reviewer for comparing two AI responses. It finds added and removed sentences, highlights changed numbers, detects risk-sensitive wording, and produces a review score so a prompt or model change can be checked before release.

## Why it is useful

Text diffs are noisy for model output: a response can be rewritten without changing meaning, or a tiny number/permission change can matter a lot. This tool combines sentence-level changes with targeted checks for numbers, URLs, and risk words. It is a triage aid, not a substitute for human review.

## Quick start

Requires Python 3.10+ and no third-party packages.

```powershell
python -m unittest discover -s tests -v
python -m response_diff.cli --baseline examples/baseline.txt --candidate examples/candidate.txt
python -m response_diff.cli --baseline examples/baseline.txt --candidate examples/candidate.txt --json
```

The human-readable report includes a score from 0 (low review effort) to 100 (high review effort), changed sentences, numeric changes, and risk signals. The JSON form is suitable for CI artifacts.

## Package layout

- `response_diff/models.py` - typed report and finding objects.
- `response_diff/analyzer.py` - sentence, token, number, URL, and risk analysis.
- `response_diff/cli.py` - command-line interface and rendering.
- `examples/` - a small before/after response pair.
- `tests/` - automated behavior tests.

## Limits

The analyzer uses deterministic lexical heuristics. It does not claim semantic equivalence, verify facts, or call an AI service. Review high-scoring changes manually, especially when a number, URL, safety instruction, or authorization phrase changes.
