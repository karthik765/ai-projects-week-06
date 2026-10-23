import unittest

from drift_detector.detector import detect_drift
from drift_detector.loader import load_records
from drift_detector.models import Thresholds


class DetectorTests(unittest.TestCase):
    def setUp(self):
        self.baseline = [
            {"id": "a", "passed": True, "latency_ms": 100, "cost_usd": 1},
            {"id": "b", "passed": True, "latency_ms": 100, "cost_usd": 1},
            {"id": "c", "passed": False, "latency_ms": 100, "cost_usd": 1},
        ]

    def test_detects_case_and_aggregate_regressions(self):
        report = detect_drift(self.baseline, [
            {"id": "a", "passed": False, "latency_ms": 150, "cost_usd": 2},
            {"id": "b", "passed": True, "latency_ms": 150, "cost_usd": 2},
            {"id": "c", "passed": False, "latency_ms": 150, "cost_usd": 2},
        ])
        kinds = {finding.kind for finding in report.findings}
        self.assertTrue(report.regressed)
        self.assertIn("new_failure", kinds)
        self.assertIn("latency_regression", kinds)
        self.assertIn("cost_regression", kinds)

    def test_reports_missing_and_recovered_cases(self):
        report = detect_drift(self.baseline, [{"id": "c", "passed": True}])
        kinds = {finding.kind for finding in report.findings}
        self.assertIn("missing_candidate", kinds)
        self.assertIn("recovery", kinds)

    def test_threshold_can_suppress_small_change(self):
        candidate = [{**item, "latency_ms": 110, "cost_usd": 1.05} for item in self.baseline]
        report = detect_drift(self.baseline, candidate, Thresholds(min_pass_rate_delta=-0.5, latency_relative=0.2, cost_relative=0.2))
        self.assertFalse(report.regressed)

    def test_loader_rejects_duplicate_ids(self):
        with self.assertRaises(ValueError):
            load_records("tests/fixtures/duplicates.jsonl")


if __name__ == "__main__":
    unittest.main()
