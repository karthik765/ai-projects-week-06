from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class ModelRate:
    input_per_million: float
    output_per_million: float

    def cost(self, input_tokens: int, output_tokens: int) -> float:
        return (input_tokens * self.input_per_million + output_tokens * self.output_per_million) / 1_000_000


@dataclass(frozen=True)
class UsageRecord:
    timestamp: str
    model: str
    input_tokens: int
    output_tokens: int


@dataclass
class BudgetReport:
    event_count: int
    input_tokens: int
    output_tokens: int
    total_cost_usd: float
    by_model: dict[str, float]
    by_day: dict[str, float]
    total_budget_usd: float | None = None
    daily_budget_usd: float | None = None
    alerts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
