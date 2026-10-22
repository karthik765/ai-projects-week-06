import unittest

from dataset_splitter.checks import duplicate_groups, normalize_text
from dataset_splitter.models import SplitRatios
from dataset_splitter.splitter import split_records


class SplitterTests(unittest.TestCase):
    def setUp(self):
        self.records = [
            {"text": f"example {index}", "label": "a" if index % 2 else "b"}
            for index in range(12)
        ]

    def test_seed_is_deterministic(self):
        first, first_report = split_records(self.records, seed=7)
        second, second_report = split_records(self.records, seed=7)
        self.assertEqual(first, second)
        self.assertEqual(first_report.to_dict(), second_report.to_dict())

    def test_different_seed_changes_assignment(self):
        first, _ = split_records(self.records, seed=1)
        second, _ = split_records(self.records, seed=2)
        self.assertNotEqual(first, second)

    def test_custom_ratios_and_counts(self):
        splits, report = split_records(self.records, SplitRatios(0.5, 0.25, 0.25))
        self.assertEqual(sum(len(value) for value in splits.values()), 12)
        self.assertEqual(report.split_counts, {"train": 6, "validation": 3, "test": 3})

    def test_duplicate_detection_normalizes_case_and_space(self):
        records = [{"text": "Hello   WORLD", "label": "a"}, {"text": "hello world", "label": "a"}]
        self.assertEqual(duplicate_groups(records), [])
        self.assertEqual(duplicate_groups(records, normalized=True), [[0, 1]])
        self.assertEqual(normalize_text(" Hello\nWORLD "), "hello world")

    def test_invalid_record_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "non-empty"):
            split_records([{"text": "", "label": "a"}])


if __name__ == "__main__":
    unittest.main()
