"""
Tests for ga-02-graph-bridge-validation: GraphDocument adapter + preflight.

Run: python3 -m unittest tests.graph_analytics.test_graph_bridge -v
"""

from __future__ import annotations

import unittest

from tests.fixtures.graph_analytics.vs_graph_factory import (
    value_stream_graph_documents,
    value_stream_value_input,
)


class TestGraphBridge(unittest.TestCase):
    """ga-02: build_graph_context normalizes LangChain graph + scores."""

    @classmethod
    def setUpClass(cls):
        from optimizer.graph_analytics.graph_bridge import build_graph_context

        cls.build_graph_context = staticmethod(build_graph_context)
        cls.documents = value_stream_graph_documents()
        cls.value_input = value_stream_value_input()

    def test_builds_context_with_flow_graph(self):
        ctx = self.build_graph_context(self.documents, self.value_input)
        self.assertTrue(hasattr(ctx, "flow_graph"))
        self.assertTrue(hasattr(ctx, "activity_ids"))

    def test_activity_ids_excludes_events_and_metrics(self):
        ctx = self.build_graph_context(self.documents, self.value_input)
        self.assertEqual(ctx.activity_ids, {"A-01", "A-02", "A-03", "A-04"})

    def test_event_type_partitions_demand_and_value_realization(self):
        ctx = self.build_graph_context(self.documents, self.value_input)
        self.assertIn("EV-D1", ctx.demand_event_ids)
        self.assertIn("EV-V1", ctx.value_realization_event_ids)

    def test_relevance_lookup_from_value_input(self):
        ctx = self.build_graph_context(self.documents, self.value_input)
        self.assertAlmostEqual(ctx.relevance("A-01", "M-01"), 0.8)
        self.assertAlmostEqual(ctx.v_score("A-03"), 0.9)

    def test_prec_path_exists_between_demand_and_value_events(self):
        import networkx as nx

        ctx = self.build_graph_context(self.documents, self.value_input)
        self.assertTrue(
            nx.has_path(ctx.flow_graph, "EV-D1", "EV-V1"),
            "Fixture must connect demand to value realization",
        )


class TestGraphValidation(unittest.TestCase):
    """ga-02: preflight warnings for missing ontology labels."""

    @classmethod
    def setUpClass(cls):
        from langchain_community.graphs.graph_document import GraphDocument, Node
        from langchain_core.documents import Document

        from optimizer.application.scenario_models import ValueScenarioInput
        from optimizer.graph_analytics.graph_bridge import build_graph_context
        from optimizer.graph_analytics.validation import preflight_graph

        cls.build_graph_context = staticmethod(build_graph_context)
        cls.preflight_graph = staticmethod(preflight_graph)
        cls.ValueScenarioInput = ValueScenarioInput
        cls.GraphDocument = GraphDocument
        cls.Node = Node
        cls.Document = Document

    def test_preflight_warns_when_event_missing_event_type(self):
        ev = self.Node(id="EV-X", type="Event", properties={})
        doc = self.GraphDocument(
            nodes=[ev],
            relationships=[],
            source=self.Document(page_content="bad event"),
        )
        empty = self.ValueScenarioInput(
            metrics=(),
            activities=(),
            process_rollups=(),
            strategic_b_zero=(),
        )
        ctx = self.build_graph_context([doc], empty)
        result = self.preflight_graph(ctx)
        self.assertTrue(result.warnings)
        combined = " ".join(result.warnings).lower()
        self.assertIn("event_type", combined)

    def test_preflight_ok_on_valid_vs_fixture(self):
        ctx = self.build_graph_context(
            value_stream_graph_documents(),
            value_stream_value_input(),
        )
        result = self.preflight_graph(ctx)
        self.assertTrue(result.ok)
        self.assertEqual(result.warnings, ())


if __name__ == "__main__":
    unittest.main()
