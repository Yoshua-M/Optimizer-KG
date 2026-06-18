"""
Tests for ui2-04-facade: run_scenario_view unified orchestration.

Run from project root:
    python3 -m unittest tests.application.test_run_scenario_view -v
"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from pyvis.network import Network

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MINIMAL_FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "demo" / "minimal"


class TestRunScenarioView(unittest.TestCase):
    """ui2-04-facade: run_scenario_view → ScenarioViewModel."""

    @classmethod
    def setUpClass(cls):
        from optimizer.application.run_scenario_view import run_scenario_view
        from optimizer.application.scenario_models import GraphFilter, ScenarioViewModel
        from optimizer.infrastructure.demo_loader import graph_json_to_graph_documents

        cls.run_scenario_view = staticmethod(run_scenario_view)
        cls.ScenarioViewModel = ScenarioViewModel
        cls.GraphFilter = GraphFilter
        cls.graph_json_to_graph_documents = staticmethod(graph_json_to_graph_documents)

        from tests.fixtures.scenario.value_scenario_factory import minimal_value_scenario

        graph = json.loads((MINIMAL_FIXTURE / "graph.json").read_text(encoding="utf-8"))
        cls.graph_documents = cls.graph_json_to_graph_documents(graph)
        cls.value_input = minimal_value_scenario()

    def test_returns_scenario_view_model_with_plot_series(self):
        vm = self.run_scenario_view(
            graph_documents=self.graph_documents,
            value_input=self.value_input,
        )
        self.assertIsInstance(vm, self.ScenarioViewModel)
        self.assertIsInstance(vm.graph_network, Network)
        self.assertTrue(hasattr(vm.plot_series, "relevance_scatter"))
        self.assertTrue(hasattr(vm.plot_series, "top_v_relevance"))

    def test_metric_label_lookup_uses_human_readable_names(self):
        vm = self.run_scenario_view(
            graph_documents=self.graph_documents,
            value_input=self.value_input,
        )
        label = vm.metric_label_by_id["M-01"]
        self.assertIn("On-Time Delivery", label)

    def test_exposes_available_graph_types_for_ui_checkboxes(self):
        vm = self.run_scenario_view(
            graph_documents=self.graph_documents,
            value_input=self.value_input,
        )
        self.assertIn("Activity", vm.available_node_types)
        self.assertIn("Metric", vm.available_node_types)
        self.assertIn("AFFECTS", vm.available_relationship_types)

    def test_graph_filter_reduces_visible_nodes(self):
        graph_filter = self.GraphFilter(
            node_types=frozenset({"Activity"}),
            relationship_types=None,
            isolation_seed_id=None,
            relevance_pull_enabled=False,
        )
        vm = self.run_scenario_view(
            graph_documents=self.graph_documents,
            value_input=self.value_input,
            graph_filter=graph_filter,
        )
        node_ids = {node["id"] for node in vm.graph_network.nodes}
        self.assertIn("A-01", node_ids)
        self.assertNotIn("M-01", node_ids)

    def test_relevance_pull_flag_passed_to_pyvis(self):
        """When enabled, activity→metric edge should carry styling (width or length)."""
        vm_off = self.run_scenario_view(
            graph_documents=self.graph_documents,
            value_input=self.value_input,
            graph_filter=self.GraphFilter(
                node_types=None,
                relationship_types=None,
                isolation_seed_id=None,
                relevance_pull_enabled=False,
            ),
        )
        vm_on = self.run_scenario_view(
            graph_documents=self.graph_documents,
            value_input=self.value_input,
            graph_filter=self.GraphFilter(
                node_types=None,
                relationship_types=None,
                isolation_seed_id=None,
                relevance_pull_enabled=True,
            ),
        )
        _assert_edge_styling_differs(vm_off.graph_network, vm_on.graph_network)


def _assert_edge_styling_differs(net_off: Network, net_on: Network) -> None:
    def edge_key(edge):
        return (edge["from"], edge["to"])

    off_edges = {edge_key(e): e for e in net_off.edges}
    on_edges = {edge_key(e): e for e in net_on.edges}
    common = set(off_edges) & set(on_edges)
    assert common, "Expected overlapping edges between on/off graphs"
    changed = False
    for key in common:
        off_edge = off_edges[key]
        on_edge = on_edges[key]
        for attr in ("width", "length", "value"):
            if off_edge.get(attr) != on_edge.get(attr):
                changed = True
                break
    assert changed, "Relevance pull should change edge width, length, or value"


class TestRunScenarioViewExplainMode(unittest.TestCase):
    """ui2-07: explain mode keeps full graph + grey-out via PyVis (AC-EXPLAIN-1, AC-EXPLAIN-2)."""

    @classmethod
    def setUpClass(cls):
        from optimizer.application.run_scenario_view import run_scenario_view
        from optimizer.application.scenario_models import GraphFilter

        cls.run_scenario_view = staticmethod(run_scenario_view)
        cls.GraphFilter = GraphFilter

        from tests.fixtures.scenario.relevance_explain_factory import (
            a26_relevance_explain_graph_documents,
            a26_value_scenario,
            expected_a26_highlight_node_ids,
        )

        cls.graph_documents = a26_relevance_explain_graph_documents()
        cls.value_input = a26_value_scenario()
        cls.expected_highlight = expected_a26_highlight_node_ids()

    def _all_node_ids(self, vm) -> set[str]:
        return {node["id"] for node in vm.graph_network.nodes}

    def test_explain_keeps_full_graph_not_pruned(self):
        vm = self.run_scenario_view(
            graph_documents=self.graph_documents,
            value_input=self.value_input,
            graph_filter=self.GraphFilter(
                node_types=None,
                relationship_types=None,
                isolation_seed_id=None,
                relevance_pull_enabled=False,
                explain_activity_id="A-26",
            ),
        )
        node_ids = self._all_node_ids(vm)
        self.assertIn("A-26", node_ids)
        self.assertIn("A-27", node_ids)
        self.assertIn("M-03", node_ids)
        self.assertGreaterEqual(len(node_ids), len(self.expected_highlight))

    def test_explain_dims_non_highlighted_nodes(self):
        vm = self.run_scenario_view(
            graph_documents=self.graph_documents,
            value_input=self.value_input,
            graph_filter=self.GraphFilter(
                node_types=None,
                relationship_types=None,
                isolation_seed_id=None,
                relevance_pull_enabled=False,
                explain_activity_id="A-26",
            ),
        )
        nodes = {node["id"]: node for node in vm.graph_network.nodes}
        highlighted = nodes["A-26"]
        dimmed = nodes["A-27"]
        self.assertNotEqual(highlighted.get("color"), dimmed.get("color"))

    def test_explain_exclusive_with_isolation_seed(self):
        """When explain_activity_id is set, isolation must not prune the graph (D22)."""
        vm = self.run_scenario_view(
            graph_documents=self.graph_documents,
            value_input=self.value_input,
            graph_filter=self.GraphFilter(
                node_types=None,
                relationship_types=None,
                isolation_seed_id="A-26",
                relevance_pull_enabled=False,
                explain_activity_id="A-26",
            ),
        )
        node_ids = self._all_node_ids(vm)
        self.assertIn("A-27", node_ids)
        self.assertIn("M-03", node_ids)


class TestRunDemoScenarioDelegatesToScenarioView(unittest.TestCase):
    """run_demo_scenario remains thin adapter over run_scenario_view."""

    @classmethod
    def setUpClass(cls):
        from optimizer.application.run_demo_scenario import run_demo_scenario
        from optimizer.application.scenario_models import ScenarioViewModel

        cls.run_demo_scenario = staticmethod(run_demo_scenario)
        cls.ScenarioViewModel = ScenarioViewModel

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.repo_root = Path(self._tmpdir.name)
        self._write_minimal_repo(self.repo_root)

    @staticmethod
    def _write_minimal_repo(root: Path) -> None:
        scenario_dir = root / "data" / "processed" / "demo" / "minimal_demo"
        scenario_dir.mkdir(parents=True)
        for name in ("graph.json", "metrics.json", "relevance.json"):
            shutil.copy(MINIMAL_FIXTURE / name, scenario_dir / name)
        manifest = {
            "scenarios": [
                {
                    "id": "minimal_demo",
                    "title": "Minimal Demo",
                    "description": "Facade delegation test",
                    "paths": {
                        "graph": "data/processed/demo/minimal_demo/graph.json",
                        "metrics": "data/processed/demo/minimal_demo/metrics.json",
                        "relevance": "data/processed/demo/minimal_demo/relevance.json",
                    },
                }
            ]
        }
        configs_dir = root / "configs"
        configs_dir.mkdir()
        (configs_dir / "demo_scenarios.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )

    def test_demo_adapter_returns_scenario_view_model(self):
        vm = self.run_demo_scenario("minimal_demo", repo_root=self.repo_root)
        self.assertIsInstance(vm, self.ScenarioViewModel)
        self.assertTrue(hasattr(vm, "plot_series"))

    def test_existing_matrix_fields_preserved_for_expander(self):
        vm = self.run_demo_scenario("minimal_demo", repo_root=self.repo_root)
        self.assertGreaterEqual(len(vm.metrics), 1)
        cells = [(r.activity_id, r.metric_id) for r in vm.matrix_rows]
        self.assertIn(("A-01", "M-01"), cells)


class TestRunScenarioViewAnalyticsIntegration(unittest.TestCase):
    """ga-11: orchestration exposes VS discovery + catalog findings on ScenarioViewModel."""

    @classmethod
    def setUpClass(cls):
        from optimizer.application.run_scenario_view import run_scenario_view
        from optimizer.application.scenario_models import GraphFilter
        from optimizer.graph_analytics.models import ActivityCategory
        from optimizer.infrastructure.demo_loader import (
            bundle_to_value_input,
            load_demo_bundle,
            resolve_repo_root,
        )

        cls.run_scenario_view = staticmethod(run_scenario_view)
        cls.GraphFilter = GraphFilter
        cls.ActivityCategory = ActivityCategory

        repo_root = resolve_repo_root()
        bundle = load_demo_bundle("energoil_mexico", repo_root=repo_root)
        cls.graph_documents = bundle.graph_documents
        cls.value_input = bundle_to_value_input(bundle)

    def test_view_model_includes_value_stream_discovery(self):
        vm = self.run_scenario_view(
            graph_documents=self.graph_documents,
            value_input=self.value_input,
        )
        self.assertIsNotNone(vm.value_stream_discovery)
        self.assertTrue(hasattr(vm.value_stream_discovery, "vs_union"))

    def test_view_model_includes_catalog_findings_for_all_analytics(self):
        vm = self.run_scenario_view(
            graph_documents=self.graph_documents,
            value_input=self.value_input,
        )
        self.assertEqual(len(vm.catalog_findings), 36)

    def test_value_stream_focus_dims_non_path_activities(self):
        from optimizer.infrastructure.visualization.pyvis_graph import (
            DIM_COLOR,
            VS_BOUNDARY_EVENT_COLOR,
            VS_FLOW_EDGE_COLOR,
            VS_METRIC_EDGE_COLOR,
            VS_METRIC_NODE_COLOR,
            VS_SUPPORT_EDGE_COLOR,
        )

        from tests.fixtures.graph_analytics.vs_graph_factory import (
            value_stream_graph_documents,
            value_stream_value_input,
        )

        graph_documents = value_stream_graph_documents()
        value_input = value_stream_value_input()
        vm = self.run_scenario_view(
            graph_documents=graph_documents,
            value_input=value_input,
            graph_filter=self.GraphFilter(
                node_types=None,
                relationship_types=None,
                isolation_seed_id=None,
                relevance_pull_enabled=False,
                value_stream_focus_delivery_id="EV-V1",
            ),
        )
        nodes = {node["id"]: node for node in vm.graph_network.nodes}
        edges = {(edge["from"], edge["to"]): edge for edge in vm.graph_network.edges}
        self.assertNotEqual(nodes["A-01"].get("color"), DIM_COLOR)
        self.assertEqual(nodes["A-04"].get("color"), DIM_COLOR)
        self.assertEqual(nodes["EV-D1"].get("color"), VS_BOUNDARY_EVENT_COLOR)
        self.assertEqual(nodes["M-01"].get("color"), VS_METRIC_NODE_COLOR)
        self.assertEqual(edges[("EV-D1", "A-01")].get("color"), VS_FLOW_EDGE_COLOR)
        self.assertEqual(edges[("A-01", "M-01")].get("color"), VS_METRIC_EDGE_COLOR)
        self.assertEqual(edges[("A-03", "A-01")].get("color"), DIM_COLOR)

    def test_value_stream_focus_support_precedes_are_blue(self):
        from optimizer.infrastructure.visualization.pyvis_graph import VS_SUPPORT_EDGE_COLOR

        from tests.fixtures.graph_analytics.vs_graph_factory import (
            value_stream_graph_documents,
            value_stream_value_input,
        )

        vm = self.run_scenario_view(
            graph_documents=value_stream_graph_documents(),
            value_input=value_stream_value_input(),
            graph_filter=self.GraphFilter(
                node_types=None,
                relationship_types=None,
                isolation_seed_id=None,
                relevance_pull_enabled=False,
                value_stream_focus_delivery_id="EV-V1",
                value_stream_include_support=True,
            ),
        )
        edges = {(edge["from"], edge["to"]): edge for edge in vm.graph_network.edges}
        self.assertEqual(edges[("A-03", "A-01")].get("color"), VS_SUPPORT_EDGE_COLOR)

    def test_value_stream_overlay_applies_classification_colors(self):
        graph_filter = self.GraphFilter(
            node_types=None,
            relationship_types=None,
            isolation_seed_id=None,
            relevance_pull_enabled=False,
            value_stream_overlay=True,
        )
        vm = self.run_scenario_view(
            graph_documents=self.graph_documents,
            value_input=self.value_input,
            graph_filter=graph_filter,
        )
        self.assertIsNotNone(vm.vs_color_overrides)
        self.assertTrue(len(vm.vs_color_overrides) >= 1)

    def test_analytic_highlight_id_produces_highlight_payload(self):
        graph_filter = self.GraphFilter(
            node_types=None,
            relationship_types=None,
            isolation_seed_id=None,
            relevance_pull_enabled=False,
            analytic_highlight_id="G-01",
        )
        vm = self.run_scenario_view(
            graph_documents=self.graph_documents,
            value_input=self.value_input,
            graph_filter=graph_filter,
        )
        self.assertIsNotNone(vm.active_analytic_highlight)


if __name__ == "__main__":
    unittest.main()
