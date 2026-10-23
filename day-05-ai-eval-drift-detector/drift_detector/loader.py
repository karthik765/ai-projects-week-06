import json
from pathlib import Path
from typing import Any


def load_records(path: str | Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line_number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON") from exc
        if not isinstance(record, dict) or not isinstance(record.get("id"), str) or not record["id"].strip():
            raise ValueError(f"{path}:{line_number}: id must be a non-empty string")
        if not isinstance(record.get("passed"), bool):
            raise ValueError(f"{path}:{line_number}: passed must be boolean")
        if record["id"] in seen:
            raise ValueError(f"{path}:{line_number}: duplicate id {record['id']}")
        for field in ("latency_ms", "cost_usd"):
            if field in record and (isinstance(record[field], bool) or not isinstance(record[field], (int, float)) or record[field] < 0):
                raise ValueError(f"{path}:{line_number}: {field} must be a non-negative number")
        seen.add(record["id"])
        records.append(record)
    return records
