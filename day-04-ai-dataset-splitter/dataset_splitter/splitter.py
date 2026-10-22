from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from typing import Any

from .checks import duplicate_groups, validate_records
from .models import SplitRatios, SplitReport


def _bucket(seed: int, record: dict[str, Any]) -> float:
    identity = f"{seed}\0{record.get('text', '')}\0{record.get('label', '')}"
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    return int(digest[:16], 16) / 16**16


def split_records(records: list[dict[str, Any]], ratios: SplitRatios | None = None, seed: int = 42) -> tuple[dict[str, list[dict[str, Any]]], SplitReport]:
    ratios = ratios or SplitRatios()
    ratios.validate()
    errors = validate_records(records)
    if errors:
        raise ValueError("; ".join(errors))
    names = ("train", "validation", "test")
    targets = {name: ratio * len(records) for name, ratio in zip(names, (ratios.train, ratios.validation, ratios.test))}
    names = ("train", "validation", "test")
    # Set exact global capacities, then fill each label toward its proportional target.
    capacities = {name: int(targets[name]) for name in names}
    for name in sorted(names, key=lambda item: targets[item] - capacities[item], reverse=True)[: len(records) - sum(capacities.values())]:
        capacities[name] += 1
    label_totals = Counter(str(record["label"]) for record in records)
    label_targets = {
        label: {name: label_totals[label] * getattr(ratios, name) for name in names}
        for label in label_totals
    }
    label_assigned = {label: Counter() for label in label_totals}
    output = {name: [] for name in names}
    by_label: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_label[str(record["label"])].append(record)
    for label, label_records in by_label.items():
        for record in sorted(label_records, key=lambda item: _bucket(seed, item)):
            available = [name for name in names if capacities[name] > 0]
            choice = max(available, key=lambda name: (label_targets[label][name] - label_assigned[label][name], capacities[name]))
            capacities[choice] -= 1
            label_assigned[label][choice] += 1
            output[choice].append({key: value for key, value in record.items() if key != "_line"})
    label_counts = {name: dict(Counter(str(record["label"]) for record in values)) for name, values in output.items()}
    warnings: list[str] = []
    for label, count in Counter(str(record["label"]) for record in records).items():
        if count < 3:
            warnings.append(f"label {label!r} has only {count} record(s); stratification is limited")
    report = SplitReport(len(records), {name: len(values) for name, values in output.items()}, label_counts, duplicate_groups(records), duplicate_groups(records, normalized=True), warnings)
    if report.normalized_duplicate_groups:
        warnings.append("normalized duplicate groups may leak similar examples across splits")
    return output, report
