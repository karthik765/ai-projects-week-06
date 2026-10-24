from dataclasses import dataclass, field


@dataclass(frozen=True)
class Job:
    id: str
    model: str
    input_tokens: int
    output_tokens: int
    priority: int = 0
    max_cost_usd: float | None = None
    deadline_minutes: float | None = None

    @property
    def tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass
class Wave:
    number: int
    start_minute: float
    jobs: list[Job] = field(default_factory=list)
    tokens: int = 0
    cost_usd: float = 0.0


@dataclass
class Plan:
    waves: list[Wave]
    rejected: list[dict]
    warnings: list[str]
    total_cost_usd: float
    total_tokens: int

    def as_dict(self) -> dict:
        return {
            "waves": [{"number": w.number, "start_minute": w.start_minute,
                       "tokens": w.tokens, "cost_usd": round(w.cost_usd, 8),
                       "jobs": [j.id for j in w.jobs]} for w in self.waves],
            "rejected": self.rejected,
            "warnings": self.warnings,
            "total_cost_usd": round(self.total_cost_usd, 8),
            "total_tokens": self.total_tokens,
        }

