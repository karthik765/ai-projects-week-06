import re
from difflib import SequenceMatcher

from .models import DiffReport, SentenceChange, Signal

_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+|\n+")
_TOKEN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_./:-]*")
_NUMBER_RE = re.compile(r"(?<![A-Za-z])(?:\$?\d[\d,]*(?:\.\d+)?%?|\d+(?:\.\d+)?[xX])")
_URL_RE = re.compile(r"https?://[^\s)]+")
_RISK_TERMS = {
    "must", "never", "always", "guarantee", "guaranteed", "delete", "admin",
    "password", "secret", "unsafe", "urgent", "legal", "medical", "financial",
    "permission", "authorized", "authorize",
}


def _sentences(text: str) -> list[str]:
    return [part.strip() for part in _SENTENCE_RE.split(text.strip()) if part.strip()]


def _tokens(text: str) -> set[str]:
    return {token.lower() for token in _TOKEN_RE.findall(text)}


def _changes(baseline: list[str], candidate: list[str]) -> list[SentenceChange]:
    matcher = SequenceMatcher(a=baseline, b=candidate, autojunk=False)
    result: list[SentenceChange] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        if tag == "replace":
            pairs = max(i2 - i1, j2 - j1)
            for offset in range(pairs):
                result.append(SentenceChange(
                    kind="changed",
                    baseline=baseline[i1 + offset] if i1 + offset < i2 else "",
                    candidate=candidate[j1 + offset] if j1 + offset < j2 else "",
                ))
        else:
            for sentence in baseline[i1:i2]:
                result.append(SentenceChange(kind="removed", baseline=sentence))
            for sentence in candidate[j1:j2]:
                result.append(SentenceChange(kind="added", candidate=sentence))
    return result


def compare(baseline: str, candidate: str) -> DiffReport:
    """Compare two responses and return explainable review signals."""
    if not baseline.strip() or not candidate.strip():
        raise ValueError("baseline and candidate must both contain text")

    old_sentences, new_sentences = _sentences(baseline), _sentences(candidate)
    changes = _changes(old_sentences, new_sentences)
    signals: list[Signal] = []
    old_numbers, new_numbers = _NUMBER_RE.findall(baseline), _NUMBER_RE.findall(candidate)
    if old_numbers != new_numbers:
        signals.append(Signal("numeric", f"numbers changed: {old_numbers or ['none']} -> {new_numbers or ['none']}", "high"))
    old_urls, new_urls = _URL_RE.findall(baseline), _URL_RE.findall(candidate)
    if old_urls != new_urls:
        signals.append(Signal("link", f"URLs changed: {old_urls or ['none']} -> {new_urls or ['none']}", "medium"))

    old_risk, new_risk = _tokens(baseline) & _RISK_TERMS, _tokens(candidate) & _RISK_TERMS
    introduced = sorted(new_risk - old_risk)
    removed = sorted(old_risk - new_risk)
    if introduced:
        signals.append(Signal("risk", f"risk terms introduced: {', '.join(introduced)}", "high"))
    if removed:
        signals.append(Signal("risk", f"risk terms removed: {', '.join(removed)}", "medium"))

    old_words, new_words = _tokens(baseline), _tokens(candidate)
    overlap = len(old_words & new_words) / max(len(old_words | new_words), 1)
    score = min(100, len(changes) * 12 + len(signals) * 15 + (20 if overlap < 0.45 else 0))
    if not changes and not signals:
        summary = "No material lexical changes detected."
    else:
        summary = f"{len(changes)} sentence change(s) and {len(signals)} targeted signal(s) require review."
    return DiffReport(score=score, summary=summary, sentence_changes=changes, signals=signals)
