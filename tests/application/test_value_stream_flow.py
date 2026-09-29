"""Tests for Valor-tab flow story selection."""

from __future__ import annotations

import unittest

from optimizer.application.run_scenario_view import run_scenario_view
from optimizer.application.run_demo_scenario import run_demo_scenario
from optimizer.application.value_stream_flow import (
    build_flow_graph_for_selection,
    default_flow_story_index,
    list_flow_story_options,
)
from optimizer.infrastructure.demo_loader import resolve_repo_root
from tests.fixtures.graph_analytics.vs_graph_factory import (
    shared_backbone_graph_documents,
    shared_backbone_value_input,
)


class TestFlowStoryOptions(unittest.TestCase):
    def test_fused_option_listed_first_on_shared_backbone(self):
        from optimizer.graph_analytics.graph_bridge import build_graph_context
        from optimizer.graph_analytics.value_streams import discover_value_streams
        from optimizer.application.scenario_models import GraphFilter

        ctx = build_graph_context(
            shared_backbone_graph_documents(),
            shared_backbone_value_input(),
        )
        discovery = discover_value_streams(ctx, merge_crossing=False)
        vm = run_scenario_view(
            shared_backbone_graph_documents(),
            shared_backbone_value_input(),
            graph_filter=GraphFilter(
                node_types=None,
                relationship_types=None,
                isolation_seed_id=None,
                relevance_pull_enabled=False,
            ),
        )
        # run_scenario_view overwrites graph_context - patch via new vm fields
        from optimizer.application.scenario_models import ScenarioViewModel

        vm = ScenarioViewModel(
            scenario=None,
            graph_network=vm.graph_network,
            metrics=vm.metrics,
            matrix_rows=vm.matrix_rows,
            strategic_b_zero=vm.strategic_b_zero,
            activities=vm.activities,
            plot_series=vm.plot_series,
            metric_label_by_id=vm.metric_label_by_id,
            event_label_by_id=vm.event_label_by_id,
            process_label_by_id=vm.process_label_by_id,
            available_node_types=vm.available_node_types,
            available_relationship_types=vm.available_relationship_types,
            graph_documents=vm.graph_documents,
            value_stream_discovery=discovery,
            catalog_findings=vm.catalog_findings,
            graph_context=ctx,
        )
        options = list_flow_story_options(vm)
        self.assertGreaterEqual(len(options), 2)
        self.assertTrue(options[0].is_fused)
        self.assertTrue(options[0].label.startswith("Fusionada"))
        self.assertEqual(default_flow_story_index(options), 0)
        flow = build_flow_graph_for_selection(vm, options[0])
        self.assertIsNotNone(flow)

    def test_energoil_v3_includes_fused_story(self):
        repo = resolve_repo_root()
        vm = run_demo_scenario("energoil_mexico_v3", repo_root=repo)
        options = list_flow_story_options(vm)
        fused = [option for option in options if option.is_fused]
        self.assertGreaterEqual(len(fused), 1)
        self.assertIn("Fusionada", fused[0].label)
        self.assertIn("historias", fused[0].label)

    def test_eneroil_real_v1_flow_activities_show_names(self):
        repo = resolve_repo_root()
        vm = run_demo_scenario("eneroil_real_v1", repo_root=repo)
        options = list_flow_story_options(vm)
        self.assertGreaterEqual(len(options), 1)
        flow = build_flow_graph_for_selection(vm, options[0])
        self.assertIsNotNone(flow)
        assert flow is not None
        activities = [node for node in flow.nodes if node.kind == "activity"]
        self.assertGreaterEqual(len(activities), 1)
        for node in activities:
            self.assertIn(" — ", node.label, f"{node.id} missing name in label")
            self.assertFalse(node.label.endswith(node.id) or node.label == node.id)

        from optimizer.application.scenario_models import GraphFilter

        repo = resolve_repo_root()
        vm = run_demo_scenario(
            "energoil_mexico_v3",
            repo_root=repo,
            graph_filter=GraphFilter(
                node_types=None,
                relationship_types=None,
                isolation_seed_id=None,
                relevance_pull_enabled=False,
                value_stream_merge_crossing=True,
            ),
        )
        options = list_flow_story_options(vm)
        per_delivery = [option for option in options if not option.is_fused]
        self.assertGreaterEqual(len(per_delivery), 5)
        self.assertTrue(any(option.is_fused for option in options))


if __name__ == "__main__":
    unittest.main()
