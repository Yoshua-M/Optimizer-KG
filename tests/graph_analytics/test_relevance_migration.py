"""
Tests for ga-04-migrate-relevance-plots: domain relevance/plot logic (migrated from application).

Run: python3 -m unittest tests.graph_analytics.test_relevance_migration -v
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MINIMAL_FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "demo" / "minimal"


class TestRelevanceMigration(unittest.TestCase):
    """ga-04: graph_analytics.relevance matches former value_insights behavior."""

    @classmethod
    def setUpClass(cls):
        from optimizer.graph_analytics.relevance import (
            build_edge_relevance_map,
            build_indirect_relevance_map,
            build_relevance_explain_paths,
        )
        from optimizer.infrastructure.demo_loader import graph_json_to_graph_documents

        from tests.fixtures.scenario.relevance_explain_factory import (
            explain_relevance_scenario,
        )
        from tests.fixtures.scenario.value_scenario_factory import (
            minimal_value_scenario,
            multi_metric_value_scenario,
        )

        cls.build_edge_relevance_map = staticmethod(build_edge_relevance_map)
        cls.build_indirect_relevance_map = staticmethod(build_indirect_relevance_map)
        cls.build_relevance_explain_paths = staticmethod(build_relevance_explain_paths)
        cls.graph_json_to_graph_documents = staticmethod(graph_json_to_graph_documents)
        cls.minimal_value_scenario = staticmethod(minimal_value_scenario)
        cls.multi_metric_value_scenario = staticmethod(multi_metric_value_scenario)
        cls.explain_relevance_scenario = staticmethod(explain_relevance_scenario)

        graph = json.loads((MINIMAL_FIXTURE / "graph.json").read_text(encoding="utf-8"))
        cls.minimal_docs = cls.graph_json_to_graph_documents(graph)

    def test_edge_relevance_map_from_activity_scores(self):
        scenario = self.minimal_value_scenario()
        edge_map = self.build_edge_relevance_map(scenario)
        self.assertAlmostEqual(edge_map[("A-01", "M-01")], 0.2)

    def test_explain_paths_include_activity_and_metric_for_g_score(self):
        scenario, documents, activity_id = self.explain_relevance_scenario()
        highlight = self.build_relevance_explain_paths(
            documents,
            scenario,
            activity_id,
        )
        self.assertIn(activity_id, highlight.node_ids)
        self.assertTrue(highlight.edge_keys)

    def test_indirect_relevance_map_when_pull_enabled(self):
        scenario = self.multi_metric_value_scenario()
        indirect = self.build_indirect_relevance_map(self.minimal_docs, scenario)
        self.assertIsInstance(indirect, dict)


class TestPlotsMigration(unittest.TestCase):
    """ga-04: graph_analytics.plots builds PlotSeries from ValueScenarioInput."""

    @classmethod
    def setUpClass(cls):
        from optimizer.graph_analytics.plots import build_plot_series

        from tests.fixtures.scenario.value_scenario_factory import (
            multi_metric_value_scenario,
        )

        cls.build_plot_series = staticmethod(build_plot_series)
        cls.multi_metric_value_scenario = staticmethod(multi_metric_value_scenario)

    def test_plot_series_has_four_scatter_families(self):
        series = self.build_plot_series(self.multi_metric_value_scenario())
        self.assertTrue(len(series.relevance_scatter) >= 1)
        self.assertTrue(hasattr(series, "top_v_relevance"))


class TestApplicationReexportShim(unittest.TestCase):
    """ga-04: application.value_insights delegates to graph_analytics."""

    def test_value_insights_reexports_build_edge_relevance_map(self):
        from optimizer.application import value_insights
        from optimizer.graph_analytics import relevance as domain_relevance

        self.assertIs(
            value_insights.build_edge_relevance_map,
            domain_relevance.build_edge_relevance_map,
        )


if __name__ == "__main__":
    unittest.main()
