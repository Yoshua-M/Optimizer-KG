"""
Tests for ui2-01-value-insights: shared plot analytics on ValueScenarioInput.

Does not import demo_loader (per change spec).

Run from project root:
    python3 -m unittest tests.application.test_value_insights -v
"""

from __future__ import annotations

import math
import unittest

from tests.fixtures.scenario.value_scenario_factory import (
    minimal_value_scenario,
    multi_metric_value_scenario,
)


class TestValueInsights(unittest.TestCase):
    """ui2-01-value-insights: plot series, top-3, labels, edge map (AC-5, AC-6, D16)."""

    @classmethod
    def setUpClass(cls):
        from optimizer.application.scenario_models import PlotPoint
        from optimizer.application.value_insights import (
            build_edge_relevance_map,
            build_plot_series,
            build_top_contributions,
            format_metric_label,
            top_n_by_distance,
        )

        cls.PlotPoint = PlotPoint
        cls.build_edge_relevance_map = staticmethod(build_edge_relevance_map)
        cls.build_plot_series = staticmethod(build_plot_series)
        cls.build_top_contributions = staticmethod(build_top_contributions)
        cls.format_metric_label = staticmethod(format_metric_label)
        cls.top_n_by_distance = staticmethod(top_n_by_distance)

    def test_format_metric_label_includes_name(self):
        scenario = minimal_value_scenario()
        label = self.format_metric_label("M-01", scenario.metrics)
        self.assertIn("M-01", label)
        self.assertIn("On-Time Delivery", label)

    def test_top_n_by_distance_ranks_farthest_from_origin(self):
        points = (
            self.PlotPoint(
                entity_id="A-01",
                entity_name="Near",
                x=1.0,
                y=0.0,
                distance_from_origin=1.0,
            ),
            self.PlotPoint(
                entity_id="A-02",
                entity_name="Far",
                x=3.0,
                y=4.0,
                distance_from_origin=5.0,
            ),
            self.PlotPoint(
                entity_id="A-03",
                entity_name="Mid",
                x=0.0,
                y=2.0,
                distance_from_origin=2.0,
            ),
        )
        top = self.top_n_by_distance(points, n=3)
        self.assertEqual([p.entity_id for p in top], ["A-02", "A-03", "A-01"])

    def test_top_n_excludes_zero_distance_points(self):
        points = (
            self.PlotPoint(
                entity_id="A-zero",
                entity_name="Origin",
                x=0.0,
                y=0.0,
                distance_from_origin=0.0,
            ),
            self.PlotPoint(
                entity_id="A-far",
                entity_name="Far",
                x=3.0,
                y=4.0,
                distance_from_origin=5.0,
            ),
        )
        top = self.top_n_by_distance(points, n=3)
        self.assertEqual(len(top), 1)
        self.assertEqual(top[0].entity_id, "A-far")

    def test_relevance_plot_uses_max_relevance_and_metric_count(self):
        series = self.build_plot_series(multi_metric_value_scenario())
        a1 = next(p for p in series.relevance_scatter if p.entity_id == "A-01")
        self.assertAlmostEqual(a1.x, 0.5)
        self.assertEqual(a1.y, 2)

    def test_v_relevance_plot_uses_v_and_max_relevance(self):
        series = self.build_plot_series(multi_metric_value_scenario())
        a1 = next(p for p in series.v_relevance_scatter if p.entity_id == "A-01")
        self.assertAlmostEqual(a1.x, 0.9)
        self.assertAlmostEqual(a1.y, 0.5)

    def test_v_plot_uses_activity_v_and_process_count(self):
        series = self.build_plot_series(multi_metric_value_scenario())
        a1 = next(p for p in series.v_scatter if p.entity_id == "A-01")
        self.assertAlmostEqual(a1.x, 0.9)
        self.assertEqual(a1.y, 1)

    def test_process_plot_aggregates_rollups_per_process(self):
        series = self.build_plot_series(multi_metric_value_scenario())
        p1 = next(p for p in series.process_scatter if p.entity_id == "P-01")
        self.assertAlmostEqual(p1.x, 1.1)
        self.assertEqual(p1.y, 2)
        p2 = next(p for p in series.process_scatter if p.entity_id == "P-02")
        self.assertAlmostEqual(p2.x, 0.9)
        self.assertEqual(p2.y, 1)

    def test_strategic_b_zero_excluded_from_relevance_scatter(self):
        scenario = minimal_value_scenario(include_b_zero=True)
        series = self.build_plot_series(scenario)
        relevance_ids = {p.entity_id for p in series.relevance_scatter}
        v_rel_ids = {p.entity_id for p in series.v_relevance_scatter}
        self.assertIn("A-01", relevance_ids)
        self.assertNotIn("A-02", relevance_ids)
        self.assertNotIn("A-02", v_rel_ids)

    def test_build_edge_relevance_map_activity_to_metric(self):
        scenario = minimal_value_scenario()
        edge_map = self.build_edge_relevance_map(scenario)
        self.assertAlmostEqual(edge_map[("A-01", "M-01")], 0.2)

    def test_plot_series_includes_top_three_per_plot(self):
        series = self.build_plot_series(multi_metric_value_scenario())
        for attr in (
            "top_relevance",
            "top_v",
            "top_v_relevance",
            "top_process",
        ):
            top = getattr(series, attr)
            self.assertLessEqual(len(top), 3)
            for point in top:
                self.assertGreater(point.distance_from_origin, 0)

    def test_top_contributions_sorted_by_pct_with_metric_labels(self):
        scenario = multi_metric_value_scenario()
        contributions = self.build_top_contributions(scenario, n=3)
        self.assertGreaterEqual(len(contributions), 1)
        first = contributions[0]
        self.assertIn("P-02", first.process_id)
        self.assertIn("Metric Two", first.metric_label)
        self.assertGreater(first.pct_contribution, 0)

    def test_euclidean_distance_computed_when_not_provided(self):
        """PlotPoint distance may be computed inside build_plot_series."""
        series = self.build_plot_series(multi_metric_value_scenario())
        for point in series.relevance_scatter:
            expected = math.hypot(point.x, point.y)
            self.assertAlmostEqual(point.distance_from_origin, expected)


class TestRelevanceExplainPaths(unittest.TestCase):
    """ui2-07: build_relevance_explain_paths on ValueScenarioInput + graph (D21)."""

    @classmethod
    def setUpClass(cls):
        from optimizer.application.value_insights import build_relevance_explain_paths

        cls.build_relevance_explain_paths = staticmethod(build_relevance_explain_paths)

        from tests.fixtures.scenario.relevance_explain_factory import (
            a26_relevance_explain_graph_documents,
            a26_value_scenario,
            expected_a26_highlight_node_ids,
        )

        cls.documents = a26_relevance_explain_graph_documents()
        cls.value_input = a26_value_scenario()
        cls.expected_nodes = expected_a26_highlight_node_ids()

    def test_build_paths_matches_a26_fixture(self):
        highlight = self.build_relevance_explain_paths(
            self.documents,
            self.value_input,
            "A-26",
        )
        self.assertEqual(highlight.node_ids, self.expected_nodes)

    def test_zero_relevance_activity_yields_empty_or_minimal_highlight(self):
        from optimizer.application.scenario_models import ActivityRow

        empty_activity = ActivityRow(
            activity_id="A-99",
            activity_name="No scores",
            process_id="P-99",
            p=0.0,
            c=0.0,
            f=0.0,
            r=0.0,
            v=0.0,
            scores=(),
        )
        from optimizer.application.scenario_models import ValueScenarioInput

        scenario = ValueScenarioInput(
            metrics=self.value_input.metrics,
            activities=(empty_activity,),
            process_rollups=(),
            strategic_b_zero=(),
        )
        highlight = self.build_relevance_explain_paths(
            self.documents,
            scenario,
            "A-99",
        )
        self.assertLessEqual(len(highlight.node_ids), 1)


class TestIndirectRelevanceMap(unittest.TestCase):
    """ui2-08: indirect activity→metric scores without direct AFFECTS (D23)."""

    @classmethod
    def setUpClass(cls):
        from optimizer.application.value_insights import build_indirect_relevance_map

        cls.build_indirect_relevance_map = staticmethod(build_indirect_relevance_map)

        from tests.fixtures.scenario.relevance_explain_factory import (
            a26_relevance_explain_graph_documents,
            a26_value_scenario,
            punto_ciego_graph_documents,
        )

        cls.a26_documents = a26_relevance_explain_graph_documents()
        cls.a26_value = a26_value_scenario()
        cls.punto_docs = punto_ciego_graph_documents()

    def test_indirect_pairs_when_no_direct_affects(self):
        indirect = self.build_indirect_relevance_map(self.a26_documents, self.a26_value)
        self.assertIn(("A-26", "M-04"), indirect)
        self.assertIn(("A-26", "M-05"), indirect)
        self.assertIn(("A-26", "M-06"), indirect)

    def test_direct_affects_not_in_indirect_map(self):
        indirect = self.build_indirect_relevance_map(self.a26_documents, self.a26_value)
        self.assertNotIn(("A-26", "M-01"), indirect)
        self.assertNotIn(("A-26", "M-02"), indirect)

    def test_punto_ciego_fixture_identifies_journey_only_metric(self):
        from optimizer.application.scenario_models import (
            ActivityRow,
            ActivityScoreRow,
            MetricRow,
            ValueScenarioInput,
        )

        scenario = ValueScenarioInput(
            metrics=(
                MetricRow(id="M-01", name="", definition="", client_need=""),
                MetricRow(id="M-04", name="", definition="", client_need=""),
            ),
            activities=(
                ActivityRow(
                    activity_id="A-01",
                    activity_name="Test",
                    process_id="P-01",
                    p=0.5,
                    c=0.5,
                    f=0.5,
                    r=0.5,
                    v=0.5,
                    scores=(
                        ActivityScoreRow(
                            metric_id="M-01",
                            g=1.0,
                            j=0.0,
                            dv=0.0,
                            b=0.5,
                            relevance=0.5,
                            pct_contribution=0.5,
                        ),
                        ActivityScoreRow(
                            metric_id="M-04",
                            g=0.0,
                            j=0.7,
                            dv=0.0,
                            b=0.3,
                            relevance=0.27,
                            pct_contribution=0.3,
                        ),
                    ),
                ),
            ),
            process_rollups=(),
            strategic_b_zero=(),
        )
        indirect = self.build_indirect_relevance_map(self.punto_docs, scenario)
        self.assertIn(("A-01", "M-04"), indirect)
        self.assertNotIn(("A-01", "M-01"), indirect)


if __name__ == "__main__":
    unittest.main()
