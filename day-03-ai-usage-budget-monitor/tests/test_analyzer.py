import io
import json
import unittest

from usage_monitor.analyzer import analyze_records, parse_records
from usage_monitor.models import ModelRate


class UsageMonitorTests(unittest.TestCase):
    def test_parse_skips_blank_lines_and_validates_records(self):
        records = parse_records(io.StringIO('\n{"timestamp":"2026-10-21T10:00:00Z","model":"atlas-small","input_tokens":2,"output_tokens":3}\n'))
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].output_tokens, 3)

    def test_invalid_line_reports_line_number(self):
        valid = '{"timestamp":"2026-10-21T10:00:00Z","model":"atlas-small","input_tokens":1,"output_tokens":1}'
        with self.assertRaisesRegex(ValueError, r"line 2: invalid JSON"):
            parse_records(io.StringIO(valid + '\nnot-json\n'))

    def test_aggregates_cost_by_model_and_day(self):
        records = parse_records(io.StringIO('\n'.join([
            '{"timestamp":"2026-10-21T10:00:00Z","model":"demo","input_tokens":1000,"output_tokens":500}',
            '{"timestamp":"2026-10-21T11:00:00Z","model":"demo","input_tokens":1000,"output_tokens":500}',
        ])))
        report = analyze_records(records, rates={"demo": ModelRate(2.0, 4.0)})
        self.assertEqual(report.event_count, 2)
        self.assertEqual(report.total_cost_usd, 0.008)
        self.assertEqual(report.by_day, {"2026-10-21": 0.008})

    def test_budget_alerts_are_explainable(self):
        records = parse_records(io.StringIO('{"timestamp":"2026-10-21T10:00:00Z","model":"demo","input_tokens":10000,"output_tokens":0}\n'))
        report = analyze_records(records, rates={"demo": ModelRate(10.0, 0.0)}, total_budget_usd=0.05, daily_budget_usd=0.05)
        self.assertEqual(len(report.alerts), 2)
        self.assertIn("total budget exceeded", report.alerts[0])

    def test_json_report_is_serializable(self):
        records = parse_records(io.StringIO('{"timestamp":"2026-10-21T10:00:00Z","model":"atlas-small","input_tokens":1,"output_tokens":1}\n'))
        report = analyze_records(records)
        encoded = json.dumps(report.to_dict())
        self.assertIn('"event_count": 1', encoded)


if __name__ == "__main__":
    unittest.main()
