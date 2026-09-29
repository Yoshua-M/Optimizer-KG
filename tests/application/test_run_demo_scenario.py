"""
Tests for demo-03-facade and demo-05-tests (facade portion).

Contract (stage 03 TDD — implementation in 04_implement):
  run_demo_scenario(scenario_id, *, repo_root=None) -> ScenarioViewModel

Run from project root (editable install):
    python3 -m unittest tests.application.test_run_demo_scenario -v
"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pyvis.network import Network

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MINIMAL_FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "demo" / "minimal"
MATRIX_TOP_N = 15


def _write_minimal_demo_repo(root: Path, *, include_b_zero: bool = False) -> None:
    """Lay out configs/ + data/processed/demo/minimal_demo/ under root."""
    scenario_dir = root / "data" / "processed" / "demo" / "minimal_demo"
    scenario_dir.mkdir(parents=True)
    for name in ("graph.json", "metrics.json"):
        shutil.copy(MINIMAL_FIXTURE / name, scenario_dir / name)

    relevance = json.loads((MINIMAL_FIXTURE / "relevance.json").read_text(encoding="utf-8"))
    if include_b_zero:
        relevance["activities"].append(
            {
                "activity_id": "A-02",
                "activity_name": "Legacy compliance audit",
                "process_id": "P-99",
                "p": 0.0,
                "c": 0.0,
                "f": 0.0,
                "r": 0.0,
                "v": 1.0,
                "scores": [],
                "strategic_b_zero": True,
                "b_zero_reason": "No client value trace in fixture",
            }
        )
        relevance["matrix"].append(
            {"activity_id": "A-02", "metric_id": "M-01", "relevance": 0.99}
        )
        relevance["strategic_b_zero"] = [
            {
                "activity_id": "A-02",
                "activity_name": "Legacy compliance audit",
                "b_zero_reason": "No client value trace in fixture",
            }
        ]

    (scenario_dir / "relevance.json").write_text(
        json.dumps(relevance, indent=2), encoding="utf-8"
    )

    manifest = {
        "scenarios": [
            {
                "id": "minimal_demo",
                "title": "Minimal Demo",
                "description": "Tiny bundle for facade tests",
                "paths": {
                    "graph": "data/processed/demo/minimal_demo/graph.json",
                    "metrics": "data/processed/demo/minimal_demo/metrics.json",
                    "relevance": "data/processed/demo/minimal_demo/relevance.json",
                },
            }
        ]
    }
    configs_dir = root / "configs"
    configs_dir.mkdir()
    (configs_dir / "demo_scenarios.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )


def _write_oversized_matrix_repo(root: Path) -> None:
    """16 activities × one metric to assert matrix top-N cap (D8)."""
    scenario_dir = root / "data" / "processed" / "demo" / "minimal_demo"
    scenario_dir.mkdir(parents=True)
    shutil.copy(MINIMAL_FIXTURE / "graph.json", scenario_dir / "graph.json")
    shutil.copy(MINIMAL_FIXTURE / "metrics.json", scenario_dir / "metrics.json")

    activities = []
    matrix = []
    for i in range(16):
        aid = f"A-{i:02d}"
        activities.append(
            {
                "activity_id": aid,
                "activity_name": f"Activity {i}",
                "process_id": "P-01",
                "p": 0.1,
                "c": 0.1,
                "f": 0.1,
                "r": 0.1,
                "v": 0.1,
                "scores": [
                    {
                        "metric_id": "M-01",
                        "g": 0.0,
                        "j": 0.0,
                        "dv": 0.0,
                        "b": 0.0,
                        "relevance": float(i) / 100.0,
                        "pct_contribution": 0.0,
                    }
                ],
                "strategic_b_zero": False,
                "b_zero_reason": None,
            }
        )
        matrix.append(
            {"activity_id": aid, "metric_id": "M-01", "relevance": float(i) / 100.0}
        )

    relevance = {
        "scenario_id": "minimal_demo",
        "activities": activities,
        "matrix": matrix,
        "rankings_by_metric": {"M-01": [a["activity_id"] for a in activities]},
        "process_rollups": [],
        "strategic_b_zero": [],
    }
    (scenario_dir / "relevance.json").write_text(
        json.dumps(relevance, indent=2), encoding="utf-8"
    )

    manifest = {
        "scenarios": [
            {
                "id": "minimal_demo",
                "title": "Minimal Demo",
                "description": "Matrix cap fixture",
                "paths": {
                    "graph": "data/processed/demo/minimal_demo/graph.json",
                    "metrics": "data/processed/demo/minimal_demo/metrics.json",
                    "relevance": "data/processed/demo/minimal_demo/relevance.json",
                },
            }
        ]
    }
    (root / "configs").mkdir()
    (root / "configs" / "demo_scenarios.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )


class TestRunDemoScenario(unittest.TestCase):
    """demo-03-facade: run_demo_scenario → ScenarioViewModel (AC-1, FR-1–FR-6)."""

    @classmethod
    def setUpClass(cls):
        from optimizer.application.run_demo_scenario import run_demo_scenario
        from optimizer.application.scenario_models import ScenarioViewModel
        from optimizer.infrastructure.demo_loader import DemoScenarioNotFoundError

        cls.ScenarioViewModel = ScenarioViewModel
        cls.run_demo_scenario = staticmethod(run_demo_scenario)
        cls.DemoScenarioNotFoundError = DemoScenarioNotFoundError

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.repo_root = Path(self._tmpdir.name)

    def test_returns_scenario_view_model_for_minimal_scenario(self):
        _write_minimal_demo_repo(self.repo_root)

        vm = self.run_demo_scenario("minimal_demo", repo_root=self.repo_root)

        self.assertIsInstance(vm, self.ScenarioViewModel)
        self.assertEqual(vm.scenario.id, "minimal_demo")
        self.assertEqual(vm.scenario.title, "Minimal Demo")

    def test_graph_network_uses_demo_labels_and_groups(self):
        _write_minimal_demo_repo(self.repo_root)

        vm = self.run_demo_scenario("minimal_demo", repo_root=self.repo_root)

        self.assertIsInstance(vm.graph_network, Network)
        nodes = {node["id"]: node for node in vm.graph_network.nodes}
        self.assertEqual(nodes["M-01"]["label"], "On-Time Delivery")
        self.assertEqual(nodes["A-01"]["group"], "Activity")

    def test_metrics_list_matches_fixture(self):
        _write_minimal_demo_repo(self.repo_root)

        vm = self.run_demo_scenario("minimal_demo", repo_root=self.repo_root)

        self.assertEqual(len(vm.metrics), 1)
        metric = vm.metrics[0]
        self.assertEqual(metric.id, "M-01")
        self.assertEqual(metric.name, "On-Time Delivery")
        self.assertIn("definition", metric.__dict__)
        self.assertIn("client_need", metric.__dict__)

    def test_matrix_includes_scored_activity(self):
        _write_minimal_demo_repo(self.repo_root)

        vm = self.run_demo_scenario("minimal_demo", repo_root=self.repo_root)

        cells = [
            (row.activity_id, row.metric_id, row.relevance)
            for row in vm.matrix_rows
        ]
        self.assertIn(("A-01", "M-01", 0.2), cells)

    def test_matrix_excludes_strategic_b_zero_activity(self):
        _write_minimal_demo_repo(self.repo_root, include_b_zero=True)

        vm = self.run_demo_scenario("minimal_demo", repo_root=self.repo_root)

        activity_ids = {row.activity_id for row in vm.matrix_rows}
        self.assertIn("A-01", activity_ids)
        self.assertNotIn("A-02", activity_ids)

    def test_strategic_b_zero_list_populated(self):
        _write_minimal_demo_repo(self.repo_root, include_b_zero=True)

        vm = self.run_demo_scenario("minimal_demo", repo_root=self.repo_root)

        self.assertEqual(len(vm.strategic_b_zero), 1)
        entry = vm.strategic_b_zero[0]
        self.assertEqual(entry.activity_id, "A-02")
        self.assertIn("No client value trace", entry.b_zero_reason)

    def test_activities_available_for_sidebar_picker(self):
        _write_minimal_demo_repo(self.repo_root, include_b_zero=True)

        vm = self.run_demo_scenario("minimal_demo", repo_root=self.repo_root)

        picker_ids = {item.activity_id for item in vm.activities}
        self.assertIn("A-01", picker_ids)
        self.assertIn("A-02", picker_ids)
        a01 = next(item for item in vm.activities if item.activity_id == "A-01")
        self.assertEqual(a01.p, 0.5)
        self.assertEqual(a01.v, 0.5)

    def test_matrix_caps_at_top_n_per_metric(self):
        _write_oversized_matrix_repo(self.repo_root)

        vm = self.run_demo_scenario("minimal_demo", repo_root=self.repo_root)

        m01_rows = [row for row in vm.matrix_rows if row.metric_id == "M-01"]
        self.assertLessEqual(len(m01_rows), MATRIX_TOP_N)

    def test_unknown_scenario_raises(self):
        _write_minimal_demo_repo(self.repo_root)

        with self.assertRaises(self.DemoScenarioNotFoundError):
            self.run_demo_scenario("does_not_exist", repo_root=self.repo_root)

    def test_does_not_call_llm_extraction(self):
        _write_minimal_demo_repo(self.repo_root)

        with patch(
            "optimizer.graph_building.extraction.extract_graph_data"
        ) as mock_extract:
            self.run_demo_scenario("minimal_demo", repo_root=self.repo_root)

        mock_extract.assert_not_called()


if __name__ == "__main__":
    unittest.main()
