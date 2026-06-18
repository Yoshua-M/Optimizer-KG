"""
Tests for ga-07-runners-support-t-a: technology + procurement runners.

Run: python3 -m unittest tests.graph_analytics.test_runners_support_ta -v
"""

from __future__ import annotations

import unittest

from tests.fixtures.graph_analytics.vs_graph_factory import (
    value_stream_graph_documents,
    value_stream_value_input,
)


class TestTechProcurementRunners(unittest.TestCase):
    """ga-07: T-01 and A-01 smoke contracts."""

    @classmethod
    def setUpClass(cls):
        from optimizer.graph_analytics.graph_bridge import build_graph_context
        from optimizer.graph_analytics.models import AnalyticStatus
        from optimizer.graph_analytics.runners.procurement import run_a01
        from optimizer.graph_analytics.runners.tech import run_t01, run_t04

        cls.build_graph_context = staticmethod(build_graph_context)
        cls.run_t01 = staticmethod(run_t01)
        cls.run_t04 = staticmethod(run_t04)
        cls.run_a01 = staticmethod(run_a01)
        cls.AnalyticStatus = AnalyticStatus
        cls.ctx = cls.build_graph_context(
            value_stream_graph_documents(),
            value_stream_value_input(),
        )

    def test_t01_returns_structured_finding(self):
        finding = self.run_t01(self.ctx)
        self.assertEqual(finding.analytic_id, "T-01")
        self.assertIn(
            finding.status,
            (self.AnalyticStatus.OK, self.AnalyticStatus.ERROR),
        )

    def test_t04_panel_only_no_highlight(self):
        finding = self.run_t04(self.ctx)
        self.assertEqual(finding.analytic_id, "T-04")
        self.assertIsNone(finding.highlight)

    def test_a01_returns_structured_finding(self):
        finding = self.run_a01(self.ctx)
        self.assertEqual(finding.analytic_id, "A-01")


if __name__ == "__main__":
    unittest.main()
