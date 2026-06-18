"""
Tests for ga-01-scaffold-deps-types: domain models and public enums.

Run: python3 -m unittest tests.graph_analytics.test_models -v
"""

from __future__ import annotations

import unittest


EXPECTED_ANALYTIC_IDS = (
    "G-01",
    "G-02",
    "G-03",
    "G-04",
    "H-01",
    "H-02",
    "H-03",
    "H-04",
    "T-01",
    "T-02",
    "T-03",
    "T-04",
    "A-01",
    "A-02",
    "A-03",
    "A-04",
    "LI-01",
    "LI-02",
    "LI-03",
    "O-01",
    "O-02",
    "O-03",
    "O-04",
    "LE-01",
    "LE-02",
    "LE-03",
    "LE-04",
    "MV-01",
    "MV-02",
    "MV-03",
    "MV-04",
    "PV-01",
    "PV-02",
    "PV-03",
    "PV-04",
    "PV-05",
)

PANEL_ONLY_ANALYTIC_IDS = frozenset({"H-04", "T-04", "O-03", "MV-04", "PV-03"})


class TestGraphAnalyticsModels(unittest.TestCase):
    """ga-01: frozen domain types for findings, highlights, VS results."""

    @classmethod
    def setUpClass(cls):
        from optimizer.graph_analytics.models import (
            ActivityCategory,
            AnalyticFinding,
            AnalyticStatus,
            HighlightPayload,
            ValueStreamDiscoveryResult,
            ValueStreamTree,
        )

        cls.ActivityCategory = ActivityCategory
        cls.AnalyticFinding = AnalyticFinding
        cls.AnalyticStatus = AnalyticStatus
        cls.HighlightPayload = HighlightPayload
        cls.ValueStreamTree = ValueStreamTree
        cls.ValueStreamDiscoveryResult = ValueStreamDiscoveryResult

    def test_activity_category_enum_values(self):
        self.assertEqual(self.ActivityCategory.VALUE_STREAM.value, "value_stream")
        self.assertEqual(self.ActivityCategory.STRUCTURAL_SUPPORT.value, "structural_support")
        self.assertEqual(self.ActivityCategory.SEMANTIC_SUPPORT.value, "semantic_support")
        self.assertEqual(self.ActivityCategory.WASTE.value, "waste")

    def test_highlight_payload_accepts_arbitrary_node_ids(self):
        payload = self.HighlightPayload(
            node_ids=frozenset({"A-01", "Team-1", "System-X"}),
            edge_keys=frozenset({("A-01", "M-01", "AFFECTS")}),
            scores={"A-01": 0.8},
        )
        self.assertIn("Team-1", payload.node_ids)
        self.assertEqual(payload.scores["A-01"], 0.8)

    def test_analytic_finding_success_shape(self):
        finding = self.AnalyticFinding(
            analytic_id="G-01",
            title="Detección de gobernanza dominante",
            summary="Qué descubrimos: …",
            detail="Por qué funciona: …",
            status=self.AnalyticStatus.OK,
            scores={"A-GOV": 1.0},
            highlight=self.HighlightPayload(node_ids=frozenset({"A-GOV"})),
            error_message=None,
        )
        self.assertEqual(finding.analytic_id, "G-01")
        self.assertIsNone(finding.error_message)
        self.assertIsNotNone(finding.highlight)

    def test_analytic_finding_error_shape_spanish_message(self):
        finding = self.AnalyticFinding(
            analytic_id="G-01",
            title="G-01",
            summary="",
            detail="",
            status=self.AnalyticStatus.ERROR,
            scores={},
            highlight=None,
            error_message="Datos insuficientes: falta event_type en Eventos",
        )
        self.assertEqual(finding.status, self.AnalyticStatus.ERROR)
        self.assertIn("insuficientes", finding.error_message.lower())

    def test_value_stream_tree_shape(self):
        tree = self.ValueStreamTree(
            delivery_event_id="EV-V1",
            anchor_event_ids=frozenset({"EV-D1"}),
            activity_ids=frozenset({"A-01", "A-02"}),
            node_ids=frozenset({"EV-D1", "A-01", "A-02", "EV-V1"}),
            edge_keys=frozenset({("A-01", "A-02", "PRECEDES")}),
            node_scores={"A-01": 1.0, "A-02": 0.5},
            total_relevance=1.5,
        )
        self.assertEqual(tree.delivery_event_id, "EV-V1")
        self.assertIn("A-01", tree.activity_ids)

    def test_value_stream_discovery_result_includes_union_and_classifications(self):
        tree = self.ValueStreamTree(
            delivery_event_id="EV-V1",
            anchor_event_ids=frozenset({"EV-D1"}),
            activity_ids=frozenset({"A-01"}),
            node_ids=frozenset({"EV-D1", "A-01", "EV-V1"}),
            edge_keys=frozenset(),
            node_scores={"A-01": 0.5},
            total_relevance=0.5,
        )
        result = self.ValueStreamDiscoveryResult(
            trees=(tree,),
            vs_union=frozenset({"A-01"}),
            classifications={"A-01": self.ActivityCategory.VALUE_STREAM},
            group_count=1,
            avg_group_size=2.0,
        )
        self.assertIn("A-01", result.vs_union)
        self.assertEqual(
            result.classifications["A-01"],
            self.ActivityCategory.VALUE_STREAM,
        )

    def test_expected_catalog_id_count_is_thirty_six(self):
        self.assertEqual(len(EXPECTED_ANALYTIC_IDS), 36)


if __name__ == "__main__":
    unittest.main()
