from typing import Any

from .metrics import average, pass_rate, relative_delta
from .models import DriftReport, Finding, Thresholds


def detect_drift(baseline: list[dict[str, Any]], candidate: list[dict[str, Any]], thresholds: Thresholds | None = None) -> DriftReport:
    thresholds = thresholds or Thresholds()
    base_by_id = {item["id"]: item for item in baseline}
    cand_by_id = {item["id"]: item for item in candidate}
    matched = [cand_by_id[key] for key in base_by_id.keys() & cand_by_id.keys()]
    base_rate, cand_rate = pass_rate(baseline), pass_rate(candidate)
    base_latency, cand_latency = average(baseline, "latency_ms"), average(candidate, "latency_ms")
    base_cost, cand_cost = average(baseline, "cost_usd"), average(candidate, "cost_usd")
    findings: list[Finding] = []
    if len(matched) < thresholds.min_cases:
        findings.append(Finding("small_sample", None, f"Only {len(matched)} matched cases; review manually.", "warning"))
    if cand_rate - base_rate <= thresholds.min_pass_rate_delta and len(matched) >= thresholds.min_cases:
        findings.append(Finding("pass_rate_regression", None, f"Pass rate fell from {base_rate:.1%} to {cand_rate:.1%}.", "error"))
    if relative_delta(base_latency, cand_latency) >= thresholds.latency_relative:
        findings.append(Finding("latency_regression", None, f"Average latency increased by {relative_delta(base_latency, cand_latency):.1%}.", "error"))
    if relative_delta(base_cost, cand_cost) >= thresholds.cost_relative:
        findings.append(Finding("cost_regression", None, f"Average cost increased by {relative_delta(base_cost, cand_cost):.1%}.", "error"))
    for case_id in sorted(base_by_id.keys() - cand_by_id.keys()):
        findings.append(Finding("missing_candidate", case_id, "Case exists in baseline but not candidate.", "warning"))
    for case_id in sorted(cand_by_id.keys() - base_by_id.keys()):
        findings.append(Finding("new_candidate", case_id, "Case exists in candidate but not baseline.", "info"))
    for case_id in sorted(base_by_id.keys() & cand_by_id.keys()):
        before, after = base_by_id[case_id], cand_by_id[case_id]
        if before["passed"] and not after["passed"]:
            findings.append(Finding("new_failure", case_id, "Previously passing case now fails.", "error"))
        elif not before["passed"] and after["passed"]:
            findings.append(Finding("recovery", case_id, "Previously failing case now passes.", "info"))
    return DriftReport(len(baseline), len(candidate), len(matched), base_rate, cand_rate, cand_rate - base_rate,
                       base_latency, cand_latency, relative_delta(base_latency, cand_latency), base_cost, cand_cost,
                       relative_delta(base_cost, cand_cost), findings)
