"""Tests for Valor-tab value stream flow payload builder."""

from __future__ import annotations

import unittest

from tests.fixtures.graph_analytics.vs_graph_factory import (
    convergent_value_stream_graph_documents,
    convergent_value_stream_value_input,
    shared_backbone_graph_documents,
    shared_backbone_value_input,
    value_stream_graph_documents,
    value_stream_value_input,
)


class TestValueStreamFlowGraph(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from optimizer.graph_analytics.graph_bridge import build_graph_context
        from optimizer.graph_analytics.value_stream_flow import build_value_stream_flow_graph
        from optimizer.graph_analytics.value_streams import discover_value_streams

        cls.build_graph_context = staticmethod(build_graph_context)
        cls.build_value_stream_flow_graph = staticmethod(build_value_stream_flow_graph)
        cls.discover_value_streams = staticmethod(discover_value_streams)

    def _flow(self, docs, value_input, delivery_ids, **labels):
        ctx = self.build_graph_context(docs, value_input)
        discovery = self.discover_value_streams(ctx)
        return self.build_value_stream_flow_graph(
            ctx,
            discovery,
            frozenset(delivery_ids),
            event_label_by_id=labels.get("events", {}),
            activity_label_by_id=labels.get("activities", {}),
            metric_label_by_id=labels.get("metrics", {"M-01": "M-01 — Entrega a tiempo"}),
        )

    def test_single_tree_includes_demand_delivery_and_activities(self):
        flow = self._flow(
            value_stream_graph_documents(),
            value_stream_value_input(),
            {"EV-V1"},
            events={"EV-D1": "Orden", "EV-V1": "Entrega"},
            activities={"A-01": "A-01 — Actividad VS 1", "A-02": "A-02 — Actividad VS 2"},
        )
        self.assertIsNotNone(flow)
        assert flow is not None
        kinds = {node.id: node.kind for node in flow.nodes}
        self.assertEqual(kinds["EV-D1"], "demand_event")
        self.assertEqual(kinds["EV-V1"], "delivery_event")
        self.assertEqual(kinds["A-01"], "activity")
        self.assertFalse(flow.overlay_mode)

    def test_edges_follow_precedes_tree(self):
        flow = self._flow(
            value_stream_graph_documents(),
            value_stream_value_input(),
            {"EV-V1"},
        )
        assert flow is not None
        edge_pairs = {(edge.source, edge.target) for edge in flow.edges}
        self.assertIn(("EV-D1", "A-01"), edge_pairs)
        self.assertIn(("A-01", "A-02"), edge_pairs)
        self.assertIn(("A-02", "EV-V1"), edge_pairs)

    def test_activity_metrics_only_when_relevance_positive(self):
        flow = self._flow(
            value_stream_graph_documents(),
            value_stream_value_input(),
            {"EV-V1"},
        )
        assert flow is not None
        by_id = {node.id: node for node in flow.nodes}
        self.assertEqual(len(by_id["A-01"].metrics), 1)
        self.assertAlmostEqual(by_id["A-01"].metrics[0].relevance, 0.8)
        self.assertEqual(len(by_id["A-02"].metrics), 1)

    def test_activity_nodes_include_evaluation_factors(self):
        flow = self._flow(
            value_stream_graph_documents(),
            value_stream_value_input(),
            {"EV-V1"},
        )
        assert flow is not None
        activity = next(node for node in flow.nodes if node.id == "A-01")
        self.assertEqual(activity.p, 0.5)
        self.assertEqual(activity.c, 0.5)
        self.assertEqual(activity.f, 0.5)
        self.assertEqual(activity.r, 0.5)
        self.assertEqual(activity.v, 0.6)
        payload = next(item for item in flow.to_dict()["nodes"] if item["id"] == "A-01")
        self.assertEqual(payload["p"], 0.5)
        self.assertEqual(payload["v"], 0.6)

    def test_join_node_flagged_on_convergent_tree(self):
        flow = self._flow(
            convergent_value_stream_graph_documents(),
            convergent_value_stream_value_input(),
            {"EV-V1"},
        )
        assert flow is not None
        amid = next(node for node in flow.nodes if node.id == "A-MID")
        self.assertTrue(amid.is_join)
        self.assertGreaterEqual(amid.in_degree, 2)

    def test_overlay_mode_counts_shared_activity(self):
        ctx = self.build_graph_context(
            shared_backbone_graph_documents(),
            shared_backbone_value_input(),
        )
        discovery = self.discover_value_streams(ctx)
        flow = self.build_value_stream_flow_graph(
            ctx,
            discovery,
            frozenset({"EV-V1", "EV-V2"}),
            event_label_by_id={},
            activity_label_by_id={"A-SHARED": "Shared activity"},
            metric_label_by_id={"M-01": "M1"},
        )
        assert flow is not None
        self.assertTrue(flow.overlay_mode)
        shared = next(node for node in flow.nodes if node.id == "A-SHARED")
        self.assertEqual(shared.overlap_count, 2)
        self.assertTrue(shared.is_backbone)

    def test_returns_none_for_unknown_delivery(self):
        flow = self._flow(
            value_stream_graph_documents(),
            value_stream_value_input(),
            {"EV-MISSING"},
        )
        self.assertIsNone(flow)

    def test_to_dict_serializes_payload(self):
        flow = self._flow(
            value_stream_graph_documents(),
            value_stream_value_input(),
            {"EV-V1"},
        )
        assert flow is not None
        payload = flow.to_dict()
        self.assertIn("nodes", payload)
        self.assertIn("edges", payload)
        self.assertEqual(payload["selected_delivery_ids"], ["EV-V1"])


if __name__ == "__main__":
    unittest.main()
