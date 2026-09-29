"""
Tests for ga-05-value-streams: Steiner tree discovery + four-way classification.

Run: python3 -m unittest tests.graph_analytics.test_value_streams -v
"""

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


class TestValueStreamDiscovery(unittest.TestCase):
    """ga-05: VS Steiner discovery per docs/VS_Selection_Protocol.md."""

    @classmethod
    def setUpClass(cls):
        from optimizer.graph_analytics.graph_bridge import build_graph_context
        from optimizer.graph_analytics.models import ActivityCategory
        from optimizer.graph_analytics.value_streams import discover_value_streams

        cls.build_graph_context = staticmethod(build_graph_context)
        cls.discover_value_streams = staticmethod(discover_value_streams)
        cls.ActivityCategory = ActivityCategory
        cls.ctx = cls.build_graph_context(
            value_stream_graph_documents(),
            value_stream_value_input(),
        )

    def test_discovers_tree_for_delivery_event(self):
        result = self.discover_value_streams(self.ctx)
        trees_by_delivery = {t.delivery_event_id: t for t in result.trees}
        self.assertIn("EV-V1", trees_by_delivery)
        tree = trees_by_delivery["EV-V1"]
        self.assertIn("A-01", tree.activity_ids)
        self.assertIn("A-02", tree.activity_ids)
        self.assertIn("EV-D1", tree.anchor_event_ids)

    def test_vs_union_contains_tree_activities(self):
        result = self.discover_value_streams(self.ctx)
        self.assertTrue(result.vs_union >= {"A-01", "A-02"})

    def test_classifies_structural_support_semantic_support_and_waste(self):
        result = self.discover_value_streams(self.ctx)
        classifications = result.classifications
        self.assertEqual(
            classifications.get("A-01"),
            self.ActivityCategory.VALUE_STREAM,
        )
        self.assertEqual(
            classifications.get("A-03"),
            self.ActivityCategory.STRUCTURAL_SUPPORT,
        )
        self.assertEqual(
            classifications.get("A-04"),
            self.ActivityCategory.WASTE,
        )

    def test_node_scores_use_cumulative_normalized_relevance(self):
        result = self.discover_value_streams(self.ctx)
        tree = next(t for t in result.trees if t.delivery_event_id == "EV-V1")
        self.assertAlmostEqual(tree.node_scores["A-01"], 1.0)
        self.assertAlmostEqual(tree.node_scores["A-02"], 0.5)

    def test_group_count_and_avg_group_size(self):
        result = self.discover_value_streams(self.ctx)
        self.assertEqual(result.group_count, 1)
        self.assertAlmostEqual(result.avg_group_size, 2.0)


class TestConvergentValueStream(unittest.TestCase):
    """Tree connects multiple demand anchors to one delivery."""

    @classmethod
    def setUpClass(cls):
        from optimizer.graph_analytics.graph_bridge import build_graph_context
        from optimizer.graph_analytics.value_streams import discover_value_streams

        cls.discover_value_streams = staticmethod(discover_value_streams)
        cls.ctx = build_graph_context(
            convergent_value_stream_graph_documents(),
            convergent_value_stream_value_input(),
        )

    def test_both_demand_anchors_in_same_tree(self):
        result = self.discover_value_streams(self.ctx)
        self.assertEqual(len(result.trees), 1)
        tree = result.trees[0]
        self.assertEqual(tree.delivery_event_id, "EV-V1")
        self.assertEqual(tree.anchor_event_ids, frozenset({"EV-D1", "EV-D2"}))
        self.assertIn("A-MID", tree.activity_ids)


class TestSharedBackbone(unittest.TestCase):
    """Shared activity appears in backbone with overlap >= 2."""

    @classmethod
    def setUpClass(cls):
        from optimizer.graph_analytics.graph_bridge import build_graph_context
        from optimizer.graph_analytics.value_streams import discover_value_streams

        cls.discover_value_streams = staticmethod(discover_value_streams)
        cls.ctx = build_graph_context(
            shared_backbone_graph_documents(),
            shared_backbone_value_input(),
        )

    def test_shared_activity_in_backbone(self):
        result = self.discover_value_streams(self.ctx)
        self.assertIn("A-SHARED", result.backbone)
        self.assertGreaterEqual(result.node_overlap.get("A-SHARED", 0), 2)


class TestValueStreamFocus(unittest.TestCase):
    """vsf-01: per-group focus payload with progressive layers."""

    @classmethod
    def setUpClass(cls):
        from optimizer.graph_analytics.models import ActivityCategory
        from optimizer.graph_analytics.value_streams import (
            build_value_stream_focus,
            discover_value_streams,
        )

        from optimizer.graph_analytics.graph_bridge import build_graph_context

        cls.ActivityCategory = ActivityCategory
        cls.build_value_stream_focus = staticmethod(build_value_stream_focus)
        cls.ctx = build_graph_context(
            value_stream_graph_documents(),
            value_stream_value_input(),
        )
        cls.discovery = discover_value_streams(cls.ctx)

    def test_vs_only_includes_tree_activities_and_metrics(self):
        focus = self.build_value_stream_focus(self.ctx, self.discovery, "EV-V1")
        self.assertIsNotNone(focus)
        self.assertEqual(focus.visible_activity_ids, frozenset({"A-01", "A-02"}))
        self.assertIn("M-01", focus.highlight_node_ids)
        self.assertIn("M-01", focus.metric_ids)
        self.assertNotIn("A-03", focus.highlight_node_ids)
        self.assertNotIn("A-04", focus.highlight_node_ids)

    def test_includes_boundary_events_and_flow_precedes_edges(self):
        focus = self.build_value_stream_focus(self.ctx, self.discovery, "EV-V1")
        self.assertIsNotNone(focus)
        self.assertEqual(focus.boundary_event_ids, frozenset({"EV-D1", "EV-V1"}))
        self.assertIn(("EV-D1", "A-01", "PRECEDES"), focus.highlight_edge_keys)
        self.assertIn(("A-01", "A-02", "PRECEDES"), focus.highlight_edge_keys)
        self.assertIn(("A-02", "EV-V1", "PRECEDES"), focus.highlight_edge_keys)

    def test_includes_metric_affect_edges_only_for_visible_activities(self):
        focus = self.build_value_stream_focus(self.ctx, self.discovery, "EV-V1")
        self.assertIsNotNone(focus)
        self.assertIn(("A-01", "M-01", "AFFECTS"), focus.highlight_edge_keys)
        self.assertIn(("A-02", "M-01", "AFFECTS"), focus.highlight_edge_keys)
        self.assertNotIn(("A-04", "M-01", "AFFECTS"), focus.highlight_edge_keys)

    def test_include_support_adds_structural_and_semantic(self):
        focus = self.build_value_stream_focus(
            self.ctx,
            self.discovery,
            "EV-V1",
            include_support=True,
        )
        self.assertIn("A-03", focus.visible_activity_ids)
        self.assertEqual(
            focus.activity_classifications["A-03"],
            self.ActivityCategory.STRUCTURAL_SUPPORT,
        )
        self.assertIn(("A-03", "A-01", "PRECEDES"), focus.highlight_edge_keys)

    def test_include_waste_adds_waste_activities(self):
        focus = self.build_value_stream_focus(
            self.ctx,
            self.discovery,
            "EV-V1",
            include_waste=True,
        )
        self.assertIn("A-04", focus.visible_activity_ids)
        self.assertEqual(
            focus.activity_classifications["A-04"],
            self.ActivityCategory.WASTE,
        )

    def test_unknown_delivery_returns_none(self):
        focus = self.build_value_stream_focus(self.ctx, self.discovery, "EV-V99")
        self.assertIsNone(focus)

    def test_includes_metrics_reached_only_through_drivers(self):
        from langchain_community.graphs.graph_document import (
            GraphDocument,
            Node,
            Relationship,
        )
        from langchain_core.documents import Document

        from optimizer.application.scenario_models import (
            ActivityRow,
            ActivityScoreRow,
            MetricRow,
            ValueScenarioInput,
        )
        from optimizer.graph_analytics.graph_bridge import build_graph_context
        from optimizer.graph_analytics.value_streams import discover_value_streams

        ev_d1 = Node(id="EV-D1", type="Event", properties={"event_type": "demand"})
        ev_v1 = Node(
            id="EV-V1", type="Event", properties={"event_type": "value_realization"}
        )
        a1 = Node(id="A-01", type="Activity", properties={"label": "Confirmar pedido"})
        a3 = Node(id="A-03", type="Activity", properties={"label": "Timbrar CFDI"})
        m1 = Node(id="M-01", type="Metric", properties={"label": "CFDI correcto y a tiempo"})
        md1 = Node(id="MD-01", type="MetricDriver", properties={"label": "Puntualidad factura"})
        docs = [
            GraphDocument(
                nodes=[ev_d1, ev_v1, a1, a3, m1, md1],
                relationships=[
                    Relationship(source=ev_d1, target=a1, type="PRECEDES"),
                    Relationship(source=a1, target=ev_v1, type="PRECEDES"),
                    Relationship(source=a3, target=a1, type="PRECEDES"),
                    Relationship(source=a3, target=md1, type="AFFECTS"),
                    Relationship(source=md1, target=m1, type="DRIVES"),
                ],
                source=Document(page_content="driver-mediated metric"),
            )
        ]
        value_input = ValueScenarioInput(
            metrics=(MetricRow(id="M-01", name="CFDI correcto y a tiempo", definition="", client_need=""),),
            activities=(
                ActivityRow(
                    activity_id="A-01",
                    activity_name="Confirmar pedido",
                    process_id="P-01",
                    p=0.5,
                    c=0.5,
                    f=0.5,
                    r=0.5,
                    v=0.6,
                    scores=(
                        ActivityScoreRow(
                            metric_id="M-01",
                            g=0.0,
                            j=0.0,
                            dv=0.0,
                            b=0.1,
                            relevance=0.2,
                            pct_contribution=0.2,
                        ),
                    ),
                ),
                ActivityRow(
                    activity_id="A-03",
                    activity_name="Timbrar CFDI",
                    process_id="P-01",
                    p=0.5,
                    c=0.5,
                    f=0.5,
                    r=0.5,
                    v=0.5,
                    scores=(
                        ActivityScoreRow(
                            metric_id="M-01",
                            g=0.0,
                            j=0.0,
                            dv=0.0,
                            b=0.3,
                            relevance=0.8,
                            pct_contribution=0.8,
                        ),
                    ),
                ),
            ),
            process_rollups=(),
            strategic_b_zero=(),
        )
        ctx = build_graph_context(docs, value_input)
        discovery = discover_value_streams(ctx)
        focus = self.build_value_stream_focus(ctx, discovery, "EV-V1")
        self.assertIsNotNone(focus)
        self.assertIn("M-01", focus.metric_ids)
        self.assertIn("MD-01", focus.metric_driver_ids)
        self.assertIn("A-03", focus.highlight_node_ids)
        self.assertIn(("A-03", "MD-01", "AFFECTS"), focus.highlight_edge_keys)
        self.assertIn(("MD-01", "M-01", "DRIVES"), focus.highlight_edge_keys)


class TestValueStreamEdgeCases(unittest.TestCase):
    """ga-05 edge: disconnected demand/value returns empty trees."""

    @classmethod
    def setUpClass(cls):
        from langchain_community.graphs.graph_document import GraphDocument, Node
        from langchain_core.documents import Document

        from optimizer.application.scenario_models import ValueScenarioInput
        from optimizer.graph_analytics.graph_bridge import build_graph_context
        from optimizer.graph_analytics.value_streams import discover_value_streams

        cls.build_graph_context = staticmethod(build_graph_context)
        cls.discover_value_streams = staticmethod(discover_value_streams)

        ev_d = Node(
            id="EV-D1",
            type="Event",
            properties={"event_type": "demand"},
        )
        ev_v = Node(
            id="EV-V2",
            type="Event",
            properties={"event_type": "value_realization"},
        )
        cls.ctx = cls.build_graph_context(
            [
                GraphDocument(
                    nodes=[ev_d, ev_v],
                    relationships=[],
                    source=Document(page_content="disconnected"),
                )
            ],
            ValueScenarioInput(
                metrics=(),
                activities=(),
                process_rollups=(),
                strategic_b_zero=(),
            ),
        )

    def test_no_path_yields_empty_trees_without_crash(self):
        result = self.discover_value_streams(self.ctx)
        self.assertEqual(result.trees, ())
        self.assertEqual(result.vs_union, frozenset())


if __name__ == "__main__":
    unittest.main()
