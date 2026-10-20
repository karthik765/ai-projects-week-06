from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class SentenceChange:
    kind: str
    baseline: str = ""
    candidate: str = ""


@dataclass(frozen=True)
class Signal:
    category: str
    detail: str
    severity: str


@dataclass(frozen=True)
class DiffReport:
    score: int
    summary: str
    sentence_changes: list[SentenceChange]
    signals: list[Signal]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
