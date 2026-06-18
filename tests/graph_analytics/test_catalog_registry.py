"""
Tests for ga-10-catalog-registry-facade: registry + run_catalog entrypoints.

Run: python3 -m unittest tests.graph_analytics.test_catalog_registry -v
"""

from __future__ import annotations

import unittest

from tests.graph_analytics.test_models import EXPECTED_ANALYTIC_IDS


class TestCatalogRegistry(unittest.TestCase):
    """ga-10: every catalog id registered and invocable via run_catalog."""

    @classmethod
    def setUpClass(cls):
        from optimizer.graph_analytics.graph_bridge import build_graph_context
        from optimizer.graph_analytics.models import AnalyticStatus
        from optimizer.graph_analytics.run_catalog import run_all_analytics, run_analytic
        from optimizer.graph_analytics.runners.registry import (
            get_runner,
            list_registered_analytic_ids,
        )
        from optimizer.infrastructure.demo_loader import (
            bundle_to_value_input,
            load_demo_bundle,
            resolve_repo_root,
        )

        cls.get_runner = staticmethod(get_runner)
        cls.list_registered_analytic_ids = staticmethod(list_registered_analytic_ids)
        cls.run_analytic = staticmethod(run_analytic)
        cls.run_all_analytics = staticmethod(run_all_analytics)
        cls.build_graph_context = staticmethod(build_graph_context)
        cls.AnalyticStatus = AnalyticStatus

        repo_root = resolve_repo_root()
        bundle = load_demo_bundle("energoil_mexico", repo_root=repo_root)
        cls.energoil_ctx = cls.build_graph_context(
            bundle.graph_documents,
            bundle_to_value_input(bundle),
        )

    def test_registry_lists_thirty_six_ids(self):
        registered = self.list_registered_analytic_ids()
        self.assertEqual(len(registered), 36)
        self.assertEqual(
            tuple(sorted(registered)),
            tuple(sorted(EXPECTED_ANALYTIC_IDS)),
        )

    def test_each_id_has_callable_runner(self):
        for analytic_id in EXPECTED_ANALYTIC_IDS:
            runner = self.get_runner(analytic_id)
            self.assertTrue(callable(runner), msg=analytic_id)

    def test_run_analytic_g01_on_energoil_returns_finding(self):
        finding = self.run_analytic(self.energoil_ctx, "G-01")
        self.assertEqual(finding.analytic_id, "G-01")
        self.assertIn(
            finding.status,
            (self.AnalyticStatus.OK, self.AnalyticStatus.ERROR),
        )

    def test_run_all_analytics_returns_thirty_six_findings(self):
        findings = self.run_all_analytics(self.energoil_ctx)
        self.assertEqual(len(findings), 36)
        ids = {f.analytic_id for f in findings}
        self.assertEqual(ids, set(EXPECTED_ANALYTIC_IDS))


if __name__ == "__main__":
    unittest.main()
