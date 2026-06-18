"""
Tests for ga-15-fixture-enrichment: energoil demo ontology preflight.

Run: python3 -m unittest tests.graph_analytics.test_fixture_validation -v
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class _EnergoilFixtureValidationMixin:
    scenario_id: str
    expected_event_count: int | None = None

    @classmethod
    def setUpClass(cls):
        from optimizer.graph_analytics.graph_bridge import build_graph_context
        from optimizer.graph_analytics.validation import preflight_graph
        from optimizer.infrastructure.demo_loader import (
            bundle_to_value_input,
            load_demo_bundle,
            resolve_repo_root,
        )

        cls.preflight_graph = staticmethod(preflight_graph)
        cls.build_graph_context = staticmethod(build_graph_context)

        repo_root = resolve_repo_root()
        cls.bundle = load_demo_bundle(cls.scenario_id, repo_root=repo_root)
        cls.ctx = cls.build_graph_context(
            cls.bundle.graph_documents,
            bundle_to_value_input(cls.bundle),
        )

        graph_path = repo_root / cls.bundle.scenario.paths["graph"]
        graph = json.loads(graph_path.read_text(encoding="utf-8"))
        cls.event_nodes = [n for n in graph["nodes"] if n.get("type") == "Event"]
        cls.activity_nodes = [n for n in graph["nodes"] if n.get("type") == "Activity"]

    def test_events_have_event_type_property(self):
        self.assertTrue(self.event_nodes, f"{self.scenario_id} graph must include Event nodes")
        if self.expected_event_count is not None:
            self.assertEqual(len(self.event_nodes), self.expected_event_count)
        missing = [
            node["id"]
            for node in self.event_nodes
            if "event_type" not in (node.get("properties") or {})
        ]
        self.assertEqual(
            missing,
            [],
            f"Events missing event_type: {missing}",
        )

    def test_preflight_passes_on_bundle(self):
        result = self.preflight_graph(self.ctx)
        self.assertTrue(result.ok, msg="; ".join(result.warnings))


class TestEnergoilV1FixtureValidation(_EnergoilFixtureValidationMixin, unittest.TestCase):
    """ga-15: energoil v1 fixture has event_type; preflight passes."""

    scenario_id = "energoil_mexico"
    expected_event_count = 8


class TestEnergoilV2FixtureValidation(_EnergoilFixtureValidationMixin, unittest.TestCase):
    """ga-15: energoil v2 fixture has Porter areas and 14 classified events."""

    scenario_id = "energoil_mexico_v2"
    expected_event_count = 14

    def test_multi_porter_area_activities_tagged(self):
        multi_area = [
            node
            for node in self.activity_nodes
            if len((node.get("properties") or {}).get("porter_areas") or []) > 1
        ]
        self.assertTrue(multi_area, "v2 must include multi-area Porter activities")
        sample = multi_area[0]["properties"]
        self.assertIn("area", sample)
        self.assertIn("gobernanza", sample["area"].lower())

    def test_demand_and_value_realization_events_present(self):
        types = {
            (node.get("properties") or {}).get("event_type")
            for node in self.event_nodes
        }
        self.assertIn("demand", types)
        self.assertIn("value_realization", types)


if __name__ == "__main__":
    unittest.main()
