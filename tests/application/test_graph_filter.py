"""
Tests for ui2-02-graph-filter: shared GraphDocument filtering and isolation.

Run from project root:
    python3 -m unittest tests.application.test_graph_filter -v
"""

from __future__ import annotations

import unittest

from tests.fixtures.scenario.graph_documents_factory import (
    process_isolation_graph_documents,
)


class TestGraphFilter(unittest.TestCase):
    """ui2-02-graph-filter: type filters and subgraph isolation (AC-1, AC-7, FR-1–FR-3)."""

    @classmethod
    def setUpClass(cls):
        from optimizer.application.graph_filter import (
            filter_graph_document,
            isolate_subgraph,
            list_node_types,
            list_relationship_types,
        )
        from optimizer.application.scenario_models import GraphFilter

        cls.GraphFilter = GraphFilter
        cls.filter_graph_document = staticmethod(filter_graph_document)
        cls.isolate_subgraph = staticmethod(isolate_subgraph)
        cls.list_node_types = staticmethod(list_node_types)
        cls.list_relationship_types = staticmethod(list_relationship_types)
        cls.documents = process_isolation_graph_documents()

    def _node_ids(self, documents):
        doc = documents[0]
        return {node.id for node in doc.nodes}

    def _relationship_types(self, documents):
        doc = documents[0]
        return {rel.type for rel in doc.relationships}

    def test_lists_available_types_from_graph(self):
        node_types = self.list_node_types(self.documents)
        rel_types = self.list_relationship_types(self.documents)
        self.assertIn("Activity", node_types)
        self.assertIn("Process", node_types)
        self.assertIn("Metric", node_types)
        self.assertIn("AFFECTS", rel_types)
        self.assertIn("PART_OF", rel_types)

    def test_node_type_filter_keeps_only_selected_types(self):
        graph_filter = self.GraphFilter(
            node_types=frozenset({"Activity", "Process"}),
            relationship_types=None,
            isolation_seed_id=None,
            relevance_pull_enabled=False,
        )
        filtered = self.filter_graph_document(self.documents, graph_filter)
        ids = self._node_ids(filtered)
        self.assertEqual(ids, {"P-01", "P-02", "A-01", "A-02"})
        self.assertNotIn("M-01", ids)

    def test_relationship_type_filter_keeps_only_selected_edges(self):
        graph_filter = self.GraphFilter(
            node_types=None,
            relationship_types=frozenset({"AFFECTS"}),
            isolation_seed_id=None,
            relevance_pull_enabled=False,
        )
        filtered = self.filter_graph_document(self.documents, graph_filter)
        self.assertEqual(self._relationship_types(filtered), {"AFFECTS"})

    def test_empty_node_type_selection_yields_no_nodes(self):
        graph_filter = self.GraphFilter(
            node_types=frozenset(),
            relationship_types=None,
            isolation_seed_id=None,
            relevance_pull_enabled=False,
        )
        filtered = self.filter_graph_document(self.documents, graph_filter)
        self.assertEqual(len(filtered[0].nodes), 0)

    def test_isolate_process_includes_activities_and_value_neighbors(self):
        isolated = self.isolate_subgraph(self.documents, "P-01")
        ids = self._node_ids(isolated)
        self.assertIn("P-01", ids)
        self.assertIn("A-01", ids)
        self.assertIn("M-01", ids)
        self.assertNotIn("P-02", ids)
        self.assertNotIn("A-02", ids)
        self.assertNotIn("M-02", ids)

    def test_isolate_activity_includes_process_and_metric(self):
        isolated = self.isolate_subgraph(self.documents, "A-01")
        ids = self._node_ids(isolated)
        self.assertIn("A-01", ids)
        self.assertIn("P-01", ids)
        self.assertIn("M-01", ids)
        self.assertNotIn("A-02", ids)

    def test_isolate_activity_keeps_failure_scope_only(self):
        from langchain_community.graphs.graph_document import GraphDocument, Node, Relationship
        from langchain_core.documents import Document

        from optimizer.application.scenario_models import (
            ActivityRow,
            ActivityScoreRow,
            MetricRow,
            ValueScenarioInput,
        )
        from optimizer.graph_analytics.models import ValueStreamTree

        p1 = Node(id="P-01", type="Process")
        a1 = Node(id="A-01", type="Activity", properties={"process_id": "P-01"})
        sibling = Node(id="A-sib", type="Activity", properties={"process_id": "P-01"})
        flow = Node(id="A-flow", type="Activity", properties={"process_id": "P-02"})
        other = Node(id="A-other", type="Activity", properties={"process_id": "P-02"})
        p2 = Node(id="P-02", type="Process")
        m1 = Node(id="M-01", type="Metric")
        noise = Node(id="M-noise", type="Metric")
        demand = Node(id="E-dem", type="Event", properties={"event_type": "demand"})
        delivery = Node(id="E-del", type="Event", properties={"event_type": "value_realization"})
        documents = [
            GraphDocument(
                nodes=[p1, p2, a1, sibling, flow, other, m1, noise, demand, delivery],
                relationships=[
                    Relationship(source=a1, target=p1, type="PART_OF"),
                    Relationship(source=sibling, target=p1, type="PART_OF"),
                    Relationship(source=other, target=p2, type="PART_OF"),
                    Relationship(source=a1, target=m1, type="AFFECTS"),
                    Relationship(source=a1, target=noise, type="AFFECTS"),
                    Relationship(source=sibling, target=m1, type="AFFECTS"),
                    Relationship(source=demand, target=a1, type="PRECEDES"),
                    Relationship(source=a1, target=flow, type="PRECEDES"),
                    Relationship(source=flow, target=delivery, type="PRECEDES"),
                ],
                source=Document(page_content="failure scope"),
            )
        ]
        value_input = ValueScenarioInput(
            metrics=(MetricRow(id="M-01", name="M-01", definition="", client_need=""),),
            activities=(
                ActivityRow(
                    activity_id="A-01",
                    activity_name="A-01",
                    process_id="P-01",
                    p=1.0,
                    c=1.0,
                    f=1.0,
                    r=1.0,
                    v=1.0,
                    scores=(
                        ActivityScoreRow(
                            metric_id="M-01",
                            g=1.0,
                            j=0.0,
                            dv=0.0,
                            b=1.0,
                            relevance=1.0,
                            pct_contribution=1.0,
                        ),
                    ),
                ),
            ),
            process_rollups=(),
            strategic_b_zero=(),
        )
        tree = ValueStreamTree(
            delivery_event_id="E-del",
            anchor_event_ids=frozenset({"E-dem"}),
            activity_ids=frozenset({"A-01", "A-flow"}),
            node_ids=frozenset({"E-dem", "A-01", "A-flow", "E-del"}),
            edge_keys=frozenset(),
            node_scores={},
            total_relevance=1.0,
        )
        isolated = self.isolate_subgraph(
            documents,
            "A-01",
            value_input=value_input,
            value_stream_trees=(tree,),
        )
        ids = self._node_ids(isolated)
        self.assertEqual(
            ids,
            {"A-01", "P-01", "M-01", "A-flow", "E-dem", "E-del"},
        )

    def test_filter_then_isolate_composes(self):
        graph_filter = self.GraphFilter(
            node_types=frozenset({"Activity", "Process", "Metric"}),
            relationship_types=frozenset({"AFFECTS", "PART_OF"}),
            isolation_seed_id="P-01",
            relevance_pull_enabled=False,
        )
        filtered = self.filter_graph_document(self.documents, graph_filter)
        isolated = self.isolate_subgraph(filtered, graph_filter.isolation_seed_id)
        ids = self._node_ids(isolated)
        self.assertIn("P-01", ids)
        self.assertIn("A-01", ids)
        self.assertIn("M-01", ids)
        self.assertNotIn("M-02", ids)


class TestExplainActivityRelevance(unittest.TestCase):
    """ui2-07-relevance-explain: highlight sets for activity relevance (AC-EXPLAIN-1, D20–D21)."""

    @classmethod
    def setUpClass(cls):
        from optimizer.application.graph_filter import explain_activity_relevance
        from optimizer.application.scenario_models import RelevanceHighlight

        cls.explain_activity_relevance = staticmethod(explain_activity_relevance)
        cls.RelevanceHighlight = RelevanceHighlight

        from tests.fixtures.scenario.relevance_explain_factory import (
            a26_relevance_explain_graph_documents,
            a26_value_scenario,
            expected_a26_highlight_edge_keys,
            expected_a26_highlight_node_ids,
        )

        cls.documents = a26_relevance_explain_graph_documents()
        cls.value_input = a26_value_scenario()
        cls.expected_nodes = expected_a26_highlight_node_ids()
        cls.expected_edges = expected_a26_highlight_edge_keys()

    def test_returns_relevance_highlight_dto(self):
        highlight = self.explain_activity_relevance(
            self.documents,
            self.value_input,
            "A-26",
        )
        self.assertIsInstance(highlight, self.RelevanceHighlight)

    def test_a26_highlight_includes_g_and_j_path_nodes(self):
        highlight = self.explain_activity_relevance(
            self.documents,
            self.value_input,
            "A-26",
        )
        self.assertEqual(highlight.node_ids, self.expected_nodes)

    def test_a26_highlight_includes_connecting_edges(self):
        highlight = self.explain_activity_relevance(
            self.documents,
            self.value_input,
            "A-26",
        )
        self.assertEqual(highlight.edge_keys, self.expected_edges)

    def test_unrelated_nodes_not_in_highlight(self):
        highlight = self.explain_activity_relevance(
            self.documents,
            self.value_input,
            "A-26",
        )
        for noise_id in ("A-27", "P-06", "M-03"):
            self.assertNotIn(noise_id, highlight.node_ids)


class TestMergeExplainHighlight(unittest.TestCase):
    """Explain paths survive relationship type filters via merge."""

    @classmethod
    def setUpClass(cls):
        from optimizer.application.graph_filter import (
            filter_graph_document,
            merge_explain_highlight_into_documents,
        )
        from optimizer.application.scenario_models import GraphFilter
        from optimizer.application.value_insights import build_relevance_explain_paths

        cls.filter_graph_document = staticmethod(filter_graph_document)
        cls.merge_explain_highlight_into_documents = staticmethod(
            merge_explain_highlight_into_documents
        )
        cls.GraphFilter = GraphFilter
        cls.build_relevance_explain_paths = staticmethod(build_relevance_explain_paths)

        from tests.fixtures.scenario.relevance_explain_factory import (
            a26_relevance_explain_graph_documents,
            a26_value_scenario,
        )

        cls.documents = a26_relevance_explain_graph_documents()
        cls.value_input = a26_value_scenario()

    def test_merge_restores_touches_signals_when_rel_filter_is_affects_only(self):
        highlight = self.build_relevance_explain_paths(
            self.documents,
            self.value_input,
            "A-26",
        )
        affects_only = self.GraphFilter(
            node_types=None,
            relationship_types=frozenset({"AFFECTS"}),
            isolation_seed_id=None,
            relevance_pull_enabled=False,
            explain_activity_id="A-26",
        )
        filtered = self.filter_graph_document(self.documents, affects_only)
        merged = self.merge_explain_highlight_into_documents(
            filtered,
            self.documents,
            highlight,
        )
        rel_types = {rel.type.upper() for rel in merged[0].relationships}
        self.assertIn("TOUCHES", rel_types)
        self.assertIn("SIGNALS", rel_types)
        node_ids = {node.id for node in merged[0].nodes}
        self.assertIn("CJS-04", node_ids)
        self.assertIn("M-04", node_ids)


if __name__ == "__main__":
    unittest.main()
