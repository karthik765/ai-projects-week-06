import argparse
import json
from pathlib import Path

from .analyzer import compare


def _read(value: str) -> str:
    path = Path(value)
    return path.read_text(encoding="utf-8") if path.exists() else value


def _human(report) -> str:
    lines = [f"Review score: {report.score}/100", report.summary]
    if report.signals:
        lines.append("\nSignals:")
        lines.extend(f"- [{signal.severity}] {signal.category}: {signal.detail}" for signal in report.signals)
    if report.sentence_changes:
        lines.append("\nSentence changes:")
        for change in report.sentence_changes:
            lines.append(f"- {change.kind}: {change.baseline or '<none>'} -> {change.candidate or '<none>'}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Review changes between two AI responses.")
    parser.add_argument("--baseline", required=True, help="text or path to the baseline response")
    parser.add_argument("--candidate", required=True, help="text or path to the candidate response")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()
    report = compare(_read(args.baseline), _read(args.candidate))
    print(json.dumps(report.to_dict(), indent=2) if args.json else _human(report))


if __name__ == "__main__":
    main()
