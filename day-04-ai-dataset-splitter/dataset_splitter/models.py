from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class SplitRatios:
    train: float = 0.8
    validation: float = 0.1
    test: float = 0.1

    def validate(self) -> None:
        values = (self.train, self.validation, self.test)
        if any(value <= 0 for value in values) or abs(sum(values) - 1.0) > 1e-9:
            raise ValueError("split ratios must be positive and sum to 1")


@dataclass
class SplitReport:
    total_records: int
    split_counts: dict[str, int]
    label_counts: dict[str, dict[str, int]]
    exact_duplicate_groups: list[list[int]] = field(default_factory=list)
    normalized_duplicate_groups: list[list[int]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
