from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterable, TextIO

from .models import BudgetReport, ModelRate, UsageRecord

DEFAULT_RATES: dict[str, ModelRate] = {
    "atlas-small": ModelRate(0.20, 0.80),
    "atlas-large": ModelRate(3.00, 12.00),
}


def _positive_int(value: object, name: str, line_number: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"line {line_number}: {name} must be a non-negative integer")
    return value


def parse_records(stream: TextIO) -> list[UsageRecord]:
    records: list[UsageRecord] = []
    for line_number, raw_line in enumerate(stream, 1):
        if not raw_line.strip():
            continue
        try:
            payload = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"line {line_number}: invalid JSON ({exc.msg})") from exc
        if not isinstance(payload, dict):
            raise ValueError(f"line {line_number}: record must be a JSON object")
        required = ("timestamp", "model", "input_tokens", "output_tokens")
        missing = [key for key in required if key not in payload]
        if missing:
            raise ValueError(f"line {line_number}: missing {', '.join(missing)}")
        timestamp = payload["timestamp"]
        model = payload["model"]
        if not isinstance(timestamp, str) or not timestamp.strip():
            raise ValueError(f"line {line_number}: timestamp must be a non-empty string")
        if not isinstance(model, str) or not model.strip():
            raise ValueError(f"line {line_number}: model must be a non-empty string")
        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"line {line_number}: timestamp must be ISO-8601") from exc
        records.append(UsageRecord(timestamp, model, _positive_int(payload["input_tokens"], "input_tokens", line_number), _positive_int(payload["output_tokens"], "output_tokens", line_number)))
    return records


def _day(timestamp: str) -> str:
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00")).date().isoformat()


def analyze_records(
    records: Iterable[UsageRecord],
    rates: dict[str, ModelRate] | None = None,
    total_budget_usd: float | None = None,
    daily_budget_usd: float | None = None,
) -> BudgetReport:
    catalog = dict(DEFAULT_RATES)
    if rates:
        catalog.update(rates)
    by_model: dict[str, float] = {}
    by_day: dict[str, float] = {}
    input_tokens = output_tokens = event_count = 0
    for record in records:
        if record.model not in catalog:
            raise ValueError(f"no pricing rate configured for model: {record.model}")
        cost = catalog[record.model].cost(record.input_tokens, record.output_tokens)
        by_model[record.model] = by_model.get(record.model, 0.0) + cost
        day = _day(record.timestamp)
        by_day[day] = by_day.get(day, 0.0) + cost
        input_tokens += record.input_tokens
        output_tokens += record.output_tokens
        event_count += 1
    total = sum(by_model.values())
    alerts: list[str] = []
    if total_budget_usd is not None and total > total_budget_usd:
        alerts.append(f"total budget exceeded by ${total - total_budget_usd:.4f}")
    if daily_budget_usd is not None:
        for day, cost in sorted(by_day.items()):
            if cost > daily_budget_usd:
                alerts.append(f"daily budget exceeded on {day} by ${cost - daily_budget_usd:.4f}")
    return BudgetReport(event_count, input_tokens, output_tokens, round(total, 6), {k: round(v, 6) for k, v in sorted(by_model.items())}, {k: round(v, 6) for k, v in sorted(by_day.items())}, total_budget_usd, daily_budget_usd, alerts)


def analyze_file(path: str | Path, **kwargs: object) -> BudgetReport:
    with Path(path).open(encoding="utf-8") as stream:
        return analyze_records(parse_records(stream), **kwargs)
