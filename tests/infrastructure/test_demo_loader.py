"""
Tests for demo-01-loader and demo-05-tests (loader portion).

Run from project root:
    python3 -m unittest tests.infrastructure.test_demo_loader -v
"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from optimizer.application.demo_models import DemoBundle, DemoScenario
from optimizer.infrastructure.demo_loader import (
    DemoFileMissingError,
    DemoScenarioNotFoundError,
    graph_json_to_graph_documents,
    load_demo_bundle,
    load_manifest,
    resolve_repo_root,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MINIMAL_FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "demo" / "minimal"


def _write_minimal_demo_repo(root: Path) -> None:
    """Lay out configs/ + data/processed/demo/minimal/ under root."""
    scenario_dir = root / "data" / "processed" / "demo" / "minimal_demo"
    scenario_dir.mkdir(parents=True)
    for name in ("graph.json", "metrics.json", "relevance.json"):
        shutil.copy(MINIMAL_FIXTURE / name, scenario_dir / name)

    manifest = {
        "scenarios": [
            {
                "id": "minimal_demo",
                "title": "Minimal Demo",
                "description": "Tiny bundle for loader tests",
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


class TestGraphJsonToGraphDocuments(unittest.TestCase):
    """demo-01-loader: graph.json → GraphDocument adapter (FR-7)."""

    def test_maps_nodes_and_relationships(self):
        graph = json.loads((MINIMAL_FIXTURE / "graph.json").read_text(encoding="utf-8"))

        docs = graph_json_to_graph_documents(graph)

        self.assertEqual(len(docs), 1)
        doc = docs[0]
        node_ids = {node.id for node in doc.nodes}
        self.assertEqual(node_ids, {"M-01", "A-01"})
        self.assertEqual(len(doc.relationships), 1)
        rel = doc.relationships[0]
        self.assertEqual(rel.source.id, "A-01")
        self.assertEqual(rel.target.id, "M-01")
        self.assertEqual(rel.type, "AFFECTS")

    def test_skips_relationships_with_unknown_endpoints(self):
        graph = json.loads((MINIMAL_FIXTURE / "graph.json").read_text(encoding="utf-8"))

        docs = graph_json_to_graph_documents(graph)

        rel_targets = {rel.target.id for rel in docs[0].relationships}
        self.assertNotIn("UNKNOWN-NODE", rel_targets)

    def test_node_properties_include_display_label(self):
        """Adapter stores fixture label in node.properties for PyVis (demo-02)."""
        graph = json.loads((MINIMAL_FIXTURE / "graph.json").read_text(encoding="utf-8"))

        docs = graph_json_to_graph_documents(graph)
        by_id = {node.id: node for node in docs[0].nodes}

        self.assertEqual(by_id["M-01"].properties.get("label"), "On-Time Delivery")
        self.assertEqual(by_id["A-01"].properties.get("label"), "Track daily rack prices")


class TestLoadManifestAndBundle(unittest.TestCase):
    """demo-01-loader: manifest resolution + bundle load (FR-7, FR-8)."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.repo_root = Path(self._tmpdir.name)
        _write_minimal_demo_repo(self.repo_root)

    def test_resolve_repo_root_finds_configs_parent(self):
        nested = self.repo_root / "src" / "optimizer"
        nested.mkdir(parents=True)

        found = resolve_repo_root(start=nested)

        self.assertEqual(found, self.repo_root)

    def test_load_manifest_returns_scenarios(self):
        scenarios = load_manifest(repo_root=self.repo_root)

        self.assertEqual(len(scenarios), 1)
        scenario = scenarios[0]
        self.assertIsInstance(scenario, DemoScenario)
        self.assertEqual(scenario.id, "minimal_demo")
        self.assertEqual(scenario.title, "Minimal Demo")
        self.assertIn("graph", scenario.paths)

    def test_load_demo_bundle_returns_typed_bundle(self):
        bundle = load_demo_bundle("minimal_demo", repo_root=self.repo_root)

        self.assertIsInstance(bundle, DemoBundle)
        self.assertEqual(bundle.scenario.id, "minimal_demo")
        self.assertIn("nodes", bundle.graph)
        self.assertIn("metrics", bundle.metrics)
        self.assertIn("activities", bundle.relevance)
        self.assertEqual(len(bundle.graph_documents), 1)
        self.assertGreater(len(bundle.graph_documents[0].nodes), 0)

    def test_load_demo_bundle_unknown_scenario_raises(self):
        with self.assertRaises(DemoScenarioNotFoundError):
            load_demo_bundle("does_not_exist", repo_root=self.repo_root)

    def test_load_demo_bundle_missing_file_raises(self):
        graph_path = (
            self.repo_root / "data" / "processed" / "demo" / "minimal_demo" / "graph.json"
        )
        graph_path.unlink()

        with self.assertRaises(DemoFileMissingError):
            load_demo_bundle("minimal_demo", repo_root=self.repo_root)


if __name__ == "__main__":
    unittest.main()
