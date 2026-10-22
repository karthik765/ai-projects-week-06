from __future__ import annotations

import re
from collections import defaultdict
from typing import Any


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold()).strip()


def validate_records(records: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for index, record in enumerate(records):
        if not isinstance(record.get("text"), str) or not record["text"].strip():
            errors.append(f"record {index}: text must be a non-empty string")
        if not isinstance(record.get("label"), str) or not record["label"].strip():
            errors.append(f"record {index}: label must be a non-empty string")
    return errors


def duplicate_groups(records: list[dict[str, Any]], normalized: bool = False) -> list[list[int]]:
    groups: dict[str, list[int]] = defaultdict(list)
    for index, record in enumerate(records):
        text = str(record.get("text", ""))
        key = normalize_text(text) if normalized else text
        groups[key].append(index)
    return [indices for indices in groups.values() if len(indices) > 1]
