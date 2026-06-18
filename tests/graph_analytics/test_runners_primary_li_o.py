"""
Tests for ga-08-runners-primary-li-o: internal logistics + operations runners.

Run: python3 -m unittest tests.graph_analytics.test_runners_primary_li_o -v
"""

from __future__ import annotations

import unittest

from langchain_community.graphs.graph_document import GraphDocument, Node, Relationship
from langchain_core.documents import Document

from optimizer.application.scenario_models import (
    ActivityRow,
    ActivityScoreRow,
    MetricRow,
    ValueScenarioInput,
)


def _critical_path_fixture():
    """LI-01 / O-01: chain A-01 -> A-02 -> A-03 with durations on edges."""
    a1 = Node(id="A-01", type="Activity", properties={"area": "logistica_interna"})
    a2 = Node(id="A-02", type="Activity", properties={"area": "logistica_interna"})
    a3 = Node(id="A-03", type="Activity", properties={"area": "logistica_interna"})
    rels = [
        Relationship(source=a1, target=a2, type="PRECEDES", properties={"duracion": 2}),
        Relationship(source=a2, target=a3, type="PRECEDES", properties={"duracion": 5}),
    ]
    docs = [
        GraphDocument(
            nodes=[a1, a2, a3],
            relationships=rels,
            source=Document(page_content="critical path"),
        )
    ]
    value = ValueScenarioInput(
        metrics=(MetricRow(id="M-01", name="M", definition="", client_need=""),),
        activities=(
            ActivityRow(
                activity_id="A-01",
                activity_name="R1",
                process_id="P-01",
                p=0.5,
                c=0.5,
                f=0.5,
                r=0.5,
                v=0.5,
                scores=(),
            ),
            ActivityRow(
                activity_id="A-02",
                activity_name="R2",
                process_id="P-01",
                p=0.5,
                c=0.5,
                f=0.5,
                r=0.5,
                v=0.5,
                scores=(),
            ),
            ActivityRow(
                activity_id="A-03",
                activity_name="R3",
                process_id="P-01",
                p=0.5,
                c=0.5,
                f=0.5,
                r=0.5,
                v=0.5,
                scores=(),
            ),
        ),
        process_rollups=(),
        strategic_b_zero=(),
    )
    return docs, value


class TestPrimaryLogisticsOperationsRunners(unittest.TestCase):
    """ga-08: LI-01 critical path and O-04 k-core smoke."""

    @classmethod
    def setUpClass(cls):
        from optimizer.graph_analytics.graph_bridge import build_graph_context
        from optimizer.graph_analytics.models import AnalyticStatus
        from optimizer.graph_analytics.runners.internal_logistics import run_li01
        from optimizer.graph_analytics.runners.operations import run_o04

        cls.build_graph_context = staticmethod(build_graph_context)
        cls.run_li01 = staticmethod(run_li01)
        cls.run_o04 = staticmethod(run_o04)
        cls.AnalyticStatus = AnalyticStatus
        docs, value = _critical_path_fixture()
        cls.ctx = cls.build_graph_context(docs, value)

    def test_li01_critical_path_includes_longest_chain(self):
        finding = self.run_li01(self.ctx)
        self.assertEqual(finding.analytic_id, "LI-01")
        if finding.status == self.AnalyticStatus.OK:
            self.assertIsNotNone(finding.highlight)
            highlighted = finding.highlight.node_ids
            self.assertTrue({"A-01", "A-02", "A-03"} <= highlighted)

    def test_o04_returns_kcore_finding(self):
        finding = self.run_o04(self.ctx)
        self.assertEqual(finding.analytic_id, "O-04")


if __name__ == "__main__":
    unittest.main()
