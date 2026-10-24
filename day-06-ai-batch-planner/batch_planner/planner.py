import math

from .models import Job, Plan, Wave

DEFAULT_PRICES = {"swift": (0.20, 0.80), "reasoning": (2.00, 8.00)}


def _cost(job: Job, prices: dict[str, tuple[float, float]]) -> float:
    input_price, output_price = prices.get(job.model, (0.0, 0.0))
    return job.input_tokens * input_price / 1_000_000 + job.output_tokens * output_price / 1_000_000


def plan_jobs(jobs: list[Job], rpm: int, tpm: int, prices=None, validation_errors=None) -> Plan:
    if rpm <= 0 or tpm <= 0:
        raise ValueError("rpm and tpm must be positive")
    prices = prices or DEFAULT_PRICES
    warnings = []
    rejected = list(validation_errors or [])
    waves: list[Wave] = []
    ordered = sorted(enumerate(jobs), key=lambda pair: (-pair[1].priority,
                                                         pair[1].deadline_minutes is None,
                                                         pair[1].deadline_minutes or math.inf,
                                                         pair[0]))
    for _, job in ordered:
        cost = _cost(job, prices)
        if job.tokens > tpm:
            rejected.append({"id": job.id, "error": f"{job.tokens} tokens exceed tpm limit {tpm}"})
            continue
        if job.max_cost_usd is not None and cost > float(job.max_cost_usd):
            rejected.append({"id": job.id, "error": f"estimated cost ${cost:.6f} exceeds max ${float(job.max_cost_usd):.6f}"})
            continue
        wave = waves[-1] if waves else None
        if wave is None or len(wave.jobs) >= rpm or wave.tokens + job.tokens > tpm:
            wave = Wave(number=len(waves) + 1, start_minute=(len(waves) * 60 / rpm))
            waves.append(wave)
        wave.jobs.append(job)
        wave.tokens += job.tokens
        wave.cost_usd += cost
        if job.deadline_minutes is not None and wave.start_minute > float(job.deadline_minutes):
            warnings.append(f"{job.id} starts at minute {wave.start_minute:.1f}, after its deadline")
    if rejected:
        warnings.append(f"{len(rejected)} job(s) rejected and need review")
    return Plan(waves, rejected, warnings, sum(w.cost_usd for w in waves), sum(w.tokens for w in waves))

