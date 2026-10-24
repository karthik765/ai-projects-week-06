import json
import tempfile
import unittest
from pathlib import Path

from batch_planner.loader import load_jobs
from batch_planner.models import Job
from batch_planner.planner import plan_jobs


class PlannerTests(unittest.TestCase):
    def test_priority_and_limits_create_waves(self):
        jobs = [Job("low", "swift", 500, 100), Job("high", "swift", 600, 100, priority=2)]
        plan = plan_jobs(jobs, rpm=1, tpm=800)
        self.assertEqual([["high"], ["low"]], [[j.id for j in w.jobs] for w in plan.waves])
        self.assertEqual(2, len(plan.waves))

    def test_oversized_and_budgeted_jobs_are_rejected(self):
        jobs = [Job("large", "swift", 900, 200), Job("expensive", "reasoning", 100, 100, max_cost_usd=0.0001)]
        plan = plan_jobs(jobs, rpm=5, tpm=1000)
        self.assertEqual({"large", "expensive"}, {item["id"] for item in plan.rejected})

    def test_deadline_warning_is_explainable(self):
        jobs = [Job(str(i), "swift", 100, 100, deadline_minutes=0) for i in range(6)]
        plan = plan_jobs(jobs, rpm=2, tpm=500)
        self.assertTrue(any("after its deadline" in warning for warning in plan.warnings))

    def test_loader_preserves_line_errors(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "jobs.jsonl"
            path.write_text('{"id":"ok","model":"swift","input_tokens":1,"output_tokens":2}\n{"id":"bad"}\n', encoding="utf-8")
            jobs, errors = load_jobs(path)
        self.assertEqual(["ok"], [job.id for job in jobs])
        self.assertEqual(2, errors[0]["line"])

    def test_json_summary_is_serializable(self):
        summary = plan_jobs([Job("a", "swift", 10, 5)], 2, 100).as_dict()
        self.assertEqual("a", summary["waves"][0]["jobs"][0])
        json.dumps(summary)


if __name__ == "__main__":
    unittest.main()
