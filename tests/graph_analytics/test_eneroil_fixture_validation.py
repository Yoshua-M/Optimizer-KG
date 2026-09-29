"""
Tests for the eneroil_real_v1 structural fixture (real interview data, no metrics).

Run: python3 -m unittest tests.graph_analytics.test_eneroil_fixture_validation -v
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_ID = "eneroil_real_v1"


class TestEneroilRealFixtureValidation(unittest.TestCase):
    """Structural scenario: no Metric nodes, empty relevance, VS still discoverable."""

    @classmethod
    def setUpClass(cls):
        from optimizer.graph_analytics.graph_bridge import build_graph_context
        from optimizer.graph_analytics.validation import preflight_graph
        from optimizer.infrastructure.demo_loader import (
            bundle_to_value_input,
            load_demo_bundle,
            load_manifest,
            resolve_repo_root,
        )

        cls.preflight_graph = staticmethod(preflight_graph)

        repo_root = resolve_repo_root()
        cls.scenario = next(
            item for item in load_manifest(repo_root) if item.id == SCENARIO_ID
        )
        cls.bundle = load_demo_bundle(SCENARIO_ID, repo_root=repo_root)
        cls.ctx = build_graph_context(
            cls.bundle.graph_documents,
            bundle_to_value_input(cls.bundle),
        )

        graph_path = repo_root / cls.bundle.scenario.paths["graph"]
        graph = json.loads(graph_path.read_text(encoding="utf-8"))
        cls.nodes = graph["nodes"]
        cls.event_nodes = [n for n in cls.nodes if n.get("type") == "Event"]

    def test_scenario_kind_is_structural(self):
        self.assertEqual(self.scenario.kind, "structural")

    def test_no_metric_nodes(self):
        metric_nodes = [n for n in self.nodes if n.get("type") == "Metric"]
        self.assertEqual(metric_nodes, [])
        self.assertEqual(self.bundle.metrics.get("metrics"), [])
        self.assertEqual(self.bundle.relevance.get("activities"), [])

    def test_node_counts_match_inventory(self):
        counts: dict[str, int] = {}
        for node in self.nodes:
            counts[node["type"]] = counts.get(node["type"], 0) + 1
        self.assertEqual(
            counts,
            {
                "Activity": 23,
                "Process": 9,
                "Team": 8,
                "Capability": 8,
                "System": 5,
                "Event": 8,
                "CustomerJourneyStep": 8,
                "MetricDriver": 6,
            },
        )

    def test_events_have_event_type_property(self):
        self.assertEqual(len(self.event_nodes), 8)
        missing = [
            node["id"]
            for node in self.event_nodes
            if "event_type" not in (node.get("properties") or {})
        ]
        self.assertEqual(missing, [], f"Events missing event_type: {missing}")

    def test_demand_and_value_realization_events_present(self):
        types = {
            (node.get("properties") or {}).get("event_type")
            for node in self.event_nodes
        }
        self.assertIn("demand", types)
        self.assertIn("value_realization", types)

    def test_preflight_passes_on_bundle(self):
        result = self.preflight_graph(self.ctx)
        self.assertTrue(result.ok, msg="; ".join(result.warnings))

    def test_scenario_view_loads_and_discovers_value_stream(self):
        from optimizer.application.run_demo_scenario import run_demo_scenario
        from optimizer.infrastructure.demo_loader import resolve_repo_root

        view_model = run_demo_scenario(SCENARIO_ID, repo_root=resolve_repo_root())
        self.assertEqual(view_model.metrics, ())
        self.assertEqual(view_model.activities, ())
        discovery = view_model.value_stream_discovery
        self.assertIsNotNone(discovery)
        self.assertGreaterEqual(len(discovery.trees), 1)
        delivery_ids = {tree.delivery_event_id for tree in discovery.trees}
        self.assertIn("EVT-07", delivery_ids)


if __name__ == "__main__":
    unittest.main()
