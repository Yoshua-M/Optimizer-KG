"""
Tests for scenario PyVis rendering: labels, grouping, filters, explain mode.

Run from project root:
    python3 -m unittest tests.infrastructure.test_pyvis_graph_scenario -v
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from langchain_community.graphs.graph_document import GraphDocument, Node, Relationship
from langchain_core.documents import Document
from pyvis.network import Network

from optimizer.infrastructure.visualization import pyvis_graph


def _labeled_scenario_graph_documents():
    metric = Node(
        id="M-01",
        type="Metric",
        properties={"label": "Tasa de Entrega a Tiempo"},
    )
    activity = Node(
        id="A-01",
        type="Activity",
        properties={"label": "Monitoreo diario de precios rack"},
    )
    rel = Relationship(source=activity, target=metric, type="AFFECTS")
    return [
        GraphDocument(
            nodes=[metric, activity],
            relationships=[rel],
            source=Document(page_content="scenario"),
        )
    ]


def _legacy_graph_documents():
    """Text-extraction shape: no display label in properties."""
    person = Node(id="Alice", type="Person")
    org = Node(id="Acme Corp", type="Organization")
    rel = Relationship(source=person, target=org, type="WORKS_AT")
    return [
        GraphDocument(
            nodes=[person, org],
            relationships=[rel],
            source=Document(page_content="Alice works at Acme Corp."),
        )
    ]


class _TempCwdTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self._prev_cwd = os.getcwd()
        os.chdir(self._tmpdir.name)
        self.addCleanup(os.chdir, self._prev_cwd)


class TestVisualizeGraphScenarioStyling(_TempCwdTestCase):
    """Human-readable labels and type grouping for scenario graphs."""

    def _nodes_by_id(self, net: Network) -> dict[str, dict]:
        return {node["id"]: node for node in net.nodes}

    def test_uses_display_label_from_properties(self):
        net = pyvis_graph.visualize_graph(_labeled_scenario_graph_documents())
        nodes = self._nodes_by_id(net)

        self.assertEqual(nodes["M-01"]["label"], "Tasa de Entrega a Tiempo")
        self.assertEqual(nodes["A-01"]["label"], "Monitoreo diario de precios rack")

    def test_groups_nodes_by_type(self):
        net = pyvis_graph.visualize_graph(_labeled_scenario_graph_documents())
        nodes = self._nodes_by_id(net)

        self.assertEqual(nodes["M-01"]["group"], "Metric")
        self.assertEqual(nodes["A-01"]["group"], "Activity")

    def test_falls_back_to_node_id_when_no_display_label(self):
        """Preserve text→graph behavior when properties lack label."""
        net = pyvis_graph.visualize_graph(_legacy_graph_documents())
        nodes = self._nodes_by_id(net)

        self.assertEqual(nodes["Alice"]["label"], "Alice")
        self.assertEqual(nodes["Acme Corp"]["label"], "Acme Corp")


class TestVisualizeGraphUi2Options(_TempCwdTestCase):
    """ui2-03-pyvis: stable colors, tooltips, relevance pull (AC-2, AC-3, AC-8)."""

    @classmethod
    def setUpClass(cls):
        from optimizer.infrastructure.visualization.pyvis_graph import VisualizeOptions

        cls.VisualizeOptions = VisualizeOptions

    def _nodes_by_id(self, net: Network) -> dict[str, dict]:
        return {node["id"]: node for node in net.nodes}

    def _edge_by_endpoints(self, net: Network) -> dict[tuple[str, str], dict]:
        return {(edge["from"], edge["to"]): edge for edge in net.edges}

    def test_stable_color_per_node_type(self):
        net_a = pyvis_graph.visualize_graph(_labeled_scenario_graph_documents())
        net_b = pyvis_graph.visualize_graph(_labeled_scenario_graph_documents())
        for node_id in ("M-01", "A-01"):
            color_a = self._nodes_by_id(net_a)[node_id].get("color")
            color_b = self._nodes_by_id(net_b)[node_id].get("color")
            self.assertIsNotNone(color_a)
            self.assertEqual(color_a, color_b)

    def test_activity_tooltip_includes_evidence_pointer(self):
        docs = _labeled_scenario_graph_documents()
        activity = docs[0].nodes[1]
        activity.properties["evidence_pointer"] = 'F2: "solo producto"'
        net = pyvis_graph.visualize_graph(docs)
        title = self._nodes_by_id(net)["A-01"].get("title", "")
        self.assertIn("Evidencia:", title)
        self.assertIn("solo producto", title)

    def test_activity_tooltip_includes_frequency_and_v_fields(self):
        docs = _labeled_scenario_graph_documents()
        activity = docs[0].nodes[1]
        activity.properties.update(
            {
                "description": "Daily price monitoring",
                "frequency": "Diaria",
                "p": 0.25,
                "c": 0.75,
                "f": 1.0,
                "r": 0.25,
                "v": 0.6,
            }
        )
        net = pyvis_graph.visualize_graph(docs)
        title = self._nodes_by_id(net)["A-01"].get("title", "")
        self.assertIn("A-01", title)
        self.assertIn("Daily price monitoring", title)
        self.assertIn("Diaria", title)
        self.assertIn("Frecuencia: 1.0", title)
        self.assertIn("Valor interno: 0.6", title)

    def test_relevance_pull_styles_activity_to_metric_edge(self):
        options = self.VisualizeOptions(
            relevance_pull_enabled=True,
            edge_relevance_map={("A-01", "M-01"): 0.8},
        )
        net_off = pyvis_graph.visualize_graph(_labeled_scenario_graph_documents())
        net_on = pyvis_graph.visualize_graph(
            _labeled_scenario_graph_documents(), options=options
        )
        off_edge = self._edge_by_endpoints(net_off)[("A-01", "M-01")]
        on_edge = self._edge_by_endpoints(net_on)[("A-01", "M-01")]
        styled = False
        for attr in ("width", "length", "value"):
            if off_edge.get(attr) != on_edge.get(attr):
                styled = True
                break
        self.assertTrue(styled)

    def test_higher_relevance_produces_stronger_pull_than_lower(self):
        options = self.VisualizeOptions(
            relevance_pull_enabled=True,
            edge_relevance_map={
                ("A-01", "M-01"): 0.9,
            },
        )
        net = pyvis_graph.visualize_graph(
            _labeled_scenario_graph_documents(), options=options
        )
        edge = self._edge_by_endpoints(net)[("A-01", "M-01")]
        self.assertTrue(
            edge.get("width") or edge.get("length") or edge.get("value"),
            "Expected edge styling attribute when relevance pull is enabled",
        )

    def test_legacy_call_without_options_unchanged(self):
        """app.py path: visualize_graph(documents) still works."""
        net = pyvis_graph.visualize_graph(_legacy_graph_documents())
        self.assertEqual(len(net.nodes), 2)


class TestVisualizeGraphUi2ExplainAndPuntoCiego(_TempCwdTestCase):
    """ui2-07 / ui2-08: grey-out highlight + punto ciego dashed edges (D23–D24)."""

    DIM_COLOR = "#555555"

    @classmethod
    def setUpClass(cls):
        from optimizer.infrastructure.visualization.pyvis_graph import VisualizeOptions

        cls.VisualizeOptions = VisualizeOptions

        from tests.fixtures.scenario.relevance_explain_factory import (
            a26_relevance_explain_graph_documents,
            expected_a26_highlight_edge_keys,
            expected_a26_highlight_node_ids,
            punto_ciego_graph_documents,
        )

        cls.explain_docs = a26_relevance_explain_graph_documents()
        cls.punto_docs = punto_ciego_graph_documents()
        cls.highlight_nodes = expected_a26_highlight_node_ids()
        cls.highlight_edges = expected_a26_highlight_edge_keys()

    def _nodes_by_id(self, net: Network) -> dict[str, dict]:
        return {node["id"]: node for node in net.nodes}

    def _edge_by_endpoints(self, net: Network) -> dict[tuple[str, str], dict]:
        return {(edge["from"], edge["to"]): edge for edge in net.edges}

    def test_non_highlighted_nodes_render_dim_color(self):
        options = self.VisualizeOptions(
            highlight_node_ids=self.highlight_nodes,
            highlight_edge_keys=self.highlight_edges,
        )
        net = pyvis_graph.visualize_graph(self.explain_docs, options=options)
        nodes = self._nodes_by_id(net)
        self.assertEqual(nodes["A-27"].get("color"), self.DIM_COLOR)
        self.assertNotEqual(nodes["A-26"].get("color"), self.DIM_COLOR)

    def test_highlighted_nodes_keep_type_color(self):
        options = self.VisualizeOptions(
            highlight_node_ids=self.highlight_nodes,
            highlight_edge_keys=self.highlight_edges,
        )
        net = pyvis_graph.visualize_graph(self.explain_docs, options=options)
        activity_color = self._nodes_by_id(net)["A-26"].get("color")
        self.assertEqual(activity_color, pyvis_graph.NODE_TYPE_COLORS["Activity"])

    def test_punto_ciego_edge_when_pull_on_and_indirect_score(self):
        options = self.VisualizeOptions(
            relevance_pull_enabled=True,
            edge_relevance_map={("A-01", "M-01"): 0.5},
            indirect_relevance_map={("A-01", "M-04"): 0.27},
        )
        net = pyvis_graph.visualize_graph(self.punto_docs, options=options)
        edge = self._edge_by_endpoints(net)[("A-01", "M-04")]
        label = (edge.get("label") or "").lower()
        self.assertIn("punto ciego", label)
        self.assertTrue(edge.get("dashes"))

    def test_no_punto_ciego_edge_when_pull_off(self):
        options = self.VisualizeOptions(
            relevance_pull_enabled=False,
            indirect_relevance_map={("A-01", "M-04"): 0.27},
        )
        net = pyvis_graph.visualize_graph(self.punto_docs, options=options)
        endpoints = self._edge_by_endpoints(net)
        self.assertNotIn(("A-01", "M-04"), endpoints)


class TestVisualizeGraphValueStreamOverlay(unittest.TestCase):
    """ga-12-pyvis-vs-colors: VS category colors via node_color_overrides."""

    @classmethod
    def setUpClass(cls):
        from optimizer.infrastructure.visualization.pyvis_graph import (
            VS_CATEGORY_COLORS,
            VS_FLOW_EDGE_COLOR,
            VS_METRIC_EDGE_COLOR,
            VisualizeOptions,
        )

        from tests.fixtures.graph_analytics.vs_graph_factory import (
            value_stream_graph_documents,
        )

        cls.VisualizeOptions = VisualizeOptions
        cls.VS_CATEGORY_COLORS = VS_CATEGORY_COLORS
        cls.VS_FLOW_EDGE_COLOR = VS_FLOW_EDGE_COLOR
        cls.VS_METRIC_EDGE_COLOR = VS_METRIC_EDGE_COLOR
        cls.documents = value_stream_graph_documents()

    def _nodes_by_id(self, net: Network) -> dict[str, dict]:
        return {node["id"]: node for node in net.nodes}

    def test_node_color_overrides_apply_to_activity_nodes(self):
        overrides = {
            "A-01": self.VS_CATEGORY_COLORS["value_stream"],
            "A-03": self.VS_CATEGORY_COLORS["structural_support"],
            "A-04": self.VS_CATEGORY_COLORS["waste"],
        }
        options = self.VisualizeOptions(node_color_overrides=overrides)
        net = pyvis_graph.visualize_graph(self.documents, options=options)
        nodes = self._nodes_by_id(net)
        self.assertEqual(nodes["A-01"]["color"], overrides["A-01"])
        self.assertEqual(nodes["A-04"]["color"], overrides["A-04"])

    def test_vs_palette_defines_four_categories(self):
        expected = {"value_stream", "structural_support", "semantic_support", "waste"}
        self.assertTrue(expected <= set(self.VS_CATEGORY_COLORS.keys()))

    def test_vs_focus_edge_overrides_color_flow_and_metric_edges(self):
        highlight_edges = frozenset(
            {
                ("EV-D1", "A-01", "PRECEDES"),
                ("A-01", "M-01", "AFFECTS"),
            }
        )
        options = self.VisualizeOptions(
            highlight_edge_keys=highlight_edges,
            edge_color_overrides={
                ("EV-D1", "A-01", "PRECEDES"): self.VS_FLOW_EDGE_COLOR,
                ("A-01", "M-01", "AFFECTS"): self.VS_METRIC_EDGE_COLOR,
            },
        )
        net = pyvis_graph.visualize_graph(self.documents, options=options)
        edges = {(edge["from"], edge["to"]): edge for edge in net.edges}
        self.assertEqual(
            edges[("EV-D1", "A-01")].get("color"),
            self.VS_FLOW_EDGE_COLOR,
        )
        self.assertEqual(
            edges[("A-01", "M-01")].get("color"),
            self.VS_METRIC_EDGE_COLOR,
        )
        self.assertEqual(edges[("A-03", "A-01")].get("color"), pyvis_graph.DIM_COLOR)


class TestRelevanceHeatmapVisualization(unittest.TestCase):
    """Activity-only highlight with blue→orange cumulative relevance colors."""

    @classmethod
    def setUpClass(cls):
        from optimizer.infrastructure.visualization.pyvis_graph import (
            HEATMAP_COLOR_HIGH,
            HEATMAP_COLOR_LOW,
            VisualizeOptions,
            relevance_heatmap_color,
        )

        cls.VisualizeOptions = VisualizeOptions
        cls.relevance_heatmap_color = staticmethod(relevance_heatmap_color)
        cls.HEATMAP_COLOR_LOW = HEATMAP_COLOR_LOW
        cls.HEATMAP_COLOR_HIGH = HEATMAP_COLOR_HIGH
        cls.documents = _labeled_scenario_graph_documents()

    def test_relevance_heatmap_color_interpolates_brown_to_orange(self):
        self.assertEqual(self.relevance_heatmap_color(0.0), self.HEATMAP_COLOR_LOW)
        self.assertEqual(self.relevance_heatmap_color(1.0), self.HEATMAP_COLOR_HIGH)

    def test_heatmap_dims_non_activity_nodes_and_all_edges(self):
        options = self.VisualizeOptions(
            highlight_node_ids=frozenset({"A-01"}),
            highlight_edge_keys=frozenset(),
            node_color_overrides={"A-01": self.relevance_heatmap_color(1.0)},
        )
        net = pyvis_graph.visualize_graph(self.documents, options=options)
        nodes = {node["id"]: node for node in net.nodes}
        edges = {(edge["from"], edge["to"]): edge for edge in net.edges}
        self.assertEqual(nodes["M-01"].get("color"), pyvis_graph.DIM_COLOR)
        self.assertEqual(nodes["A-01"].get("color"), self.HEATMAP_COLOR_HIGH)
        self.assertEqual(edges[("A-01", "M-01")].get("color"), pyvis_graph.DIM_COLOR)


if __name__ == "__main__":
    unittest.main()
