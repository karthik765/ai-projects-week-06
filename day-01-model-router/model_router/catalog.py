"""Model metadata used by the offline router."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Model:
    name: str
    quality: float
    latency_ms: int
    cost_per_million_tokens: float
    context_tokens: int
    capabilities: frozenset[str]


def default_catalog() -> tuple[Model, ...]:
    """Return illustrative model metadata; no provider calls are made."""
    return (
        Model("swift-small", 0.70, 180, 0.20, 8_192, frozenset({"text", "json"})),
        Model("balanced-medium", 0.84, 420, 1.10, 32_768, frozenset({"text", "json", "tools"})),
        Model("reasoning-large", 0.95, 1_050, 4.50, 128_000, frozenset({"text", "json", "tools", "vision"})),
    )
