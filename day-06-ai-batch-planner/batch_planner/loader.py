import json
from pathlib import Path

from .models import Job


def load_jobs(path: str | Path) -> tuple[list[Job], list[dict]]:
    jobs, errors = [], []
    for line_number, raw in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            item = json.loads(raw)
            required = {"id", "model", "input_tokens", "output_tokens"}
            missing = sorted(required - item.keys())
            if missing:
                raise ValueError("missing " + ", ".join(missing))
            job = Job(id=str(item["id"]), model=str(item["model"]),
                      input_tokens=int(item["input_tokens"]), output_tokens=int(item["output_tokens"]),
                      priority=int(item.get("priority", 0)),
                      max_cost_usd=item.get("max_cost_usd"),
                      deadline_minutes=item.get("deadline_minutes"))
            if not job.id or not job.model or job.input_tokens < 0 or job.output_tokens < 0:
                raise ValueError("id/model must be non-empty and token counts non-negative")
            jobs.append(job)
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            errors.append({"line": line_number, "error": str(exc)})
    return jobs, errors

