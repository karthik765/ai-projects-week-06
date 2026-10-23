from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Thresholds:
    min_pass_rate_delta: float = -0.05
    latency_relative: float = 0.20
    cost_relative: float = 0.15
    min_cases: int = 3


@dataclass
class Finding:
    kind: str
    case_id: str | None
    message: str
    severity: str = "warning"

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "case_id": self.case_id, "message": self.message, "severity": self.severity}


@dataclass
class DriftReport:
    baseline_count: int
    candidate_count: int
    matched_count: int
    baseline_pass_rate: float
    candidate_pass_rate: float
    pass_rate_delta: float
    baseline_latency_ms: float
    candidate_latency_ms: float
    latency_delta: float
    baseline_cost_usd: float
    candidate_cost_usd: float
    cost_delta: float
    findings: list[Finding] = field(default_factory=list)

    @property
    def regressed(self) -> bool:
        return any(f.severity == "error" for f in self.findings)

    def to_dict(self) -> dict[str, Any]:
        return {"baseline_count": self.baseline_count, "candidate_count": self.candidate_count,
                "matched_count": self.matched_count, "baseline_pass_rate": round(self.baseline_pass_rate, 4),
                "candidate_pass_rate": round(self.candidate_pass_rate, 4), "pass_rate_delta": round(self.pass_rate_delta, 4),
                "baseline_latency_ms": round(self.baseline_latency_ms, 2), "candidate_latency_ms": round(self.candidate_latency_ms, 2),
                "latency_delta": round(self.latency_delta, 4), "baseline_cost_usd": round(self.baseline_cost_usd, 6),
                "candidate_cost_usd": round(self.candidate_cost_usd, 6), "cost_delta": round(self.cost_delta, 4),
                "regressed": self.regressed, "findings": [f.to_dict() for f in self.findings]}
