from collections.abc import Iterable
from typing import Any


def average(records: Iterable[dict[str, Any]], field: str) -> float:
    values = [float(item[field]) for item in records if field in item]
    return sum(values) / len(values) if values else 0.0


def pass_rate(records: list[dict[str, Any]]) -> float:
    return sum(1 for item in records if item["passed"]) / len(records) if records else 0.0


def relative_delta(before: float, after: float) -> float:
    return (after - before) / before if before else (1.0 if after else 0.0)
