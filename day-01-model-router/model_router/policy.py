"""Validation and explainable model ranking."""

from dataclasses import dataclass, field
from typing import Iterable

from .catalog import Model


class RoutingError(ValueError):
    """Raised when no model satisfies the hard constraints."""


@dataclass(frozen=True)
class RouteRequest:
    task: str
    min_quality: float = 0.0
    max_latency_ms: int | None = None
    max_cost_per_million_tokens: float | None = None
    context_tokens: int = 0
    required_capabilities: frozenset[str] = field(default_factory=frozenset)

    @classmethod
    def from_dict(cls, data: dict) -> "RouteRequest":
        task = str(data.get("task", "")).strip()
        if not task:
            raise RoutingError("task must be a non-empty string")
        quality = float(data.get("min_quality", 0.0))
        latency = data.get("max_latency_ms")
        cost = data.get("max_cost_per_million_tokens")
        context = int(data.get("context_tokens", 0))
        if not 0 <= quality <= 1:
            raise RoutingError("min_quality must be between 0 and 1")
        if latency is not None and int(latency) <= 0:
            raise RoutingError("max_latency_ms must be positive")
        if cost is not None and float(cost) < 0:
            raise RoutingError("max_cost_per_million_tokens cannot be negative")
        if context < 0:
            raise RoutingError("context_tokens cannot be negative")
        capabilities = frozenset(str(item) for item in data.get("required_capabilities", []))
        return cls(task, quality, None if latency is None else int(latency), None if cost is None else float(cost), context, capabilities)


def _rejection_reasons(model: Model, request: RouteRequest) -> list[str]:
    reasons: list[str] = []
    if model.quality < request.min_quality:
        reasons.append(f"quality {model.quality:.2f} < {request.min_quality:.2f}")
    if request.max_latency_ms is not None and model.latency_ms > request.max_latency_ms:
        reasons.append(f"latency {model.latency_ms}ms > {request.max_latency_ms}ms")
    if request.max_cost_per_million_tokens is not None and model.cost_per_million_tokens > request.max_cost_per_million_tokens:
        reasons.append(f"cost ${model.cost_per_million_tokens:.2f} > ${request.max_cost_per_million_tokens:.2f}")
    if model.context_tokens < request.context_tokens:
        reasons.append(f"context {model.context_tokens} < {request.context_tokens}")
    missing = request.required_capabilities - model.capabilities
    if missing:
        reasons.append("missing capabilities: " + ", ".join(sorted(missing)))
    return reasons


def _score(model: Model, request: RouteRequest) -> float:
    quality = model.quality
    latency = 1 - min(model.latency_ms / 2_000, 1)
    cost = 1 - min(model.cost_per_million_tokens / 5, 1)
    return round(quality * 0.60 + latency * 0.20 + cost * 0.20, 4)


def route(request: RouteRequest, catalog: Iterable[Model]) -> dict:
    """Return the best eligible model and an audit-friendly decision record."""
    models = tuple(catalog)
    rejected = {model.name: _rejection_reasons(model, request) for model in models}
    eligible = [model for model in models if not rejected[model.name]]
    if not eligible:
        details = "; ".join(f"{name}: {', '.join(reasons)}" for name, reasons in rejected.items())
        raise RoutingError("no eligible model; " + details)
    ranked = sorted(eligible, key=lambda model: (-_score(model, request), model.name))
    selected = ranked[0]
    return {
        "task": request.task,
        "selected_model": selected.name,
        "score": _score(selected, request),
        "estimated_cost_per_million_tokens": selected.cost_per_million_tokens,
        "eligible_models": [model.name for model in ranked],
        "rejected_models": rejected,
        "reason": "highest weighted quality/latency/cost score among eligible models",
    }
