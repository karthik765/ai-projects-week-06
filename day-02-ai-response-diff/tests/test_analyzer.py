import unittest

from response_diff import compare


class CompareTests(unittest.TestCase):
    def test_identical_text_has_no_changes(self):
        report = compare("A short answer.", "A short answer.")
        self.assertEqual(report.score, 0)
        self.assertFalse(report.sentence_changes)
        self.assertFalse(report.signals)

    def test_number_change_is_high_signal(self):
        report = compare("Wait 5 days.", "Wait 2 days.")
        self.assertTrue(any(signal.category == "numeric" for signal in report.signals))
        self.assertGreaterEqual(report.score, 15)

    def test_introduced_risk_term_is_detected(self):
        report = compare("Use the account.", "Always use the account.")
        self.assertTrue(any("always" in signal.detail for signal in report.signals))

    def test_added_sentence_is_structured(self):
        report = compare("Hello.", "Hello. Contact support.")
        self.assertEqual(report.sentence_changes[0].kind, "added")
        self.assertEqual(report.sentence_changes[0].candidate, "Contact support.")

    def test_empty_input_is_rejected(self):
        with self.assertRaises(ValueError):
            compare("", "Candidate.")


if __name__ == "__main__":
    unittest.main()
