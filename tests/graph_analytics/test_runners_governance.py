"""
Tests for ga-06-runners-support-g-h: governance + HR catalog runners.

Run: python3 -m unittest tests.graph_analytics.test_runners_governance -v
"""

from __future__ import annotations

import unittest

from tests.fixtures.graph_analytics.vs_graph_factory import (
    governance_graph_documents,
    governance_value_input,
)


class TestGovernanceRunners(unittest.TestCase):
    """ga-06: G-01 … G-04 representative contracts."""

    @classmethod
    def setUpClass(cls):
        from optimizer.graph_analytics.graph_bridge import build_graph_context
        from optimizer.graph_analytics.models import AnalyticStatus
        from optimizer.graph_analytics.runners.governance import run_g01, run_g02

        cls.build_graph_context = staticmethod(build_graph_context)
        cls.run_g01 = staticmethod(run_g01)
        cls.run_g02 = staticmethod(run_g02)
        cls.AnalyticStatus = AnalyticStatus
        cls.ctx = cls.build_graph_context(
            governance_graph_documents(),
            governance_value_input(),
        )

    def test_g01_finding_highlights_governance_dominator(self):
        finding = self.run_g01(self.ctx)
        self.assertEqual(finding.analytic_id, "G-01")
        self.assertEqual(finding.status, self.AnalyticStatus.OK)
        self.assertIsNotNone(finding.highlight)
        self.assertIn("A-GOV", finding.highlight.node_ids)

    def test_g01_executive_copy_not_empty_spanish(self):
        finding = self.run_g01(self.ctx)
        self.assertIn("descubrimos", finding.summary.lower())

    def test_g02_returns_fragility_scores_for_governance_nodes(self):
        finding = self.run_g02(self.ctx)
        self.assertEqual(finding.analytic_id, "G-02")
        self.assertTrue(finding.scores)
        self.assertIn("A-GOV", finding.scores)


class TestHrRunnerSmoke(unittest.TestCase):
    """ga-06: H-01 smoke — returns structured finding or Spanish error."""

    @classmethod
    def setUpClass(cls):
        from optimizer.graph_analytics.graph_bridge import build_graph_context
        from optimizer.graph_analytics.models import AnalyticStatus
        from optimizer.graph_analytics.runners.hr import run_h01

        from tests.fixtures.graph_analytics.vs_graph_factory import (
            value_stream_graph_documents,
            value_stream_value_input,
        )

        cls.build_graph_context = staticmethod(build_graph_context)
        cls.run_h01 = staticmethod(run_h01)
        cls.AnalyticStatus = AnalyticStatus
        cls.ctx = cls.build_graph_context(
            value_stream_graph_documents(),
            value_stream_value_input(),
        )

    def test_h01_returns_ok_or_error_not_exception(self):
        finding = self.run_h01(self.ctx)
        self.assertEqual(finding.analytic_id, "H-01")
        self.assertIn(
            finding.status,
            (self.AnalyticStatus.OK, self.AnalyticStatus.ERROR),
        )
        if finding.status == self.AnalyticStatus.ERROR:
            self.assertIn("insuficientes", finding.error_message.lower())


if __name__ == "__main__":
    unittest.main()
