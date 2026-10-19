import unittest

from model_router.catalog import Model, default_catalog
from model_router.policy import RouteRequest, RoutingError, route


class RoutingTests(unittest.TestCase):
    def test_prefers_balanced_model_when_large_is_too_slow(self):
        request = RouteRequest.from_dict({"task": "summarize", "min_quality": 0.8, "max_latency_ms": 900})
        result = route(request, default_catalog())
        self.assertEqual(result["selected_model"], "balanced-medium")
        self.assertIn("reason", result)

    def test_hard_capabilities_and_context_are_respected(self):
        request = RouteRequest.from_dict({"task": "inspect images", "context_tokens": 50_000, "required_capabilities": ["vision"]})
        result = route(request, default_catalog())
        self.assertEqual(result["selected_model"], "reasoning-large")
        reasons = result["rejected_models"]["balanced-medium"]
        self.assertTrue(any("vision" in reason for reason in reasons))

    def test_rejection_explains_no_match(self):
        request = RouteRequest.from_dict({"task": "cheap", "max_cost_per_million_tokens": 0.01})
        with self.assertRaisesRegex(RoutingError, "no eligible model"):
            route(request, default_catalog())

    def test_request_validation_rejects_invalid_quality(self):
        with self.assertRaisesRegex(RoutingError, "between 0 and 1"):
            RouteRequest.from_dict({"task": "x", "min_quality": 1.1})

    def test_ties_are_deterministic_by_name(self):
        catalog = (
            Model("b", 0.8, 100, 1, 1000, frozenset()),
            Model("a", 0.8, 100, 1, 1000, frozenset()),
        )
        result = route(RouteRequest.from_dict({"task": "x"}), catalog)
        self.assertEqual(result["selected_model"], "a")


if __name__ == "__main__":
    unittest.main()
