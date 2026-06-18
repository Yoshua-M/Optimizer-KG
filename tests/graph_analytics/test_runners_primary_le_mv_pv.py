"""
Tests for ga-09-runners-primary-le-mv-pv: external logistics, marketing, postsale.

Run: python3 -m unittest tests.graph_analytics.test_runners_primary_le_mv_pv -v
"""

from __future__ import annotations

import unittest

from tests.fixtures.graph_analytics.vs_graph_factory import (
    value_stream_graph_documents,
    value_stream_value_input,
)


class TestPrimaryLeMvPvRunners(unittest.TestCase):
    """ga-09: LE-01, MV-03, PV-01, PV-03 panel-only smoke."""

    @classmethod
    def setUpClass(cls):
        from optimizer.graph_analytics.graph_bridge import build_graph_context
        from optimizer.graph_analytics.models import AnalyticStatus
        from optimizer.graph_analytics.runners.external_logistics import run_le01
        from optimizer.graph_analytics.runners.marketing import run_mv03, run_mv04
        from optimizer.graph_analytics.runners.postsale import run_pv01, run_pv03

        cls.build_graph_context = staticmethod(build_graph_context)
        cls.run_le01 = staticmethod(run_le01)
        cls.run_mv03 = staticmethod(run_mv03)
        cls.run_mv04 = staticmethod(run_mv04)
        cls.run_pv01 = staticmethod(run_pv01)
        cls.run_pv03 = staticmethod(run_pv03)
        cls.AnalyticStatus = AnalyticStatus
        cls.ctx = cls.build_graph_context(
            value_stream_graph_documents(),
            value_stream_value_input(),
        )

    def test_le01_returns_structured_finding(self):
        finding = self.run_le01(self.ctx)
        self.assertEqual(finding.analytic_id, "LE-01")

    def test_mv03_lookup_relevance_finding(self):
        finding = self.run_mv03(self.ctx)
        self.assertEqual(finding.analytic_id, "MV-03")

    def test_mv04_panel_only(self):
        finding = self.run_mv04(self.ctx)
        self.assertEqual(finding.analytic_id, "MV-04")
        self.assertIsNone(finding.highlight)

    def test_pv01_critical_path_finding(self):
        finding = self.run_pv01(self.ctx)
        self.assertEqual(finding.analytic_id, "PV-01")

    def test_pv03_panel_only_bayesian(self):
        finding = self.run_pv03(self.ctx)
        self.assertEqual(finding.analytic_id, "PV-03")
        self.assertIsNone(finding.highlight)


if __name__ == "__main__":
    unittest.main()
